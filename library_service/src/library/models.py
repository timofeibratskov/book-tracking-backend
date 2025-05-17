from sqlalchemy import Column, UUID, DateTime, Boolean
from src.database import Base  

class BookStatusModel(Base):
    __tablename__ = "book_status"

    book_id = Column(UUID(as_uuid=True), primary_key=True)
    borrowed_at = Column(DateTime)
    returned_at = Column(DateTime)
    is_available = Column(Boolean)
