from fastapi import  Request
from src.rabbit.producer import AsyncioRabbitMQProducer 

def get_rabbitmq_producer(request: Request) -> AsyncioRabbitMQProducer:
    producer_instance = getattr(request.app.state, 'rabbitmq_producer', None)

    if not isinstance(producer_instance, AsyncioRabbitMQProducer):
        raise RuntimeError("RabbitMQ Producer is not available in app state or not correctly initialized.")

    return producer_instance