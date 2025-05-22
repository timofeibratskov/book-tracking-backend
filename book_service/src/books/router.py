from fastapi import APIRouter, Depends, status, Query
from uuid import UUID
from typing import Optional

from src.books.schemas import Book, BookCreate, BookUpdate
from src.books.service import BookService
from src.dependencies import get_book_service
from src.auth import security
from authx import RequestToken, TokenPayload

router = APIRouter(prefix="/books", tags=["books"])


def require_admin(payload: TokenPayload = Depends(security.access_token_required)):
    if "admin" not in getattr(payload, "role", []):
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return payload


def require_authenticated(token: RequestToken = Depends(security.access_token_required)):
    return token


@router.post("/", response_model=Book, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: BookCreate,
    token: RequestToken = Depends(require_admin),
    service: BookService = Depends(get_book_service)
):
    return await service.create_book(book_data)


@router.get("/", response_model=list[Book])
async def list_books(
    token: RequestToken = Depends(require_authenticated),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    language: Optional[str] = Query(None, description="Filter books by language"),
    author: Optional[str] = Query(None, description="Filter books by author"),
    service: BookService = Depends(get_book_service)
):
    return await service.list_books(
        skip=skip,
        limit=limit,
        language=language,
        author=author
    )


@router.get("/{book_id}", response_model=Book)
async def get_book(
    book_id: UUID,
    token: RequestToken = Depends(require_authenticated),
    service: BookService = Depends(get_book_service)
):
    return await service.get_book(book_id)


@router.patch("/{book_id}", response_model=Book)
async def update_book(
    book_id: UUID,
    update_data: BookUpdate,
    token: RequestToken = Depends(require_admin),
    service: BookService = Depends(get_book_service)
):
    return await service.update_book(book_id, update_data)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: UUID,
    token: RequestToken = Depends(require_admin),
    service: BookService = Depends(get_book_service)
):
    await service.delete_book(book_id)
