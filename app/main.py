from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.auth import admin_router
from app.api import roles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.requests import Request
import hmac
import hashlib
import secrets
from app.core.config import settings as _settings
import datetime


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        # Базовые безопасные заголовки
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
        # CSP: ослабляем для /docs|/redoc (Swagger/Redoc тянут ресурсы с CDN)
        path = request.url.path or ""
        is_docs = path.startswith("/docs") or path.startswith("/redoc")
        if (request.url.hostname in {"localhost", "127.0.0.1"}):
            script_src = "'self' 'unsafe-eval' 'unsafe-inline'" + (" https://cdn.jsdelivr.net" if is_docs else "")
            style_src = "'self' 'unsafe-inline'" + (" https://cdn.jsdelivr.net" if is_docs else "")
            csp = (
                "default-src 'self'; "
                "img-src 'self' data: blob: https:; "
                f"style-src {style_src}; "
                f"script-src {script_src}; "
                "connect-src 'self' http://localhost:8000 http://127.0.0.1:8000 http://localhost:8080 http://127.0.0.1:8080 http://localhost:5173 ws://localhost:5173; "
                "frame-ancestors 'none'"
            )
        else:
            script_src = "'self'" + (" https://cdn.jsdelivr.net" if is_docs else "")
            style_src = "'self' 'unsafe-inline'" + (" https://cdn.jsdelivr.net" if is_docs else "")
            csp = (
                "default-src 'self'; "
                "img-src 'self' data: https:; "
                f"style-src {style_src}; "
                f"script-src {script_src}; "
                "connect-src 'self'; "
                "frame-ancestors 'none'"
            )
        response.headers.setdefault("Content-Security-Policy", csp)
        return response


class CSRFMiddleware(BaseHTTPMiddleware):
    """Double Submit Cookie CSRF защита для cookie-потока.

    Требует заголовок X-CSRF-Token для небезопасных методов, если не используется Bearer.
    Токен = nonce, а подпись хранится в cookie: csrf_token = nonce.signature
    """

    COOKIE_NAME = "csrf_token"
    HEADER_NAME = "X-CSRF-Token"

    def _sign(self, nonce: str) -> str:
        sig = hmac.new(_settings.CSRF_SECRET.encode(), nonce.encode(), hashlib.sha256).hexdigest()
        return f"{nonce}.{sig}"

    def _verify(self, value: str, presented: str) -> bool:
        try:
            nonce, sig = value.split(".", 1)
        except ValueError:
            return False
        calc = hmac.new(_settings.CSRF_SECRET.encode(), nonce.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, calc):
            return False
        return hmac.compare_digest(nonce, presented)

    EXEMPT_PATHS = {"/auth/login", "/auth/register"}

    async def dispatch(self, request: Request, call_next):
        # Выдаём токен, если отсутствует, на безопасные методы
        csrf_cookie = request.cookies.get(self.COOKIE_NAME)
        if request.method in ("GET", "HEAD", "OPTIONS") and not csrf_cookie:
            nonce = secrets.token_urlsafe(32)
            csrf_cookie = self._sign(nonce)
            response: Response = await call_next(request)
            response.set_cookie(
                self.COOKIE_NAME,
                csrf_cookie,
                httponly=False,
                secure=_settings.COOKIE_SECURE,
                samesite=_settings.COOKIE_SAMESITE,
                path="/",
                max_age=60 * 60 * 24,
            )
            return response

        # Для небезопасных методов — проверка, если не Bearer
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            # Исключения (логин/регистрация)
            if request.url.path in self.EXEMPT_PATHS:
                return await call_next(request)
            auth = request.headers.get("Authorization", "")
            if not auth.lower().startswith("bearer "):
                presented = request.headers.get(self.HEADER_NAME)
                if not (csrf_cookie and presented and self._verify(csrf_cookie, presented)):
                    return Response("CSRF token missing or invalid", status_code=403)

        return await call_next(request)

app = FastAPI()
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CSRFMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://5.63.120.30:5173",   # если фронт крутится тут
        "http://5.63.120.30",        # если фронт статику отдаёт с 80 порта
    ],
    allow_credentials=True,  
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/attachments", StaticFiles(directory="attachments"), name="attachments")

from app.api import (
    auth, knowledge, protected, incidents,
    messages, attachments, tickets, notifications,
    report, slametrics
)
app.include_router(roles.router, prefix="/api")
app.include_router(auth.router, prefix="/auth")
app.include_router(admin_router)
app.include_router(knowledge.router)          
app.include_router(protected.router, prefix="/api")
app.include_router(incidents.router)           
app.include_router(messages.router)            
app.include_router(attachments.router, prefix="")      
app.include_router(tickets.router)              
app.include_router(notifications.router, prefix="/api")
app.include_router(report.router, prefix="/report")    
app.include_router(slametrics.router)        

from app.db.database import init_db
from app.jobs.scheduler import start_scheduler

@app.on_event("startup")
async def on_startup():
    await init_db()
    start_scheduler()

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker and load balancers."""
    return {"status": "healthy", "timestamp": datetime.datetime.utcnow().isoformat()}
