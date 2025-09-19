import os
from datetime import datetime, timedelta

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import SessionLocal
from app.models.ticket import Ticket, TicketStatus
from app.models.ticket_message import TicketMessage
from app.services.notify import send_notification_event

async def check_ticket_sla():
    """Проверка тикетов без ответа аналитика в SLA_TICKET_FIRST_HOURS."""
    # Сколько часов ждать реакции аналитика
    hours = int(os.getenv("TICKET_SLA_FIRST_HOURS", "24"))
    cutoff = datetime.utcnow() - timedelta(hours=hours)

    async with SessionLocal() as db:  
        # Ищем тикеты, созданные до cutoff, всё ещё открытые
        stmt = select(Ticket).where(
            Ticket.created_at < cutoff,
            Ticket.status == TicketStatus.open  # статус "open"
        )
        tickets = (await db.execute(stmt)).scalars().all()

        for ticket in tickets:
            # Проверяем, был ли хоть один ответ аналитика
            msg_stmt = select(TicketMessage).where(
                TicketMessage.ticket_id == ticket.id,
                TicketMessage.sender_role == "analyst"
            ).order_by(TicketMessage.created_at)
            first_analyst = (await db.execute(msg_stmt)).scalars().first()

            if not first_analyst:
                # Шлём всем подписанным напоминание о SLA-нарушении
                await send_notification_event(
                    "ticket_sla_breach",
                    f"Ticket #{ticket.id} не получил ответа аналитика в течение {hours} ч."
                )
