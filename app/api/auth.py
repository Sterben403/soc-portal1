from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import pyotp
import httpx
import os
import re
from app.db.database import SessionLocal
from app.models.user import User
from app.schemas.user import (
    UserCreate, Token, MFASetupOut, MFAVerifyIn, MFAVerifyOut
)
from app.core.security import hash_password, create_access_token
from app.core.config import settings
from app.dependencies.auth import get_current_user
from sqlalchemy.exc import IntegrityError
from app.security.keycloak import require_roles, get_current_claims

router = APIRouter(tags=["auth"])

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

async def get_db():
    async with SessionLocal() as session:
        yield session

def _set_auth_cookie(response: Response, token: str):
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=60 * 60 * 24,
        path="/",
    )

@router.post("/register", response_model=Token)
async def register(
    user: UserCreate,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    # простая проверка e-mail
    if not EMAIL_RE.match(user.email or ""):
        raise HTTPException(status_code=400, detail="Invalid email")

    # username/email должны быть уникальными
    existing = await db.execute(
        select(User).where((User.email == user.email) | (User.username == user.username))
    )
    if existing.scalar():
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
        role="client",             # <— всегда client
    )
    db.add(new_user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="User already exists")

    await db.refresh(new_user)
    token = create_access_token({"sub": new_user.email})
    _set_auth_cookie(response, token)
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login")
async def login(payload: dict, response: Response):
    """
    Логин по e-mail/паролю через Keycloak (Direct Access Grants), поддержка OTP (totp).
    { "email": "...", "password": "...", "otp"?: "123456" }
    """
    email = (payload.get("email") or "").strip()
    password = payload.get("password") or ""
    otp = (payload.get("otp") or payload.get("totp") or payload.get("code") or "").strip()

    if not email or not password:
        raise HTTPException(status_code=400, detail="email/password required")
    if not EMAIL_RE.match(email):
        raise HTTPException(status_code=400, detail="Invalid email")

    # Если backend запущен ВНУТРИ docker-compose -> KC_BASE_URL=http://keycloak:8080
    # Если ЛОКАЛЬНО без докера -> KC_BASE_URL=http://localhost:8080
    KC_BASE = os.getenv("KC_BASE_URL", "http://keycloak:8080").rstrip("/")
    KC_REALM = os.getenv("KC_REALM", "soc-portal")
    KC_CLIENT_ID = os.getenv("KC_CLIENT_ID", "soc-portal")

    token_url = f"{KC_BASE}/realms/{KC_REALM}/protocol/openid-connect/token"
    data = {
        "grant_type": "password",
        "client_id": KC_CLIENT_ID,
        "username": email,
        "password": password,
        "scope": "openid profile email",
    }
    if otp:
        data["totp"] = otp

    try:
        async with httpx.AsyncClient(timeout=15.0) as c:
            r = await c.post(
                token_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Keycloak connection error: {e}")

    if r.status_code != 200:
        try:
            j = r.json()
            err = j.get("error")
            desc = j.get("error_description")
            detail = f"{err or ''}{': ' if err and desc else ''}{desc or ''}".strip() or j
        except Exception:
            detail = r.text or f"Keycloak error {r.status_code}"

        if isinstance(detail, str) and ("otp" in detail.lower() or "action" in detail.lower()):
            detail += " (если включён TOTP — введите код из приложения)"

        raise HTTPException(status_code=401, detail=detail)

    tok = r.json()
    return {"access_token": tok["access_token"], "token_type": "bearer"}

@router.get("/kc/me")
async def kc_me(claims: dict = Depends(get_current_claims)):
    return {
        "email": claims.get("email"),
        "roles": claims.get("realm_access", {}).get("roles", []),
        "sub": claims.get("sub"),
        "email_verified": claims.get("email_verified"),
    }

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        "access_token",
        path="/",
        samesite=settings.COOKIE_SAMESITE,
    )
    return {"message": "Logged out"}

@router.post("/mfa/setup", response_model=MFASetupOut)
async def mfa_setup(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    secret = pyotp.random_base32()
    user.totp_secret = secret
    db.merge(user)
    await db.commit()

    uri = pyotp.TOTP(secret).provisioning_uri(
        name=user.email,
        issuer_name="YourSOCPortal",
    )
    return {"otp_auth_url": uri}

@router.post("/mfa/verify", response_model=MFAVerifyOut)
async def mfa_verify(
    data: MFAVerifyIn,
    user: User = Depends(get_current_user),
):
    if not user.totp_secret:
        raise HTTPException(status_code=400, detail="MFA not set up")
    totp = pyotp.TOTP(user.totp_secret)
    valid = totp.verify(data.code)
    return {"success": bool(valid)}

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email, "role": current_user.role}

admin_router = APIRouter(prefix="/api/admin", tags=["admin"])

@admin_router.get("/ping", dependencies=[Depends(require_roles("manager"))])
def admin_ping():
    return {"ok": True}
