class ISBNAlreadyExistsError(ValueError):
    """Исключение при попытке создать книгу с уже существующим ISBN."""
    def __init__(self, isbn: str):
        self.isbn = isbn
        super().__init__(f"Book with ISBN '{isbn}' already exists")

class BookNotFoundError(ValueError):
    """Исключение, выбрасываемое при попытке получить несуществующую книгу."""
    def __init__(self, book_id: str):
        self.book_id = book_id
        super().__init__(f"Book with ID '{book_id}' not found")

class InvalidBookDataError(ValueError):
    """Исключение, выбрасываемое при некорректных данных книги (например, при обновлении)."""
    def __init__(self, message: str):
        super().__init__(message)