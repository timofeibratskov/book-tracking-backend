from fastapi import Request, HTTPException
from src.rabbit.producer import RabbitMQProducer

async def get_rabbit_producer(request: Request) -> RabbitMQProducer:
    if not hasattr(request.app.state, 'rabbitmq_producer'):
        raise HTTPException(
            status_code=500,
            detail="RabbitMQ producer not initialized"
        )
    return request.app.state.rabbitmq_producer