from pydantic import BaseModel, Field

class RoleRequestCreate(BaseModel):
    role: str = Field(pattern="^(analyst|manager)$")

class RoleRequestOut(BaseModel):
    id: int
    user_id: int
    requested_role: str
    status: str
    comment: str | None = None

    class Config:
        orm_mode = True
