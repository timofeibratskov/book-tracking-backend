from typing import List, Optional, Dict, Any 
from uuid import UUID
from datetime import datetime
from src.library.models import BookStatusModel
from src.library.repository import ILibraryRepository 
from .schemas import BookStatus

class LibraryService:
    """Сервис для управления статусами книг в библиотеке."""
    def __init__(self, library_repo: ILibraryRepository):
        self._library_repo = library_repo

    async def create_book_status(self, book_id: UUID) -> BookStatus:
        """
        Создает новую запись о статусе книги (по умолчанию доступна).
        """
        book_status_model = BookStatusModel(
            book_id=book_id,
            borrowed_at=None,
            returned_at=None,
            is_available=True
        )
        saved_book_status = await self._library_repo.create(book_status_model)
        return BookStatus.model_validate(saved_book_status) 


    async def delete_book_status(self, book_id: UUID) -> int:
        """
        Удаляет запись о статусе книги по ID книги.
        Возвращает количество удаленных записей (0 или 1).
        """
        deleted_count = await self._library_repo.delete(book_id)
        return deleted_count


    async def borrow_book(self, book_id: UUID) -> Dict[str, Any]:
        """
        Помечает книгу как взятую.
        Возвращает статус операции и данные книги, если успешно.
        Не выбрасывает исключения при ошибках (не найдена, недоступна).
        """
        book_status = await self._library_repo.get(book_id)

        if not book_status:
            return {"success": False, "reason": "Book not found"}

        if not book_status.is_available:
            return {"success": False, "reason": "Book not available"}

        book_status.borrowed_at = datetime.now()
        book_status.returned_at = None 
        book_status.is_available = False

        updated_book_status = await self._library_repo.update(book_status)

        return {"success": True, "book_status": BookStatus.model_validate(updated_book_status)}


    async def return_book(self, book_id: UUID) -> Dict[str, Any]:
        """
        Помечает книгу как возвращенную.
        Возвращает статус операции и данные книги, если успешно.
        Не выбрасывает исключения при ошибках (не найдена, не была взята).
        """
        book_status = await self._library_repo.get(book_id)

        if not book_status:
            return {"success": False, "reason": "Book not found"}

        if book_status.is_available:
            return {"success": False, "reason": "Book was not borrowed"}

        book_status.borrowed_at = None
        book_status.returned_at = None
        book_status.is_available = True

        updated_book_status = await self._library_repo.update(book_status)

        return {"success": True, "book_status": BookStatus.model_validate(updated_book_status)}

    async def get_book_status(self, book_id: UUID) -> Optional[BookStatus]:
        """
        Получает статус книги по ID книги.
        Возвращает Pydantic модель BookStatus или None, если книга не найдена.
        """
        book_status_model = await self._library_repo.get(book_id)
        if book_status_model:
            return BookStatus.model_validate(book_status_model) 
        return None

    async def get_available_books(self) -> List[BookStatus]:
        """
        Получает список всех доступных книг.
        """
        available_books_models = await self._library_repo.get_all(is_available=True)
        return [BookStatus.model_validate(book) for book in available_books_models]