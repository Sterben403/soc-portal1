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

class IncidentOut(IncidentBase):
    id: int
    status: str
    created_at: datetime
    client_id: int

    class Config:
        orm_mode = True