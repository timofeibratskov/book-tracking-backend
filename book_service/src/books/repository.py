from abc import ABC, abstractmethod
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exc, delete
from src.books.models import BookModel
from uuid import UUID
from src.books.exceptions import RepositoryError
from typing import Optional
class IBookRepository(ABC):
    @abstractmethod
    async def create(self, book: BookModel) -> BookModel:
        ...

    @abstractmethod
    async def get_all(self,
                      skip: int = 0,
                      limit: int = 100,
                      language: Optional[str] = None,
                      author: Optional[str] = None
                    ) -> List[BookModel]:
        ...

    @abstractmethod
    async def get(self, id: UUID) -> BookModel | None:
        ...
    
    @abstractmethod
    async def update(self, book: BookModel) -> BookModel:
        ...

    @abstractmethod
    async def delete(self, book: BookModel) -> None:
        ...


class SqlBookRepository(IBookRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, book: BookModel) -> BookModel:
        try:
            self._session.add(book)
            await self._session.commit() 
            await self._session.refresh(book) 
            return book
        except exc.SQLAlchemyError as e:
            await self._session.rollback() 
            raise RepositoryError("Database operation failed during book creation", original_error=e) from e


    async def get_all(self, skip: int = 0, limit: int = 100,language: Optional[str] = None, author: Optional[str] = None) -> List[BookModel]:
        try:
            query = select(BookModel)
            if language is not None:
                query = query.where(BookModel.language == language)
            if author is not None:
                query = query.where(BookModel.author == author)
            query = query.offset(skip).limit(limit)
            result = await self._session.execute(
                query)
            return list(result.scalars().all())
        except exc.SQLAlchemyError as e:
            raise RepositoryError("Database operation failed while retrieving books", original_error=e) from e


    async def get(self, id: UUID) -> BookModel | None:
        try:
            result = await self._session.execute(
                select(BookModel)
                .where(BookModel.id==id))
            return result.scalar_one_or_none()
        except exc.SQLAlchemyError as e:
            raise RepositoryError(f"Database operation failed while retrieving book with ID {id}", original_error=e) from e
    

    async def update(self, book: BookModel) -> BookModel:
        try:
            self._session.add(book)
            await self._session.commit()
            await self._session.refresh(book)
            return book
        except exc.SQLAlchemyError as e:
            await self._session.rollback()
            raise RepositoryError(f"Database operation failed while updating book with ID {book.id}", original_error=e) from e


    async def delete(self, book_id: UUID) -> int:
        try:
            stmt = delete(BookModel).where(BookModel.id == book_id)
            result = await self._session.execute(stmt)
            await self._session.commit()
            deleted_count = result.rowcount 
            return deleted_count 
        except exc.SQLAlchemyError as e: 
            await self._session.rollback()
            raise RepositoryError(f"Database operation failed while deleting book with ID {book_id}", original_error=e) from e
