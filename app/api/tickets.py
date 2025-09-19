from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.db.database import SessionLocal
from app.models.ticket import Ticket
from app.models.ticket_message import TicketMessage
from app.schemas.ticket import TicketCreate, TicketOut, TicketMessageOut, TicketWithMessages
from app.dependencies.auth import get_current_user, require_roles
from app.models.user import User
from sqlalchemy.orm import selectinload
from app.services.notify import send_notification_event

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


async def get_db():
    async with SessionLocal() as session:
        yield session


@router.post(
    "",
    response_model=TicketOut,
    dependencies=[Depends(require_roles("client"))],  # admin пройдёт
)
async def create_ticket(
    data: TicketCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ticket = Ticket(client_id=user.id, category=data.category, title=data.title)
    db.add(ticket)
    await db.flush()

    message = TicketMessage(
        ticket_id=ticket.id,
        sender_id=user.id,
        sender_role="client",
        message=data.message,
    )
    db.add(message)
    await db.commit()
    await db.refresh(ticket)

    await send_notification_event(
        "ticket_created",
        f"Новый тикет #{ticket.id}: {ticket.title}",
    )
    return ticket


@router.get(
    "",
    response_model=List[TicketOut],
    dependencies=[Depends(require_roles("client", "analyst", "manager"))],  # admin пройдёт
)
async def get_tickets(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = select(Ticket)
    if (user.role or "").lower() == "client":
        query = query.where(Ticket.client_id == user.id)

    result = await db.execute(query.order_by(Ticket.created_at.desc()))
    return result.scalars().all()


@router.get(
    "/{ticket_id}",
    response_model=TicketWithMessages,
    dependencies=[Depends(require_roles("client", "analyst", "manager"))],
)
async def get_ticket_with_messages(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Ticket)
        .where(Ticket.id == ticket_id)
        .options(selectinload(Ticket.messages))
    )
    ticket = result.scalars().first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if (user.role or "").lower() == "client" and ticket.client_id != user.id:
        raise HTTPException(status_code=403, detail="Not your ticket")

    return ticket


@router.get(
    "/{ticket_id}/messages",
    response_model=List[TicketMessageOut],
    dependencies=[Depends(require_roles("client", "analyst", "manager"))],
)
async def get_ticket_messages(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if (user.role or "").lower() == "client" and ticket.client_id != user.id:
        raise HTTPException(status_code=403, detail="Not your ticket")

    result = await db.execute(
        select(TicketMessage)
        .where(TicketMessage.ticket_id == ticket_id)
        .order_by(TicketMessage.created_at.asc())
    )
    return result.scalars().all()


@router.post(
    "/{ticket_id}/reply",
    response_model=TicketMessageOut,
    # менеджеру запрещаем писать -> не включаем в список ролей
    dependencies=[Depends(require_roles("client", "analyst"))],  # admin пройдёт
)
async def reply_ticket(
    ticket_id: int,
    message: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if (user.role or "").lower() == "client" and ticket.client_id != user.id:
        raise HTTPException(status_code=403, detail="Not your ticket")

    msg = TicketMessage(
        ticket_id=ticket_id,
        sender_id=user.id,
        sender_role=(user.role or "client"),
        message=message,
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)

    await send_notification_event(
        "ticket_replied",
        f"Новый ответ в тикете #{ticket_id}",
    )
    return msg
