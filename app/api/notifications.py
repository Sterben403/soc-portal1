from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.database import SessionLocal
from app.schemas.notification import NotificationCreate, NotificationOut
from app.models.notification import Notification
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/notifications", tags=["notifications"])

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.post("/", response_model=NotificationOut)
async def create_notification(data: NotificationCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    notif = Notification(
        user_id=user.id,
        channel=data.channel,
        target=data.target,
        event=data.event
    )
    db.add(notif)
    await db.commit()
    await db.refresh(notif)
    return notif

@router.get("/", response_model=list[NotificationOut])
async def list_notifications(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(Notification).where(Notification.user_id == user.id))
    return result.scalars().all()