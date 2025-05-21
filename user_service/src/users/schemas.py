from pydantic import BaseModel, EmailStr
from uuid import UUID
from enum import Enum

class UserRole(str, Enum):
    user = "user"
    admin = "admin"

class UserRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    role: UserRole   

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
