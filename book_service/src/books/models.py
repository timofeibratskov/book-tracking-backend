from sqlalchemy import Column, String, UUID
import uuid
from src.database import Base  

class BookModel(Base):
    __tablename__ = "books"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    isbn = Column(String, unique=True, nullable=False)
    description = Column(String)
    language = Column(String)
    genre = Column(String)