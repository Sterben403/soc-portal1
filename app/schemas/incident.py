from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class IncidentBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "medium"

class IncidentCreate(IncidentBase):
    pass

class IncidentUpdate(BaseModel):
    status: str

class IncidentOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    client_id: int
    created_at: datetime
    first_response_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None

    class Config:
        orm_mode = True
