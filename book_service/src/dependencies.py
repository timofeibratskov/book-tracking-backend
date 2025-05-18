from src.database import get_session
from src.books.repository import SqlBookRepository, IBookRepository
from src.books.service import BookService
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from src.rabbit.dependencies import get_rabbitmq_producer
from src.rabbit.producer import AsyncioRabbitMQProducer


async def get_book_repository(
    session: AsyncSession = Depends(get_session)
) -> IBookRepository:
    return SqlBookRepository(session)

async def get_book_service(
    repo: IBookRepository = Depends(get_book_repository),
    producer: AsyncioRabbitMQProducer = Depends(get_rabbitmq_producer)
) -> BookService:
    return BookService(repo, producer)