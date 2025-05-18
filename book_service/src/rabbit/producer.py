import aio_pika
from uuid import UUID
from src.rabbit.schemas import BookEvent
import logging

logger = logging.getLogger(__name__)

class RabbitMQProducer:
    def __init__(self, amqp_url: str):
        self.amqp_url = amqp_url
        self.connection = None
        self.channel = None
        self.exchange = None

    async def connect(self):
        try:
            self.connection = await aio_pika.connect_robust(self.amqp_url)
            self.channel = await self.connection.channel()
            self.exchange = await self.channel.declare_exchange(
                "book_events",
                aio_pika.ExchangeType.TOPIC,
                durable=True
            )
            logger.info("Connected to RabbitMQ")
            return True
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            return False

    async def is_connected(self):
        return self.connection and not self.connection.is_closed

    async def send_event(self, book_id: UUID, action: str):
        if not await self.is_connected():
            if not await self.connect():
                raise ConnectionError("RabbitMQ connection failed")
        
        try:
            event = BookEvent(book_id=book_id, action=action)
            await self.exchange.publish(
                aio_pika.Message(
                    body=event.model_dump_json().encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                ),
                routing_key=f"book.{action}"
            )
            logger.debug(f"Sent event: {event}")
            return True
        except Exception as e:
            logger.error(f"Error sending event: {str(e)}")
            return False

    async def disconnect(self):
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            logger.info("Disconnected from RabbitMQ")