from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class TicketCategory(str, Enum):
    question = "Вопрос"
    bug = "Ошибка"
    incident = "Инцидент"
    source_request = "Запрос на источник"


class TicketStatus(str, Enum):
    open = "Открыт"
    waiting = "В ожидании"
    closed = "Закрыт"


class TicketCreate(BaseModel):
    category: TicketCategory
    title: str
    message: str


class TicketMessageOut(BaseModel):
    id: int
    ticket_id: int
    sender_id: int
    sender_role: str
    message: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TicketOut(BaseModel):
    id: int
    client_id: int
    category: TicketCategory
    title: str
    status: TicketStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TicketWithMessages(TicketOut):
    messages: List[TicketMessageOut]
