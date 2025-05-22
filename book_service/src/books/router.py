from fastapi import APIRouter, Depends, status, Query, HTTPException
from uuid import UUID
from typing import Optional

from src.books.schemas import Book, BookCreate, BookUpdate
from src.books.service import BookService
from src.dependencies import get_book_service
from authx import RequestToken
from src.auth.permissions import require_admin, require_authenticated

router = APIRouter(prefix="/books", tags=["books"])


@router.post(
    "/",
    response_model=Book,
    status_code=status.HTTP_201_CREATED,
    summary="Создать книгу",
    description="Добавляет новую книгу в систему. Требуются права администратора.",
    response_description="Созданная книга",
    responses={
        201: {"description": "Книга успешно создана"},
        401: {"description": "Необходима авторизация"},
        403: {"description": "Нет прав администратора"},
        422: {"description": "Ошибка валидации входных данных"},
    }
)
async def create_book(
    book_data: BookCreate,
    token: RequestToken = Depends(require_admin),
    service: BookService = Depends(get_book_service)
):
    return await service.create_book(book_data)


@router.get(
    "/",
    response_model=list[Book],
    summary="Список книг",
    description="Получить список всех книг. Поддерживается фильтрация по языку и автору.",
    response_description="Список книг",
    responses={
        200: {"description": "Список книг получен"},
        401: {"description": "Необходима авторизация"},
    }
)
async def list_books(
    token: RequestToken = Depends(require_authenticated),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    language: Optional[str] = Query(None, description="Фильтрация по языку"),
    author: Optional[str] = Query(None, description="Фильтрация по автору"),
    service: BookService = Depends(get_book_service)
):
    return await service.list_books(
        skip=skip,
        limit=limit,
        language=language,
        author=author
    )


@router.get(
    "/{book_id}",
    response_model=Book,
    summary="Получить книгу по ID",
    description="Возвращает книгу по указанному ID.",
    response_description="Информация о книге",
    responses={
        200: {"description": "Книга найдена"},
        401: {"description": "Необходима авторизация"},
        404: {"description": "Книга не найдена"},
    }
)
async def get_book(
    book_id: UUID,
    token: RequestToken = Depends(require_authenticated),
    service: BookService = Depends(get_book_service)
):
    return await service.get_book(book_id)


@router.patch(
    "/{book_id}",
    response_model=Book,
    summary="Обновить книгу",
    description="Обновляет информацию о книге по ID. Требуются права администратора.",
    response_description="Обновлённая книга",
    responses={
        200: {"description": "Книга успешно обновлена"},
        401: {"description": "Необходима авторизация"},
        403: {"description": "Нет прав администратора"},
        404: {"description": "Книга не найдена"},
        422: {"description": "Ошибка валидации входных данных"},
    }
)
async def update_book(
    book_id: UUID,
    update_data: BookUpdate,
    token: RequestToken = Depends(require_admin),
    service: BookService = Depends(get_book_service)
):
    return await service.update_book(book_id, update_data)


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить книгу",
    description="Удаляет книгу по ID. Только для администратора.",
    response_description="Книга удалена",
    responses={
        204: {"description": "Книга успешно удалена"},
        401: {"description": "Необходима авторизация"},
        403: {"description": "Нет прав администратора"},
        404: {"description": "Книга не найдена"},
    }
)
async def delete_book(
    book_id: UUID,
    token: RequestToken = Depends(require_admin),
    service: BookService = Depends(get_book_service)
):
    await service.delete_book(book_id)
