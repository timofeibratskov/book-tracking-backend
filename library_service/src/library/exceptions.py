from uuid import UUID
from typing import Optional


class BookStatusError(Exception):
    pass


class InvalidUUIDError(BookStatusError):
    def __init__(self, invalid_id: str):
        self.invalid_id = invalid_id
        super().__init__(f"Invalid UUID format: '{invalid_id}'")


class BookStatusNotFoundError(BookStatusError):
    def __init__(self, book_id: UUID): 
        self.book_id = book_id
        super().__init__(f"Book status with ID '{book_id}' not found")


class BookNotAvailableError(BookStatusError):
    def __init__(self, book_id: UUID):
        self.book_id = book_id
        super().__init__(f"Book with ID '{book_id}' is not available for borrowing.")


class BookNotBorrowedError(BookStatusError):
    def __init__(self, book_id: UUID):
        self.book_id = book_id
        super().__init__(f"Book with ID '{book_id}' was not borrowed.")


class RepositoryError(BookStatusError):
    def __init__(self, message: str = "Database operation failed", original_error: Optional[Exception] = None):
        self.original_error = original_error
        full_message = f"Repository error: {message}"
        if original_error:
             full_message += f" (Original error: {original_error})"
        super().__init__(full_message)


class ServiceError(BookStatusError):
    def __init__(self, message: str = "An unexpected service error occurred", original_error: Optional[Exception] = None):
        self.original_error = original_error
        full_message = f"Service error: {message}"
        if original_error:
             full_message += f" (Original error: {original_error})"
        super().__init__(full_message)