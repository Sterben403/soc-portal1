from pydantic import BaseModel
from datetime import datetime

class AttachmentOut(BaseModel):
    id: int
    message_id: int
    file_path: str
    file_name: str
    uploaded_at: datetime

    class Config:
        orm_mode = True