import aio_pika
import asyncio
import json
from uuid import UUID
from typing import Optional


class AsyncioRabbitMQProducer:
    def __init__(self, amqp_url: str): 
        self._amqp_url = amqp_url 
        self._connection: Optional[aio_pika.RobustConnection] = None
        self._channel: Optional[aio_pika.Channel] = None
        self._exchange_name = "book_events"
        self._exchange: Optional[aio_pika.Exchange] = None


    async def connect(self):
        if self._connection is None or self._connection.is_closed:
            try:
                self._connection = await aio_pika.connect_robust(
                    self._amqp_url,
                    loop=asyncio.get_event_loop()
                )
                self._channel = await self._connection.channel()
                self._exchange = await self._channel.declare_exchange(
                    self._exchange_name,
                    aio_pika.ExchangeType.TOPIC,
                    durable=True
                )
            except Exception as e:
                raise


    async def disconnect(self):
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
        self._connection = None
        self._channel = None
        self._exchange = None

    
    async def publish_book_event(self, book_id: UUID, action: str):
        if self._exchange is None:
             return
        message_data = {
            "book_id": str(book_id),
            "action": action
        }
        message_body = json.dumps(message_data).encode('utf-8')
        routing_key = f"book.{action}"
        message = aio_pika.Message(
            body=message_body,
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )
        try:
            await self._exchange.publish(message, routing_key=routing_key)
        except Exception as e:
            raise
