from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Response
from src.library.schemas import BookStatus, BookStatusCreate
from src.library.service import LibraryService
from src.dependencies import get_library_service
from src.library.exceptions import (
    BookStatusNotFoundError,
    BookNotAvailableError,
    BookNotBorrowedError,
    ServiceError 
)

router = APIRouter(
    prefix="/library",
    tags=["library"],
)


@router.post(
    "",
    response_model=BookStatus,
    status_code=status.HTTP_201_CREATED,
    summary="Создать статус книги",
    response_description="Созданный статус книги",
)
async def create_book_status(
    book_status_create: BookStatusCreate,
    library_service: LibraryService = Depends(get_library_service)
):
    """
    Создает новую запись о статусе книги. Принимает только ID книги.
    Начальный статус: доступна, даты выдачи/возврата: None.
    Обрабатывает ошибки сервиса.
    """
    try:
        book_id = book_status_create.book_id
        created_book_status = await library_service.create_book_status(book_id)
        return created_book_status
    except ServiceError as e:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Service error during creation: {e}")
    except Exception as e:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred during creation: {e}")


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить статус книги по ID",
    response_description="Успешное удаление",
)
async def delete_book_status(
    book_id: UUID,
    library_service: LibraryService = Depends(get_library_service)
):
    """
    Удаляет запись о статусе книги по её уникальному идентификатору.
    Возвращает 404, если статус книги не найден.
    Обрабатывает ошибки сервиса.
    """
    try:
        deleted_count = await library_service.delete_book_status(book_id)

        if deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book status with ID {book_id} not found"
            )

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except ServiceError as e:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Service error during deletion: {e}")
    except Exception as e:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred during deletion: {e}")


@router.get(
    "/status/{book_id}",
    response_model=BookStatus,
    summary="Получить статус книги по ID",
    response_description="Статус книги",
)
async def get_book_status(
    book_id: UUID,
    library_service: LibraryService = Depends(get_library_service)
):
    """
    Получает статус книги по её уникальному идентификатору.
    Обрабатывает исключения бизнес-логики и сервиса.
    """
    try:
        book_status = await library_service.get_book_status(book_id)
        return book_status
    except BookStatusNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ServiceError as e:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Service error: {e}")
    except Exception as e:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")


@router.get(
    "/available",
    response_model=List[BookStatus],
    summary="Получить список доступных книг",
    response_description="Список доступных книг",
)
async def get_available_books(
    library_service: LibraryService = Depends(get_library_service)
):
    """
    Получает список всех книг, которые доступны для выдачи.
    Обрабатывает ошибки сервиса.
    """
    try:
        available_books = await library_service.get_available_books()
        return available_books
    except ServiceError as e:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Service error: {e}")
    except Exception as e:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")


@router.post(
    "/{book_id}/borrow",
    response_model=BookStatus,
    summary="Взять книгу",
    response_description="Обновленный статус книги после взятия",
)
async def borrow_book(
    book_id: UUID,
    library_service: LibraryService = Depends(get_library_service)
):
    """
    Отмечает книгу как взятую. Обрабатывает исключения бизнес-логики и сервиса.
    """
    try:
        updated_book_status = await library_service.borrow_book(book_id)
        return updated_book_status

    except BookStatusNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BookNotAvailableError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ServiceError as e:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Service error: {e}")
    except Exception as e:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")


# Эндпоинт: Вернуть книгу
@router.post(
    "/{book_id}/return",
    response_model=BookStatus,
    summary="Вернуть книгу",
    response_description="Обновленный статус книги после возврата",
)
async def return_book(
    book_id: UUID,
    library_service: LibraryService = Depends(get_library_service)
):
    """
    Отмечает книгу как возвращенную. Обрабатывает исключения бизнес-логики и сервиса.
    """
    try:
        updated_book_status = await library_service.return_book(book_id)
        return updated_book_status

    except BookStatusNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BookNotBorrowedError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ServiceError as e:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Service error: {e}")
    except Exception as e:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")