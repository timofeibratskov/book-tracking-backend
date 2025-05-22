from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status, Response, HTTPException
from src.library.schemas import BookStatus, BookStatusCreate
from src.library.service import LibraryService
from src.dependencies import get_library_service
from authx import RequestToken
from src.auth.permissions import require_admin, require_authenticated

router = APIRouter(
    prefix="/library",
    tags=["library"],
)


@router.post(
    "",
    response_model=BookStatus,
    status_code=status.HTTP_201_CREATED,
    summary="Создать статус книги",
    description="Создает новый статус для книги. Доступно только для администратора.",
    response_description="Созданный статус книги",
    responses={
        201: {"description": "Статус книги успешно создан"},
        401: {"description": "Необходима авторизация"},
        403: {"description": "Нет прав администратора"},
        422: {"description": "Ошибка валидации входных данных"},
    }
)
async def create_book_status(
    book_status_create: BookStatusCreate,
    token: RequestToken = Depends(require_admin),
    library_service: LibraryService = Depends(get_library_service)
):
    return await library_service.create_book_status(book_status_create.book_id)


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить статус книги",
    description="Удаляет статус книги по ID. Только для администратора.",
    response_description="Статус книги успешно удален",
    responses={
        204: {"description": "Удалено успешно"},
        401: {"description": "Необходима авторизация"},
        403: {"description": "Нет прав администратора"},
        404: {"description": "Статус книги не найден"},
    }
)
async def delete_book_status(
    book_id: UUID,
    token: RequestToken = Depends(require_admin),
    library_service: LibraryService = Depends(get_library_service)
):
    deleted_count = await library_service.delete_book_status(book_id)
    if deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book status with ID {book_id} not found"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/status/{book_id}",
    response_model=BookStatus,
    summary="Получить статус книги",
    description="Возвращает текущий статус книги по ее ID.",
    response_description="Статус книги",
    responses={
        200: {"description": "Статус книги найден"},
        401: {"description": "Необходима авторизация"},
        404: {"description": "Статус не найден"},
    }
)
async def get_book_status(
    book_id: UUID,
    token: RequestToken = Depends(require_authenticated),
    library_service: LibraryService = Depends(get_library_service)
):
    return await library_service.get_book_status(book_id)


@router.get(
    "/available",
    response_model=List[BookStatus],
    summary="Список доступных книг",
    description="Возвращает список всех доступных к выдаче книг.",
    response_description="Список доступных книг",
    responses={
        200: {"description": "Список доступных книг"},
        401: {"description": "Необходима авторизация"},
    }
)
async def get_available_books(
    token: RequestToken = Depends(require_authenticated),
    library_service: LibraryService = Depends(get_library_service)
):
    return await library_service.get_available_books()


@router.post(
    "/{book_id}/borrow",
    response_model=BookStatus,
    summary="Взять книгу",
    description="Помечает книгу как выданную пользователю.",
    response_description="Книга успешно выдана",
    responses={
        200: {"description": "Книга успешно взята"},
        400: {"description": "Книга недоступна"},
        401: {"description": "Необходима авторизация"},
        404: {"description": "Книга не найдена"},
    }
)
async def borrow_book(
    book_id: UUID,
    token: RequestToken = Depends(require_authenticated),
    library_service: LibraryService = Depends(get_library_service)
):
    return await library_service.borrow_book(book_id)


@router.post(
    "/{book_id}/return",
    response_model=BookStatus,
    summary="Вернуть книгу",
    description="Помечает книгу как возвращённую пользователем.",
    response_description="Книга успешно возвращена",
    responses={
        200: {"description": "Книга возвращена"},
        400: {"description": "Книга не была выдана"},
        401: {"description": "Необходима авторизация"},
        404: {"description": "Книга не найдена"},
    }
)
async def return_book(
    book_id: UUID,
    token: RequestToken = Depends(require_authenticated),
    library_service: LibraryService = Depends(get_library_service)
):
    return await library_service.return_book(book_id)
