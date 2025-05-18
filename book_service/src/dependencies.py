from src.database import get_session
from src.books.repository import SqlBookRepository, IBookRepository
from src.books.service import BookService
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from src.rabbit.dependencies import get_rabbit_producer
from src.rabbit.producer import RabbitMQProducer


async def get_book_repository(
    session: AsyncSession = Depends(get_session)
) -> IBookRepository:
    return SqlBookRepository(session)

async def get_book_service(
    repo: IBookRepository = Depends(get_book_repository),
    producer: RabbitMQProducer = Depends(get_rabbit_producer)
) -> BookService:
    return BookService(repo, producer)