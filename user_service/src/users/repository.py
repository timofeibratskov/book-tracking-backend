from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, exc
from uuid import UUID
from src.users.models import UserModel
from src.users.exceptions import UserNotFoundError, EmailAlreadyExistsError, RepositoryError


class IUserRepository(ABC):
    @abstractmethod
    async def create(self, user: UserModel) -> UserModel: ...
   
    @abstractmethod
    async def delete(self, user_id: UUID) -> int: ...
    
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[UserModel]: ...
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[UserModel]: ...


class SqlUserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, user: UserModel) -> UserModel:
        try:
            self._session.add(user)
            await self._session.commit()
            await self._session.refresh(user)
            return user
        except exc.IntegrityError as e:
            await self._session.rollback()
            raise EmailAlreadyExistsError(user.email) from e
        except exc.SQLAlchemyError as e:
            await self._session.rollback()
            raise RepositoryError("Database error during user creation", original_error=e) from e

    async def delete(self, user_id: UUID) -> int:
        try:
            stmt = delete(UserModel).where(UserModel.id == user_id)
            result = await self._session.execute(stmt)
            await self._session.commit()            
            return result.rowcount
        except exc.SQLAlchemyError as e:
            await self._session.rollback()
            raise RepositoryError(f"Database error during deleting user with ID {user_id}", original_error=e) from e

    async def get_by_id(self, user_id: UUID) -> Optional[UserModel]:
        try:
            result = await self._session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            user = result.scalar_one_or_none()
            if user is None:
                raise UserNotFoundError(str(user_id))
            return user
        except exc.SQLAlchemyError as e:
            raise RepositoryError(f"Database error during getting user by ID {user_id}", original_error=e) from e

    async def get_by_email(self, email: str) -> Optional[UserModel]:
        try:
            result = await self._session.execute(
                select(UserModel).where(UserModel.email == email)
            )
            return result.scalar_one_or_none()
        except exc.SQLAlchemyError as e:
            raise RepositoryError(f"Database error during getting user by email {email}", original_error=e) from e