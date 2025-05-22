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
from src.auth import security
from authx import RequestToken,TokenPayload


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
    """
    Создает новую книгу в системе.

    **Параметры запроса:**
    - Не принимаются (используется тело запроса).

    **Тело запроса:**
    - `book_data`: Объект с данными для новой книги (согласно схеме BookCreate).

    **Успешный ответ:**
    - **201 Created**: Книга успешно создана. Возвращает объект созданной книги (согласно схеме Book).

    **Возможные ошибки:**
    - **409 Conflict**: Книга с таким ISBN уже существует.
    - **422 Unprocessable Entity**: Неверный формат данных в теле запроса (обрабатывается FastAPI автоматически по схеме BookCreate).
    - **500 Internal Server Error**: Произошла внутренняя ошибка на сервере во время создания книги (например, ошибка БД).
    """
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
    token: RequestToken = Depends(require_authenticated),
    skip: int = Query(0, ge=0), 
    limit: int = Query(100, ge=1, le=100), 
    language: Optional[str] = Query(None, description="Filter books by language"), 
    author: Optional[str] = Query(None, description="Filter books by author"),
    service: BookService = Depends(get_book_service)
):
    """
    Получает список всех книг с возможностью фильтрации по языку или автору, с пагинацией.

    **Параметры запроса:**
    - `skip`: Пагинация, количество пропускаемых книг.
    - `limit`: Пагинация, максимальное количество книг в ответе.
    - `language`: Необязательный фильтр по языку книги.
    - `author`: Необязательный фильтр по автору книги.

    **Успешный ответ:**
    - **200 OK**: Возвращает список объектов Книга (согласно схеме List[Book]).

    **Возможные ошибки:**
    - **422 Unprocessable Entity**: Неверный формат параметров запроса skip или limit (обрабатывается FastAPI автоматически).
    - **500 Internal Server Error**: Произошла внутренняя ошибка на сервере во время получения списка.
    """
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
    token: RequestToken = Depends(require_authenticated),
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
    token: RequestToken = Depends(require_admin),
    service: BookService = Depends(get_book_service)
):
    """
    Получает список всех книг с возможностью фильтрации по языку или автору, с пагинацией.

    **Параметры запроса:**
    - `skip`: Пагинация, количество пропускаемых книг.
    - `limit`: Пагинация, максимальное количество книг в ответе.
    - `language`: Необязательный фильтр по языку книги.
    - `author`: Необязательный фильтр по автору книги.

    **Успешный ответ:**
    - **200 OK**: Возвращает список объектов Книга (согласно схеме List[Book]).

    **Возможные ошибки:**
    - **422 Unprocessable Entity**: Неверный формат параметров запроса skip или limit (обрабатывается FastAPI автоматически).
    - **500 Internal Server Error**: Произошла внутренняя ошибка на сервере во время получения списка.
    """
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
    token: RequestToken = Depends(require_admin),
    service: BookService = Depends(get_book_service)
):
    """
    Получает информацию об одной книге по ее уникальному идентификатору (ID).

    **Параметры пути:**
    - `book_id`: Уникальный идентификатор книги (в формате UUID).

    **Параметры запроса:**
    - Не принимаются.

    **Успешный ответ:**
    - **200 OK**: Возвращает объект Книга (согласно схеме Book).

    **Возможные ошибки:**
    - **404 Not Found**: Книга с указанным ID не найдена.
    - **422 Unprocessable Entity**: Неверный формат book_id в пути (обрабатывается FastAPI автоматически).
    - **500 Internal Server Error**: Произошла внутренняя ошибка на сервере.
    """
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