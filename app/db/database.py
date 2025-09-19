import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/soc_portal"
)
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set!")

engine = create_async_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session

async def init_db():
    # ⚠️ ВАЖНО: «засветить» модели перед create_all,
    # но делать импорт ЛОКАЛЬНО, чтобы не вызывать циклы при старте
    from app.models import user  # noqa: F401
    from app.models import role_request  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)