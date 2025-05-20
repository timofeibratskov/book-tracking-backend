from src.database import get_session
from src.users.repository import SqlUserRepository, IUserRepository
from src.users.service import UserService
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends


async def get_user_repository(
    session: AsyncSession = Depends(get_session)
) -> IUserRepository:
    return SqlUserRepository(session)

async def get_user_service(
    repo: IUserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(repo)