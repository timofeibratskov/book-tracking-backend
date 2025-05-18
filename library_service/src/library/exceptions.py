from uuid import UUID
from typing import Optional

class BookError(Exception):
    pass

class InvalidUUIDError(BookError):
    def __init__(self, invalid_id: str):
        self.invalid_id = invalid_id
        super().__init__(f"Invalid UUID format: '{invalid_id}'")

class ISBNAlreadyExistsError(BookError):
    def __init__(self, isbn: str):
        self.isbn = isbn
        super().__init__(f"Book with ISBN '{isbn}' already exists")

class BookNotFoundError(BookError):
    def __init__(self, book_id: str):
        self.book_id = book_id
        super().__init__(f"Book with ID '{book_id}' not found")


class ConcurrentUpdateError(BookError):
    def __init__(self, book_id: UUID):
        self.book_id = book_id
        super().__init__(f"Concurrent modification detected for book {book_id}")


class RepositoryError(BookError):
    def __init__(self, message: str = "Database operation failed", original_error: Optional[Exception] = None):
        self.original_error = original_error
        super().__init__(f"Repository error: {message}")


class ServiceError(BookError):
    def __init__(self, message: str = "An unexpected service error occurred", original_error: Optional[Exception] = None):
        self.original_error = original_error
        super().__init__(f"Service error: {message}")
