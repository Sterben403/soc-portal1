from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os
from app.db.base import Base
from typing import AsyncGenerator
DATABASE_URL = os.getenv("SYNC_DB_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/soc_portal")

if DATABASE_URL is None:
    raise RuntimeError("DATABASE_URL is not set!")

engine = create_async_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)