import logging
from uuid import UUID
from src.rabbit.schemas import BookEvent
from src.database import get_session
from src.library.repository import SqlLibraryRepository
from src.library.service import LibraryService

logger = logging.getLogger(__name__)

async def handle_book_event(event: BookEvent):
    """Обработчик событий о книгах"""
    async for session in get_session():
        try:
            service = LibraryService(SqlLibraryRepository(session))
            
            if event.action == "created":
                logger.info(f"Creating book status for {event.book_id}")
                await service.create_book_status(event.book_id)
            elif event.action == "deleted":
                logger.info(f"Deleting book status for {event.book_id}")
                await service.delete_book_status(event.book_id)
                
            await session.commit()
        except Exception as e:
            logger.error(f"Error processing event: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()