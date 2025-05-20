from pydantic import BaseModel, EmailStr
from uuid import UUID
class UserRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"