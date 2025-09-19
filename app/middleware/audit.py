from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.db.database import SessionLocal
from app.models.audit_log import AuditLog
from sqlalchemy.future import select
from app.models.user import User
import datetime
from jose import jwt as _jose_jwt
from app.core.config import settings as _settings

class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        user = None
        try:
            # Пытаемся восстановить пользователя из cookie-токена (локальная сессия)
            cookie_token = request.cookies.get("access_token")
            if cookie_token:
                payload = _jose_jwt.decode(cookie_token, _settings.SECRET_KEY, algorithms=[_settings.ALGORITHM])
                email = payload.get("sub")
                if email:
                    async with SessionLocal() as db:
                        res = await db.execute(select(User).where(User.email == email))
                        user = res.scalar_one_or_none()
        except Exception:
            user = None

        response = await call_next(request)

        # Логируем только значимые методы
        if request.method in ("POST", "PUT", "DELETE", "PATCH"):
            async with SessionLocal() as db:
                log = AuditLog(
                    user_id=getattr(user, "id", None),
                    path=str(request.url.path),
                    method=request.method,
                    status_code=response.status_code,
                    timestamp=datetime.datetime.utcnow(),
                    user_agent=request.headers.get("user-agent"),
                    ip=request.client.host if request.client else None,
                    error=None,
                )
                db.add(log)
                await db.commit()
        return response
