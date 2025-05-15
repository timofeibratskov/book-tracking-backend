from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from .schemas import Book, BookCreate
from .models import BookModel  
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from src.database import get_session

router = APIRouter(prefix="/api/books")

@router.post("/", response_model=Book, status_code=201)
async def create_book(book_in: BookCreate, session: AsyncSession = Depends(get_session)):
    try:
        db_book = BookModel(**book_in.dict())
        session.add(db_book)
        await session.commit()
        await session.refresh(db_book) 
        return Book.model_validate(db_book)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="ISBN must be unique")
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create book: {e}")

@router.get("/", response_model=List[Book])
async def list_books(skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(BookModel).offset(skip).limit(limit))
    books = result.scalars().all()
    return [Book.model_validate(book) for book in books]