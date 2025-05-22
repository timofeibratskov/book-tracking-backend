from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status, Response
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
    summary="Создать статус книги (только для администратора)",
    response_description="Созданный статус книги",
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
    summary="Удалить статус книги по ID (только для администратора)",
    response_description="Успешное удаление",
)
async def delete_book_status(
    book_id: UUID,
    token: RequestToken = Depends(require_admin),
    library_service: LibraryService = Depends(get_library_service)
):
    deleted_count = await library_service.delete_book_status(book_id)
    if deleted_count == 0:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book status with ID {book_id} not found"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/status/{book_id}",
    response_model=BookStatus,
    summary="Получить статус книги по ID",
    response_description="Статус книги",
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
    summary="Получить список доступных книг",
    response_description="Список доступных книг",
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
    response_description="Обновленный статус книги после взятия",
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
    response_description="Обновленный статус книги после возврата",
)
async def return_book(
    book_id: UUID,
    token: RequestToken = Depends(require_authenticated),
    library_service: LibraryService = Depends(get_library_service)
):
    return await library_service.return_book(book_id)
