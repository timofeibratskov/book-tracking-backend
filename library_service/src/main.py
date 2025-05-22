from contextlib import asynccontextmanager
from fastapi import FastAPI
import asyncio
from src.rabbit.consumer import RabbitMQConsumer
from src.library.message_listeners import handle_book_event
from src.config import settings
import logging
from src.library.router import router
from src.openapi_config import configure_swagger
from authx.exceptions import MissingTokenError
from src.exception_handlers import missing_token_exception_handler

logger = logging.getLogger(__name__)

@asynccontextmanager
async def app_lifespan(app: FastAPI):
    logger.info("Starting application...")
    
    consumer = RabbitMQConsumer(
        amqp_url=settings.RABBITMQ_URL,
        queue_name=settings.RABBITMQ_CONSUMER_QUEUE_NAME
    )
    consumer.set_handler(handle_book_event)
    
    consumer_task = asyncio.create_task(consumer.consume())
    app.state.rabbitmq_consumer_task = consumer_task
    
    logger.info("RabbitMQ consumer started")
    yield
    
    logger.info("Shutting down application...")
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        logger.info("Consumer stopped gracefully")

app = FastAPI(lifespan=app_lifespan)
app.include_router(router)
configure_swagger(app)
app.add_exception_handler(MissingTokenError, missing_token_exception_handler)
