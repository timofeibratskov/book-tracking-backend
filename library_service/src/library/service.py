from typing import List
from uuid import UUID
from datetime import datetime
from src.library.models import BookStatusModel
from src.library.repository import ILibraryRepository
from src.library.schemas import BookStatus
from .exceptions import (
    BookStatusNotFoundError,
    BookNotAvailableError,
    BookNotBorrowedError,
    RepositoryError, 
    ServiceError
)

class LibraryService:
    def __init__(self, library_repo: ILibraryRepository):
        self._library_repo = library_repo


    async def create_book_status(self, book_id: UUID) -> BookStatus:
        try:
            book_status_model = BookStatusModel(
                book_id=book_id,
                borrowed_at=None,
                returned_at=None,
                is_available=True
            )
            saved_book_status = await self._library_repo.create(book_status_model)
            return BookStatus.model_validate(saved_book_status)
        except RepositoryError as e:
            raise ServiceError(f"Database operation failed during creation for ID {book_id}", original_error=e) from e
        except Exception as e:
            raise ServiceError(f"An unexpected error occurred during creation for ID {book_id}", original_error=e) from e


    async def delete_book_status(self, book_id: UUID) -> int:
        try:
            deleted_count = await self._library_repo.delete(book_id)
            return deleted_count
        except RepositoryError as e:
             raise ServiceError(f"Database operation failed during deletion for ID {book_id}", original_error=e) from e
        except Exception as e:
             raise ServiceError(f"An unexpected error occurred during deletion for ID {book_id}", original_error=e) from e


    async def borrow_book(self, book_id: UUID) -> BookStatus:
        try:
            book_status = await self._library_repo.get(book_id)

            if not book_status:
                raise BookStatusNotFoundError(book_id)

            if not book_status.is_available:
                raise BookNotAvailableError(book_id)

            book_status.borrowed_at = datetime.now()
            book_status.returned_at = None 
            book_status.is_available = False

            updated_book_status = await self._library_repo.update(book_status)

            return BookStatus.model_validate(updated_book_status)

        except BookStatusNotFoundError: 
             raise
        except BookNotAvailableError: 
             raise
        except RepositoryError as e:
            raise ServiceError(f"Database operation failed while borrowing book with ID {book_id}", original_error=e) from e
        except Exception as e:
            raise ServiceError(f"An unexpected error occurred while borrowing book with ID {book_id}", original_error=e) from e


    async def return_book(self, book_id: UUID) -> BookStatus:
        try:
            book_status = await self._library_repo.get(book_id)

            if not book_status:
                raise BookStatusNotFoundError(book_id)

            if book_status.is_available:
                raise BookNotBorrowedError(book_id)

            book_status.borrowed_at = None
            book_status.returned_at = None
            book_status.is_available = True

            updated_book_status = await self._library_repo.update(book_status)

            return BookStatus.model_validate(updated_book_status)

        except BookStatusNotFoundError: 
             raise
        except BookNotBorrowedError: 
             raise
        except RepositoryError as e:
             raise ServiceError(f"Database operation failed while returning book with ID {book_id}", original_error=e) from e
        except Exception as e:
             raise ServiceError(f"An unexpected error occurred while returning book with ID {book_id}", original_error=e) from e


    async def get_book_status(self, book_id: UUID) -> BookStatus:
        try:
            book_status_model = await self._library_repo.get(book_id)
            if book_status_model is None:
                raise BookStatusNotFoundError(book_id)

            return BookStatus.model_validate(book_status_model)

        except BookStatusNotFoundError: 
             raise
        except RepositoryError as e:
             raise ServiceError(f"Database operation failed while getting status for ID {book_id}", original_error=e) from e
        except Exception as e:
             raise ServiceError(f"An unexpected error occurred while getting status for ID {book_id}", original_error=e) from e


    async def get_available_books(self) -> List[BookStatus]:
        try:
            available_books_models = await self._library_repo.get_all(is_available=True)
            return [BookStatus.model_validate(book) for book in available_books_models]
        except RepositoryError as e:
             raise ServiceError(f"Database operation failed while getting available books", original_error=e) from e
        except Exception as e:
             raise ServiceError(f"An unexpected error occurred while getting available books", original_error=e) from e