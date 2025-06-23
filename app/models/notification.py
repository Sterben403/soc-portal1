from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.sql import func
from app.db.base import Base
import enum

class NotificationChannel(str, enum.Enum):
    email = "email"
    telegram = "telegram"
    webhook = "webhook"

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    channel = Column(Enum(NotificationChannel), nullable=False)
    target = Column(String, nullable=False)  # email address, telegram ID, URL
    event = Column(String, nullable=False)   # "incident_created", "ticket_reply", etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())