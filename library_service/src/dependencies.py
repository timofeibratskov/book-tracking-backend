from src.database import get_session
from src.library.repository import SqlLibraryRepository, ILibraryRepository
from src.library.service import LibraryService
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

async def get_library_repository(
    session: AsyncSession = Depends(get_session)
) -> ILibraryRepository:
    return SqlLibraryRepository(session)

async def get_library_service(
    repo: ILibraryRepository = Depends(get_library_repository)
) -> LibraryService:
    return LibraryService(repo)