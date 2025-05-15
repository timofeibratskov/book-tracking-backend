from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from src.config import settings

engine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=True,  
    pool_size=10,  
    max_overflow=20,
)

session_factory = async_sessionmaker(engine)

Base = declarative_base()