from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class KnowledgeArticleBase(BaseModel):
    title: str
    category: Optional[str] = None
    content: str

class KnowledgeArticleCreate(KnowledgeArticleBase):
    pass

class KnowledgeArticleUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    content: Optional[str] = None

class KnowledgeArticleOut(KnowledgeArticleBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    # pydantic v2
    model_config = ConfigDict(from_attributes=True)
