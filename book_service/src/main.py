from contextlib import asynccontextmanager 
from fastapi import FastAPI
from src.books.router import router as books_router 
from src.config import settings
from src.rabbit.producer import AsyncioRabbitMQProducer 
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Приложение стартует (lifespan)...")
    try:
        producer_instance = AsyncioRabbitMQProducer(settings.RABBITMQ_URL)
        await producer_instance.connect()
        app.state.rabbitmq_producer = producer_instance
        logger.info("RabbitMQ Producer успешно подключен и сохранен в app.state.")
    except Exception as e:
        logger.error(f"Ошибка при старте RabbitMQ Producer: {e}", exc_info=True)
    yield
    logger.info("Приложение завершает работу (lifespan)...")

    producer_instance = getattr(app.state, 'rabbitmq_producer', None)
    if isinstance(producer_instance, AsyncioRabbitMQProducer):
        try:
            await producer_instance.disconnect()
            logger.info("RabbitMQ Producer отключен.")
        except Exception as e:
             logger.error(f"Ошибка при отключении RabbitMQ Producer: {e}", exc_info=True)
    else:
        logger.warning("RabbitMQ Producer не найден в app.state при завершении.")




app = FastAPI(lifespan=lifespan) 

app.include_router(books_router)