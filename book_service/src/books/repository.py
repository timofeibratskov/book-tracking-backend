from abc import ABC, abstractmethod
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.books.models import BookModel


class IBookRepository(ABC):
    @abstractmethod
    async def create(self, book: BookModel) -> BookModel: ...
    
    @abstractmethod
    async def get_all(self, skip: int, limit: int) -> List[BookModel]: ...


class SqlBookRepository(IBookRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, book: BookModel) -> BookModel:
        self._session.add(book)
        await self._session.commit()
        await self._session.refresh(book)
        return book

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[BookModel]:
        result = await self._session.execute(
            select(BookModel).offset(skip).limit(limit))
        return list(result.scalars().all())