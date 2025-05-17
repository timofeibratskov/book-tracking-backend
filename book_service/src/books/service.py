from src.books.exceptions import (
    ISBNAlreadyExistsError,
    BookNotFoundError,
    RepositoryError,
    ServiceError)
from sqlalchemy.exc import IntegrityError
from src.books.repository import IBookRepository 
from src.books.schemas import Book, BookCreate, BookUpdate
from src.books.models import BookModel
from uuid import UUID
from typing import Optional


class BookService:
    def __init__(self, repo: IBookRepository):
        self._repo = repo 


    async def create_book(self, book_data: BookCreate) -> Book:
        try:
            db_book = BookModel(**book_data.model_dump())
            created_book = await self._repo.create(db_book) 
            return Book.model_validate(created_book)
        except RepositoryError as e:
            original_sqla_error = e.original_error
            if isinstance(original_sqla_error, IntegrityError):
                error_string = str(original_sqla_error).lower()
                if "isbn" in error_string or "unique constraint" in error_string:
                    raise ISBNAlreadyExistsError(book_data.isbn) from original_sqla_error 
                else:
                    raise ServiceError("Unexpected database integrity violation", original_error=e) from e 
            raise ServiceError(f"Repository error: {e}", original_error=e) from e 
        except Exception as e:
            raise ServiceError("An unexpected error occurred during book creation", original_error=e) from e


    async def list_books(self,
                        skip: int = 0,
                        limit: int = 100,
                        language: Optional[str] = None,
                        author: Optional[str] = None
                        ) -> list[Book]:
        try:
            db_books = await self._repo.get_all(skip=skip,
                                                limit=limit,
                                                language=language,
                                                author=author
                                                )
            return [Book.model_validate(db_book) for db_book in db_books]
        except RepositoryError as e:
            raise ServiceError(f"Repository error during listing books: {e}", original_error=e) from e
        except Exception as e:
            raise ServiceError("An unexpected error occurred while listing books", original_error=e) from e


    async def get_book(self, id: UUID) -> Book:
        try:
            db_book = await self._repo.get(id)
            if not db_book:
                raise BookNotFoundError(str(id)) 
            return Book.model_validate(db_book)
        except RepositoryError as e:
            raise ServiceError(f"Repository error during getting book with ID {id}: {e}", original_error=e) from e
        except BookNotFoundError:
            raise
        except Exception as e:
            raise ServiceError(f"An unexpected error occurred while getting book with ID {id}", original_error=e) from e


    async def update_book(self, book_id: UUID, update_data: BookUpdate) -> Book:
        try:
            book = await self._repo.get(book_id) 
            if not book:
                 raise BookNotFoundError(str(book_id))
            update_dict = update_data.model_dump(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(book, field, value)
            updated_book_model = await self._repo.update(book) 
            return Book.model_validate(updated_book_model)
        except BookNotFoundError:
            raise 
        except RepositoryError as e: 
            original_sqla_error = e.original_error
            if isinstance(original_sqla_error, IntegrityError):
                error_string = str(original_sqla_error).lower()
                if "isbn" in error_string or "unique constraint" in error_string:
                    raise ISBNAlreadyExistsError(update_data.isbn) from original_sqla_error 
                else:
                    raise ServiceError("Unexpected database integrity violation", original_error=e) from e 
            raise ServiceError(f"Repository error: {e}", original_error=e) from e 
        except Exception as e:
             raise ServiceError("An unexpected error occurred during book update", original_error=e) from e


    async def delete_book(self, book_id: UUID) -> None:
        try:
            deleted_count = await self._repo.delete(book_id)
            if deleted_count == 0:
                raise BookNotFoundError(book_id)
        except RepositoryError as e:
            raise ServiceError(f"Repository error during getting book with ID {id}: {e}", original_error=e) from e
        except BookNotFoundError:
            raise
        except Exception as e:
            raise ServiceError(f"An unexpected error occurred while getting book with ID {id}", original_error=e) from e

