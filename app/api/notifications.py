from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, desc

from app.db.database import SessionLocal
from app.schemas.notification import NotificationCreate, NotificationOut
from app.models.notification import Notification, NotificationChannel
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/notifications", tags=["notifications"])

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.post("", response_model=NotificationOut)
async def create_notification(
    data: NotificationCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    notif = Notification(
        user_id=user.id,
        channel=data.channel,
        target=data.target,
        event=data.event,
    )
    db.add(notif)
    await db.commit()
    await db.refresh(notif)
    return notif

@router.get("", response_model=list[NotificationOut])
async def list_notifications(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == user.id)
        .order_by(desc(Notification.created_at))
    )
    return result.scalars().all()

@router.get("/latest", response_model=list[NotificationOut])
async def latest_notifications(
    limit: int = 5,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()

@router.get("/summary", response_model=dict)
async def get_notification_summary(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Возвращаем булевы флаги, как ждёт фронт:
    { "email": true/false, "telegram": true/false, "webhook": true/false }
    Флаг = есть ли активная подписка на канал.
    """
    result = await db.execute(
        select(
            Notification.channel,
            func.count(Notification.id)
        ).where(
            Notification.user_id == user.id,
            Notification.is_active == True
        ).group_by(Notification.channel)
    )
    counts = {row[0].value if isinstance(row[0], NotificationChannel) else row[0]: row[1] for row in result.all()}

    summary = {
        "email": (counts.get("email", 0) > 0),
        "telegram": (counts.get("telegram", 0) > 0),
        "webhook": (counts.get("webhook", 0) > 0),
    }
    return summary
