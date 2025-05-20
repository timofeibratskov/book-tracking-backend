from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from .models import UserModel
from uuid import UUID
from abc import ABC, abstractmethod


class IUserRepository(ABC):
    @abstractmethod
    async def create(self, user: UserModel) -> UserModel: ...
   
    @abstractmethod
    async def delete(self, user_id: UUID) -> None: ...
    
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> UserModel | None: ...
    
    @abstractmethod
    async def get_by_email(self, email: str) -> UserModel | None: ...

class SqlUserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: UserModel) -> UserModel:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user_id: UUID) -> None:
        result = await self.session.execute(
            delete(UserModel).where(UserModel.id == user_id)
            )
        await self.session.commit()
        return result.rowcount 

    async def get_by_id(self, user_id: UUID) -> UserModel | None:
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> UserModel | None:
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email))
        return result.scalar_one_or_none()