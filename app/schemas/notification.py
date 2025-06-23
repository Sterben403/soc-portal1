from pydantic import BaseModel
from enum import Enum
from datetime import datetime

class NotificationChannel(str, Enum):
    email = "email"
    telegram = "telegram"
    webhook = "webhook"

class NotificationCreate(BaseModel):
    channel: NotificationChannel
    target: str
    event: str

class NotificationOut(BaseModel):
    id: int
    user_id: int
    channel: NotificationChannel
    target: str
    event: str
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True