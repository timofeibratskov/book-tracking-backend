from abc import ABC, abstractmethod
from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exc
from src.books.models import BookModel

class BookRepositoryInterface(ABC):
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[BookModel]:
        raise NotImplementedError
        
    @abstractmethod
    async def create(self, book: BookModel) -> BookModel:
        raise NotImplementedError

class AsyncSqlAlchemyBookRepository(BookRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[BookModel]:
        result = await self.session.execute(
            select(BookModel).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, book: BookModel) -> BookModel:
        self.session.add(book)
        await self.session.commit()
        await self.session.refresh(book)
        return book