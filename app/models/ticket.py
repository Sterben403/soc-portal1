from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from app.db.database import Base
import enum

class TicketStatus(str, enum.Enum):
    open = "Открыт"
    waiting = "В ожидании"
    closed = "Закрыт"

class TicketCategory(str, enum.Enum):
    question = "Вопрос"
    bug = "Ошибка"
    incident = "Инцидент"
    source_request = "Запрос на источник"

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(Enum(TicketCategory), nullable=False)
    title = Column(String, nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.open)
    created_at = Column(DateTime(timezone=True), server_default=func.now())