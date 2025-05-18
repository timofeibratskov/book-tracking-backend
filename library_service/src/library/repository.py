from abc import ABC, abstractmethod
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from src.library.models import BookStatusModel
from uuid import UUID
from typing import Optional

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
    async def get(self, id: UUID) -> BookStatusModel | None:
        ...
    
    @abstractmethod
    async def update(self, book_status: BookStatusModel) -> BookStatusModel:
        ...

    @abstractmethod
    async def delete(self, book_status: BookStatusModel) -> None:
        ...


class SqlBookRepository(ILibraryRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, book_status: BookStatusModel) -> BookStatusModel:
            self._session.add(book_status)
            await self._session.commit() 
            await self._session.refresh(book_status) 
            return book_status


    async def get_all(self, skip: int = 0, limit: int = 100, is_avaliable: Optional[bool] = None) -> List[BookStatusModel]:
            query = select(BookStatusModel)
            if is_avaliable is not None:
                query = query.where(BookStatusModel.is_available == is_avaliable)
            query = query.offset(skip).limit(limit)
            result = await self._session.execute(
                query)
            return list(result.scalars().all())


    async def get(self, id: UUID) -> BookStatusModel | None:
            result = await self._session.execute(
                select(BookStatusModel)
                .where(BookStatusModel.id==id))
            return result.scalar_one_or_none()
    

    async def update(self, book: BookStatusModel) -> BookStatusModel:
            self._session.add(book)
            await self._session.commit()
            await self._session.refresh(book)
            return book


    async def delete(self, book_status_id: UUID) -> int:
            stmt = delete(BookStatusModel).where(BookStatusModel.id == book_status_id)
            result = await self._session.execute(stmt)
            await self._session.commit()
            deleted_count = result.rowcount 
            return deleted_count 
