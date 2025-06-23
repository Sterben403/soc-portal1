from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.database import SessionLocal
from app.models.message import Message
from app.models.incident import Incident
from app.schemas.message import MessageCreate, MessageOut
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/messages", tags=["messages"])

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.post("/", response_model=MessageOut)
async def send_message(data: MessageCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(Incident).where(Incident.id == data.incident_id))
    incident = result.scalar()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if user.role == "client" and incident.client_id != user.id:
        raise HTTPException(status_code=403, detail="Not your incident")

    message = Message(
        incident_id=data.incident_id,
        text=data.text,
        sender_id=user.id,
        sender_role=user.role
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message

@router.get("/{incident_id}", response_model=list[MessageOut])
async def get_messages(incident_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if user.role == "client" and incident.client_id != user.id:
        raise HTTPException(status_code=403, detail="Not your incident")

    result = await db.execute(select(Message).where(Message.incident_id == incident_id).order_by(Message.created_at))
    return result.scalars().all()