from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

# Чтобы не было ворнинга Pydantic v2:
# вместо Config.orm_mode = True -> model_config = ConfigDict(from_attributes=True)

class MessageOut(BaseModel):
    id: int
    incident_id: int
    sender_id: int
    sender_role: str
    # фронт ждёт "message", а в БД поле "text" — маппим в ручную в эндпоинте
    message: str
    created_at: datetime
    attachment: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
