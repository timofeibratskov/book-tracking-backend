from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc
from typing import List
from src.books.schemas import Book, BookCreate
from src.books.models import BookModel
from src.database import get_session
from src.books.repository import AsyncSqlAlchemyBookRepository, BookRepositoryInterface

async def get_book_repository(
    session: AsyncSession = Depends(get_session)
) -> BookRepositoryInterface:
    return AsyncSqlAlchemyBookRepository(session)

router = APIRouter(prefix="/books", tags=["books"])

@router.post("/", response_model=Book, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_in: BookCreate,
    repo: BookRepositoryInterface = Depends(get_book_repository)
):
    try:
        db_book = BookModel(**book_in.model_dump())
        created_book = await repo.create(db_book)
        return Book.model_validate(created_book)
    except exc.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book with this ISBN already exists"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create book: {str(e)}"
        )

@router.get("/", response_model=List[Book])
async def list_books(
    skip: int = 0,
    limit: int = 100,
    repo: BookRepositoryInterface = Depends(get_book_repository)
):
    try:
        db_books = await repo.get_all(skip=skip, limit=limit)
        return [Book.model_validate(db_book) for db_book in db_books]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch books: {str(e)}"
        )