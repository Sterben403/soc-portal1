from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from typing import List

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

class TicketOut(BaseModel):
    id: int
    client_id: int
    category: TicketCategory
    title: str
    status: TicketStatus
    created_at: datetime

    class Config:
        orm_mode = True

class TicketMessageOut(BaseModel):
    id: int
    ticket_id: int
    sender_id: int
    sender_role: str
    message: str
    created_at: datetime

    class Config:
        orm_mode = True