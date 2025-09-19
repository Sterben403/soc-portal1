from pydantic import BaseModel, EmailStr

class MFASetupOut(BaseModel):
    otp_auth_url: str

class MFAVerifyIn(BaseModel):
    code: str  

class MFAVerifyOut(BaseModel):
    success: bool
    
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    mfa_code: str | None = None
class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"