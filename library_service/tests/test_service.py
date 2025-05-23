import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from datetime import datetime
from pydantic import ValidationError

from src.library.service import LibraryService
from src.library.schemas import BookStatus
from src.library.models import BookStatusModel
from src.library.exceptions import (
    BookStatusNotFoundError,
    BookNotAvailableError,
    BookNotBorrowedError,
    ServiceError,
    RepositoryError
)

@pytest.mark.asyncio
async def test_create_book_status_success():
    book_id = uuid4()
    model = BookStatusModel(book_id=book_id, borrowed_at=None, returned_at=None, is_available=True)
    
    mock_repo = AsyncMock()
    mock_repo.create.return_value = model
    
    service = LibraryService(mock_repo)
    
    result = await service.create_book_status(book_id)
    
    assert isinstance(result, BookStatus)
    assert result.book_id == book_id
    assert result.is_available is True
    mock_repo.create.assert_awaited_once()

@pytest.mark.asyncio
async def test_create_book_status_repository_error():
    book_id = uuid4()
    
    mock_repo = AsyncMock()
    mock_repo.create.side_effect = RepositoryError("DB error")
    
    service = LibraryService(mock_repo)
    
    with pytest.raises(ServiceError):
        await service.create_book_status(book_id)

@pytest.mark.asyncio
async def test_delete_book_status_success():
    book_id = uuid4()
    mock_repo = AsyncMock()
    mock_repo.delete.return_value = 1
    
    service = LibraryService(mock_repo)
    
    deleted_count = await service.delete_book_status(book_id)
    
    assert deleted_count == 1
    mock_repo.delete.assert_awaited_once_with(book_id)

@pytest.mark.asyncio
async def test_delete_book_status_repository_error():
    book_id = uuid4()
    mock_repo = AsyncMock()
    mock_repo.delete.side_effect = RepositoryError("DB error")
    
    service = LibraryService(mock_repo)
    
    with pytest.raises(ServiceError):
        await service.delete_book_status(book_id)

@pytest.mark.asyncio
async def test_borrow_book_success():
    book_id = uuid4()
    original_status = BookStatusModel(book_id=book_id, borrowed_at=None, returned_at=None, is_available=True)
    updated_status = BookStatusModel(book_id=book_id, borrowed_at=datetime.now(), returned_at=None, is_available=False)
    
    mock_repo = AsyncMock()
    mock_repo.get.return_value = original_status
    mock_repo.update.return_value = updated_status
    
    service = LibraryService(mock_repo)
    
    result = await service.borrow_book(book_id)
    
    assert isinstance(result, BookStatus)
    assert result.book_id == book_id
    assert result.is_available is False
    assert result.borrowed_at is not None
    mock_repo.get.assert_awaited_once_with(book_id)
    mock_repo.update.assert_awaited_once()

@pytest.mark.asyncio
async def test_borrow_book_not_found():
    book_id = uuid4()
    mock_repo = AsyncMock()
    mock_repo.get.return_value = None
    
    service = LibraryService(mock_repo)
    
    with pytest.raises(BookStatusNotFoundError):
        await service.borrow_book(book_id)

@pytest.mark.asyncio
async def test_borrow_book_not_available():
    book_id = uuid4()
    model = BookStatusModel(book_id=book_id, borrowed_at=None, returned_at=None, is_available=False)
    
    mock_repo = AsyncMock()
    mock_repo.get.return_value = model
    
    service = LibraryService(mock_repo)
    
    with pytest.raises(BookNotAvailableError):
        await service.borrow_book(book_id)

@pytest.mark.asyncio
async def test_borrow_book_repository_error():
    book_id = uuid4()
    mock_repo = AsyncMock()
    mock_repo.get.side_effect = RepositoryError("DB error")
    
    service = LibraryService(mock_repo)
    
    with pytest.raises(ServiceError):
        await service.borrow_book(book_id)

