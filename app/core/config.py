from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    # Crypto / JWT (для локальной cookie-сессии — не Keycloak)
    SECRET_KEY: str = "dev-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 день

    # Cookies для локальной аутентификации (если используешь)
    # На проде: COOKIE_SECURE=True и COOKIE_SAMESITE="None" (если фронт на другом домене)
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "Lax"  # В проде установить "None"

    # CORS — фронт на Vite 5173 + локальные варианты
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # Доп. секреты (если нужны)
    CSRF_SECRET: str = "dev-csrf"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

settings = Settings()
