from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from app.db.base import Base

DATABASE_URL = os.getenv("SYNC_DB_URL") or "postgresql+psycopg2://postgres:postgres@db:5432/soc_portal"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)