@pytest.mark.asyncio
async def test_return_book_success():
    book_id = uuid4()
    original_status = BookStatusModel(book_id=book_id, borrowed_at=datetime.now(), returned_at=None, is_available=False)
    updated_status = BookStatusModel(book_id=book_id, borrowed_at=None, returned_at=None, is_available=True)
    
    mock_repo = AsyncMock()
    mock_repo.get.return_value = original_status
    mock_repo.update.return_value = updated_status
    
    service = LibraryService(mock_repo)
    
    result = await service.return_book(book_id)
    
    assert isinstance(result, BookStatus)
    assert result.book_id == book_id
    assert result.is_available is True
    assert result.borrowed_at is None
    mock_repo.get.assert_awaited_once_with(book_id)
    mock_repo.update.assert_awaited_once()

@pytest.mark.asyncio
async def test_return_book_not_found():
    book_id = uuid4()
    mock_repo = AsyncMock()
    mock_repo.get.return_value = None
    
    service = LibraryService(mock_repo)
    
    with pytest.raises(BookStatusNotFoundError):
        await service.return_book(book_id)

@pytest.mark.asyncio
async def test_return_book_not_borrowed():
    book_id = uuid4()
    model = BookStatusModel(book_id=book_id, borrowed_at=None, returned_at=None, is_available=True)
    
    mock_repo = AsyncMock()
    mock_repo.get.return_value = model
    
    service = LibraryService(mock_repo)
    
    with pytest.raises(BookNotBorrowedError):
        await service.return_book(book_id)

@pytest.mark.asyncio
async def test_return_book_repository_error():
    book_id = uuid4()
    mock_repo = AsyncMock()
    mock_repo.get.side_effect = RepositoryError("DB error")
    
    service = LibraryService(mock_repo)
    
    with pytest.raises(ServiceError):
        await service.return_book(book_id)

@pytest.mark.asyncio
async def test_get_book_status_success():
    book_id = uuid4()
    model = BookStatusModel(book_id=book_id, borrowed_at=None, returned_at=None, is_available=True)
    
    mock_repo = AsyncMock()
    mock_repo.get.return_value = model
    
    service = LibraryService(mock_repo)
    
    result = await service.get_book_status(book_id)
    
    assert isinstance(result, BookStatus)
    assert result.book_id == book_id
    mock_repo.get.assert_awaited_once_with(book_id)

@pytest.mark.asyncio
async def test_get_book_status_not_found():
    book_id = uuid4()
    
    mock_repo = AsyncMock()
    mock_repo.get.return_value = None
    
    service = LibraryService(mock_repo)
    
    with pytest.raises(BookStatusNotFoundError):
        await service.get_book_status(book_id)

@pytest.mark.asyncio
async def test_get_book_status_repository_error():
    book_id = uuid4()
    mock_repo = AsyncMock()
    mock_repo.get.side_effect = RepositoryError("DB error")
    
    service = LibraryService(mock_repo)
    
    with pytest.raises(ServiceError):
        await service.get_book_status(book_id)

@pytest.mark.asyncio
async def test_get_available_books_success():
    book_id1 = uuid4()
    book_id2 = uuid4()
    model1 = BookStatusModel(book_id=book_id1, borrowed_at=None, returned_at=None, is_available=True)
    model2 = BookStatusModel(book_id=book_id2, borrowed_at=None, returned_at=None, is_available=True)
    
    mock_repo = AsyncMock()
    mock_repo.get_all.return_value = [model1, model2]
    
    service = LibraryService(mock_repo)
    
    results = await service.get_available_books()
    
    assert isinstance(results, list)
    assert all(isinstance(book, BookStatus) for book in results)
    assert len(results) == 2
    mock_repo.get_all.assert_awaited_once_with(is_available=True)

@pytest.mark.asyncio
async def test_get_available_books_repository_error():
    mock_repo = AsyncMock()
    mock_repo.get_all.side_effect = RepositoryError("DB error")
    
    service = LibraryService(mock_repo)
    
    with pytest.raises(ServiceError):
        await service.get_available_books()
