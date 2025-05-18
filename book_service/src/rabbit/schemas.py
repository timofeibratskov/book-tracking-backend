from pydantic import BaseModel
from uuid import UUID

class BookEvent(BaseModel):
    book_id: UUID
    action: str  


    class Config:
        json_encoders = {
            UUID: lambda v: str(v)
        }