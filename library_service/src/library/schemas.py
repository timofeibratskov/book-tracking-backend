from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime 
from typing import Optional

class BookStatusCreate(BaseModel):
    """Схема Pydantic для создания нового статуса книги."""
    book_id: UUID = Field(..., description="Уникальный ID книги")


class BookStatus(BaseModel):
    """Схема Pydantic для представления статуса книги (для чтения/ответа)."""
    book_id: UUID = Field(..., description="Уникальный ID книги")
    borrowed_at: Optional[datetime] = Field(None, description="Время выдачи книги")
    returned_at: Optional[datetime] = Field(None, description="Время возврата книги")
    is_available: bool = Field(..., description="Доступна ли книга")

    class Config:
        from_attributes = True 