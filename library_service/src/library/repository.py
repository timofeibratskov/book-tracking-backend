from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exc, delete
from src.library.models import BookStatusModel 
from uuid import UUID
from src.library.exceptions import RepositoryError 

class ILibraryRepository(ABC):
    @abstractmethod
    async def create(self, book_status: BookStatusModel) -> BookStatusModel:
        ...

    @abstractmethod
    async def get_all(self,
                      skip: int = 0,
                      limit: int = 100,
                      is_available: Optional[bool] = None
                     ) -> List[BookStatusModel]:
        ...

    @abstractmethod
    async def get(self, book_id: UUID) -> BookStatusModel | None:
        """Получает статус книги по ID книги."""
        ...

    @abstractmethod
    async def update(self, book_status: BookStatusModel) -> BookStatusModel:
        ...

    @abstractmethod
    async def delete(self, book_id: UUID) -> int:
        """Удаляет статус книги по ID книги. Возвращает количество удаленных записей."""
        ...


class SqlLibraryRepository(ILibraryRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, book_status: BookStatusModel) -> BookStatusModel:
        """Создает новую запись о статусе книги в БД."""
        try:
            self._session.add(book_status)
            await self._session.commit()
            await self._session.refresh(book_status)
            return book_status
        except exc.SQLAlchemyError as e:
            await self._session.rollback()
            raise RepositoryError("Database operation failed during book status creation", original_error=e) from e


    async def get_all(self, skip: int = 0, limit: int = 100, is_available: Optional[bool] = None) -> List[BookStatusModel]:
        """Получает список статусов книг с пагинацией и фильтром по доступности."""
        try:
            query = select(BookStatusModel)
            if is_available is not None:
                query = query.where(BookStatusModel.is_available == is_available)
            query = query.offset(skip).limit(limit)
            result = await self._session.execute(query)
            return list(result.scalars().all())
        except exc.SQLAlchemyError as e:
             raise RepositoryError("Database operation failed while retrieving book statuses", original_error=e) from e


    async def get(self, book_id: UUID) -> BookStatusModel | None:
        """Получает статус книги по её ID."""
        try:
            result = await self._session.execute(
                select(BookStatusModel).where(BookStatusModel.book_id == book_id) # Используем book_id
            )
            return result.scalar_one_or_none()
        except exc.SQLAlchemyError as e:
            raise RepositoryError(f"Database operation failed while retrieving book status with ID {book_id}", original_error=e) from e


    async def update(self, book_status: BookStatusModel) -> BookStatusModel:
        """Обновляет существующую запись о статусе книги в БД."""
        try:
            self._session.add(book_status)
            await self._session.commit()
            await self._session.refresh(book_status)
            return book_status
        except exc.SQLAlchemyError as e:
            await self._session.rollback()
            raise RepositoryError(f"Database operation failed while updating book status with ID {book_status.book_id}", original_error=e) from e


    async def delete(self, book_id: UUID) -> int:
        """Удаляет запись о статусе книги по её ID. Возвращает количество удаленных."""
        try:
            stmt = delete(BookStatusModel).where(BookStatusModel.book_id == book_id) 
            result = await self._session.execute(stmt)
            await self._session.commit()
            deleted_count = result.rowcount
            return deleted_count 
        except exc.SQLAlchemyError as e:
            await self._session.rollback()
            raise RepositoryError(f"Database operation failed while deleting book status with ID {book_id}", original_error=e) from e