from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.db.database import SessionLocal
from app.models.ticket import Ticket, TicketCategory, TicketStatus
from app.models.ticket_message import TicketMessage
from app.schemas.ticket import TicketCreate, TicketOut, TicketMessageOut
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/tickets", tags=["tickets"])

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.post("/", response_model=TicketOut)
async def create_ticket(data: TicketCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role != "client":
        raise HTTPException(status_code=403, detail="Only clients can create tickets")

    ticket = Ticket(client_id=user.id, category=data.category, title=data.title)
    db.add(ticket)
    await db.flush()

    message = TicketMessage(
        ticket_id=ticket.id,
        sender_id=user.id,
        sender_role="client",
        message=data.message
    )
    db.add(message)
    await db.commit()
    await db.refresh(ticket)
    return ticket

@router.get("/", response_model=List[TicketOut])
async def get_tickets(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    query = select(Ticket)
    if user.role == "client":
        query = query.where(Ticket.client_id == user.id)

    result = await db.execute(query.order_by(Ticket.created_at.desc()))
    return result.scalars().all()

@router.get("/{ticket_id}/messages", response_model=List[TicketMessageOut])
async def get_ticket_messages(ticket_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if user.role == "client" and ticket.client_id != user.id:
        raise HTTPException(status_code=403, detail="Not your ticket")

    result = await db.execute(select(TicketMessage).where(TicketMessage.ticket_id == ticket_id).order_by(TicketMessage.created_at))
    return result.scalars().all()

@router.post("/{ticket_id}/reply", response_model=TicketMessageOut)
async def reply_ticket(ticket_id: int, message: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if user.role == "client" and ticket.client_id != user.id:
        raise HTTPException(status_code=403, detail="Not your ticket")

    msg = TicketMessage(
        ticket_id=ticket_id,
        sender_id=user.id,
        sender_role=user.role,
        message=message
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg