from src.database import get_session
from src.library.repository import SqlBookRepository, IBookRepository
from src.library.service import BookService
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

async def get_book_repository(
    session: AsyncSession = Depends(get_session)
) -> IBookRepository:
    return SqlBookRepository(session)

async def get_book_service(
    repo: IBookRepository = Depends(get_book_repository)
) -> BookService:
    return BookService(repo)