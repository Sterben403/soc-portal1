# app/dependencies/auth.py
from __future__ import annotations

import re
from typing import Optional, Iterable

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyHeader
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.db.database import SessionLocal
from app.models.user import User
from app.security.keycloak import get_current_claims, get_roles

bearer_scheme = APIKeyHeader(name="Authorization", auto_error=False)

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


# ---------- DB session ----------
async def get_db():
    async with SessionLocal() as session:
        yield session


# ---------- helpers ----------
def _normalize_roles(roles: Iterable[str] | None) -> set[str]:
    """soc_admin / ROLE_ADMIN -> admin, и т.п."""
    if not roles:
        return set()
    return {
        r.replace("ROLE_", "").replace("soc_", "").lower()
        for r in roles
    }


def pick_role(kc_roles: Iterable[str] | None) -> str:
    """
    Выбираем «самую сильную» роль из Keycloak.
    Приоритет: admin > manager > analyst > client
    """
    norm = _normalize_roles(kc_roles)
    if "admin" in norm:
        return "admin"
    if "manager" in norm:
        return "manager"
    if "analyst" in norm:
        return "analyst"
    return "client"


async def _generate_unique_username(db: AsyncSession, base: str) -> str:
    """
    Делаем уникальный username на основе base.
    base нормализуем (латиница, цифры, . _ -), длина ограничена.
    """
    base = re.sub(r"[^a-zA-Z0-9._-]", "_", base).strip("._-") or "user"
    base = base[:30]

    candidate = base
    idx = 0
    while True:
        res = await db.execute(select(User).where(User.username == candidate))
        if res.scalar_one_or_none() is None:
            return candidate
        idx += 1
        candidate = f"{base}{idx}"[:40]


# ---------- main ----------
async def get_current_user(
    request: Request,
    authorization: Optional[str] = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    1) Если пришёл Bearer: валидируем KC-токен, создаём пользователя при необходимости,
       username делаем уникальным, роль синхронизируем с KC.
    2) Иначе — локальная cookie-сессия.
    """

    # --- 1) Keycloak Bearer поток ---
    if authorization and authorization.lower().startswith("bearer "):
        try:
            claims = get_current_claims(authorization)  # 401, если токен невалиден
            email = claims.get("email")
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Email claim missing in token",
                )

            # username формируем на основе email, а не preferred_username (чтобы не словить 'admin' -> конфликт)
            email_local = email.split("@", 1)[0]
            kc_roles = get_roles(claims)
            effective_role = pick_role(kc_roles)

            # Ищем по email — это «ключ» для одного и того же человека
            res = await db.execute(select(User).where(User.email == email))
            user: Optional[User] = res.scalar_one_or_none()

            if not user:
                # подбираем уникальный username
                username = await _generate_unique_username(db, email_local)
                user = User(
                    email=email,
                    username=username,
                    role=effective_role or "client",
                    hashed_password="",  # для KC пароль не храним
                )
                db.add(user)
                await db.commit()
                await db.refresh(user)
            else:
                # синхронизируем роль из KC -> БД
                if effective_role and user.role != effective_role:
                    user.role = effective_role
                    db.add(user)
                    await db.commit()
                    await db.refresh(user)

            return user

        except HTTPException:
            # Переходим к cookie-потоку
            ...

    # --- 2) Локальный cookie-поток ---
    cookie_token = request.cookies.get("access_token")
    if not cookie_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        payload = jwt.decode(cookie_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: Optional[str] = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid cookie token (no sub)",
            )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token decode error: {e}",
        )

    res = await db.execute(select(User).where(User.email == email))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


def require_roles(*allowed_roles: str):
    allowed = {r.lower() for r in allowed_roles}

    async def checker(
        request: Request,
        user: User = Depends(get_current_user),
        authorization: Optional[str] = Depends(bearer_scheme),
    ) -> User:
        # Если админ — доступ везде
        if (user.role or "").lower() == "admin":
            return user

        # Проверяем KC-токен
        if authorization and authorization.lower().startswith("bearer "):
            try:
                claims = get_current_claims(authorization)
                kc = _normalize_roles(get_roles(claims))
                if kc & allowed:
                    return user
            except HTTPException:
                pass

        # Проверяем локальную роль
        if (user.role or "").lower() in allowed:
            return user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Allowed roles: {', '.join(sorted(allowed))}",
        )

    return checker