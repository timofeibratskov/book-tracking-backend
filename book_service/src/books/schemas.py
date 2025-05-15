from enum import Enum
from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from typing import Optional

class Language(str, Enum):
    EN = "en"
    RU = "ru"
    FR = "fr"

class Genre(str, Enum):
    FICTION = "fiction"
    NON_FICTION = "non_fiction"
    SCIENCE = "science"

class BookBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    author: str = Field(min_length=2, max_length=50)
    isbn: str = Field(min_length=10, max_length=13)
    description: Optional[str] = Field(None, max_length=500)
    language: Language = Field(..., description="Book language")
    genre: Genre = Field(..., description="Book genre")

    @field_validator('isbn')
    def validate_isbn(cls, v):
        if not v.isdigit():
            raise ValueError("ISBN must contain only digits")
        if len(v) not in (10, 13):
            raise ValueError("ISBN must be 10 or 13 digits")
        return v

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    author: Optional[str] = Field(None, min_length=2, max_length=50)
    isbn: Optional[str] = Field(None, min_length=10, max_length=13)
    description: Optional[str] = Field(None, max_length=500)
    language: Optional[Language] = None
    genre: Optional[Genre] = None

class Book(BookBase):
    id: UUID

    class Config:
        from_attributes = True