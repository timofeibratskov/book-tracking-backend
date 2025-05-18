import aio_pika
import logging
from typing import Callable, Awaitable
from src.rabbit.schemas import BookEvent
import asyncio

logger = logging.getLogger(__name__)

class RabbitMQConsumer:
    def __init__(self, amqp_url: str, queue_name: str):
        self.amqp_url = amqp_url
        self.queue_name = queue_name
        self._handler = None
        self._connection = None
        self._channel = None

    def set_handler(self, handler: Callable[[BookEvent], Awaitable[None]]):
        """Установка асинхронного обработчика сообщений"""
        if not asyncio.iscoroutinefunction(handler):
            raise TypeError("Handler must be an async function")
        self._handler = handler

    async def _ensure_connection(self):
        """Гарантирует наличие подключения"""
        if not self._connection or self._connection.is_closed:
            self._connection = await aio_pika.connect_robust(self.amqp_url)
            self._channel = await self._connection.channel()

    async def consume(self):
        await self._ensure_connection()
        
        exchange = await self._channel.declare_exchange(
            "book_events", aio_pika.ExchangeType.TOPIC, durable=True)
        queue = await self._channel.declare_queue(self.queue_name, durable=True)
        await queue.bind(exchange, routing_key="book.*")

        logger.info(f"Consumer started for {self.queue_name}")
        
        try:
            await queue.consume(self._process_message)
            while True: await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
        finally:
            if self._connection:
                await self._connection.close()

    async def _process_message(self, message: aio_pika.IncomingMessage):
        async with message.process():
            try:
                event = BookEvent.model_validate_json(message.body.decode())
                if self._handler:
                    await self._handler(event)
            except Exception as e:
                logger.error(f"Message failed: {e}")
                await message.reject(requeue=False)