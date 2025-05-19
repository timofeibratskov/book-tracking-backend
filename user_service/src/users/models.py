from sqlalchemy import Column, UUID, String, Enum
import uuid
from enum import Enum as PyEnum
from src.database import Base

class UserRole(str, PyEnum):
    USER = "user"
    ADMIN = "admin"

class UserModel(Base):
    __tablename__ = "users"  

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)  
    password = Column(String(255), nullable=False)  
    role = Column(Enum(UserRole), nullable=False, default=UserRole.USER)  
    
    
    def __repr__(self):
        return f"<User {self.email}, role={self.role}>"