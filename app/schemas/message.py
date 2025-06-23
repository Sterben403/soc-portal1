from pydantic import BaseModel
from datetime import datetime

class MessageCreate(BaseModel):
    incident_id: int
    text: str

class MessageOut(BaseModel):
    id: int
    incident_id: int
    sender_id: int
    sender_role: str
    text: str
    created_at: datetime

    class Config:
        orm_mode = True