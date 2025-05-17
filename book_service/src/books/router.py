from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID
from src.books.schemas import Book, BookCreate, BookUpdate
from src.books.service import BookService
from src.books.exceptions import (
    BookNotFoundError,
    ISBNAlreadyExistsError,
    ServiceError 
)
from typing import Optional
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
            status_code=status.HTTP_409_CONFLICT, 
            detail=str(e) 
        ) from e
    
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during book creation"
        ) from e


@router.get("/", response_model=list[Book])
async def list_books(
    skip: int = Query(0, ge=0), 
    limit: int = Query(100, ge=1, le=100), 
    language: Optional[str] = Query(None, description="Filter books by language"), 
    author: Optional[str] = Query(None, description="Filter books by author"),
    service: BookService = Depends(get_book_service)
):
    try:
        return await service.list_books(
            skip=skip,
            limit=limit,
            language=language,
            author=author            
            )
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while listing books"
        ) from e


@router.get("/{book_id}", response_model=Book)
async def get_book(
    book_id: UUID,
    service: BookService = Depends(get_book_service)
):
    try:
        return await service.get_book(book_id)
    except BookNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e) 
        ) from e
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while getting book"
        ) from e


@router.patch("/{book_id}", response_model=Book)
async def update_book(
    book_id: UUID,
    update_data: BookUpdate,
    service: BookService = Depends(get_book_service)
):
    try:
        return await service.update_book(book_id, update_data)
    except BookNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        ) from e
    except ISBNAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=str(e)
        ) from e
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during book update." 
        ) from e
    
@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: UUID,
    service: BookService = Depends(get_book_service)
):
    try:
        return await service.delete_book(book_id)
    except BookNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e) 
        ) from e
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while deletion book"
        ) from e