from sqlalchemy import exc
from src.books.repository import IBookRepository
from src.books.schemas import Book, BookCreate
from src.books.models import BookModel
from src.books.exceptions import ISBNAlreadyExistsError

class BookService:
    def __init__(self, repo: IBookRepository):
        self._repo = repo

    async def create_book(self, book_data: BookCreate) -> Book:
        try:
            db_book = BookModel(**book_data.model_dump())
            created_book = await self._repo.create(db_book)
            return Book.model_validate(created_book)
        except exc.IntegrityError as e:
            if "isbn" in str(e).lower():
                raise ISBNAlreadyExistsError(book_data.isbn)
            raise

    async def list_books(self, skip: int = 0, limit: int = 100) -> list[Book]:
        db_books = await self._repo.get_all(skip=skip, limit=limit)
        return [Book.model_validate(db_book) for db_book in db_books]