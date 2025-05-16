from fastapi import APIRouter, Depends, HTTPException, status
from src.books.schemas import Book, BookCreate
from src.books.service import BookService
from src.books.exceptions import ISBNAlreadyExistsError
from src.dependencies import get_book_service

router = APIRouter(prefix="/books", tags=["books"])

@router.post("/", response_model=Book, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: BookCreate,
    service: BookService = Depends(get_book_service)
):
    try:
        return await service.create_book(book_data)
    except ISBNAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=list[Book])
async def list_books(
    skip: int = 0,
    limit: int = 100,
    service: BookService = Depends(get_book_service)
):
    return await service.list_books(skip=skip, limit=limit)