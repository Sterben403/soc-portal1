import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from app.db.base import Base
from sqlalchemy.orm import relationship

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
    category = Column(SQLEnum(TicketCategory), nullable=False)
    title = Column(String, nullable=False)
    status = Column(SQLEnum(TicketStatus), default=TicketStatus.open)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    messages = relationship("TicketMessage", back_populates="ticket", cascade="all, delete-orphan")
