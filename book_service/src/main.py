from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging
from src.config import settings
from src.rabbit.producer import RabbitMQProducer
from src.books.router import router as books_router

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    producer = RabbitMQProducer(settings.RABBITMQ_URL)
    try:
        await producer.connect()
        app.state.rabbitmq_producer = producer
        logger.info("RabbitMQ producer connected successfully")
    except Exception as e:
        logger.error(f"Failed to connect RabbitMQ: {str(e)}")
        raise

    yield
    
    if hasattr(app.state, 'rabbitmq_producer'):
        try:
            await producer.disconnect()
            logger.info("RabbitMQ producer disconnected")
        except Exception as e:
            logger.error(f"Error disconnecting RabbitMQ: {str(e)}")

app = FastAPI(lifespan=lifespan)
app.include_router(books_router)