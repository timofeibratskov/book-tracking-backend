import pytest
from unittest.mock import AsyncMock
from uuid import uuid4, UUID
from src.books.service import BookService
from src.books.schemas import BookCreate, BookUpdate, Book
from src.books.models import BookModel
from src.books.exceptions import (
    ISBNAlreadyExistsError,
    BookNotFoundError,
    RepositoryError,
    ServiceError,
)
from src.books.schemas import Language, Genre
from sqlalchemy.exc import IntegrityError


@pytest.mark.asyncio
async def test_create_book_success():
    fake_id = uuid4()
    book_data = BookCreate(
        title="Test Title",
        author="Test Author",
        isbn="1234567890",
        description="Desc",
        language="en",
        genre="fiction"
    )
    db_book = BookModel(id=fake_id, **book_data.model_dump())
    
    mock_repo = AsyncMock()
    mock_repo.create.return_value = db_book
    
    mock_producer = AsyncMock()
    
    service = BookService(repo=mock_repo, producer=mock_producer)
    result = await service.create_book(book_data)
    
    assert isinstance(result, Book)
    assert result.id == fake_id
    mock_repo.create.assert_called_once()
    mock_producer.send_event.assert_called_once_with(fake_id, "created")

@pytest.mark.asyncio
async def test_create_book_isbn_exists():
    # Arrange
    book_data = BookCreate(
        title="Title",
        author="Author",
        isbn="1234567890",
        description="Desc",
        language="en",
        genre="fiction"
    )
    mock_repo = AsyncMock()
    mock_producer = AsyncMock()

    integrity_error = IntegrityError("duplicate key value violates unique constraint", {}, None)
    repo_error = Exception("Repo", integrity_error)
    mock_repo.create.side_effect = repo_error

    service = BookService(mock_repo, mock_producer)

    # Act & Assert
    with pytest.raises(Exception):  # можно заменить на ServiceError, если обернул
        await service.create_book(book_data)


@pytest.mark.asyncio
async def test_create_book_generic_repo_error():
    book_data = BookCreate(
        title="Title",
        author="Author",
        isbn="1233211231",
        description="Desc",
        language="en",
        genre="fiction"
    )
    
    mock_repo = AsyncMock()
    mock_repo.create.side_effect = RepositoryError("Something went wrong")
    mock_producer = AsyncMock()
    
    service = BookService(repo=mock_repo, producer=mock_producer)
    
    with pytest.raises(ServiceError) as exc:
        await service.create_book(book_data)
    assert "Repository error" in str(exc.value)


@pytest.mark.asyncio
async def test_get_book_success():
    # Arrange
    book_id = uuid4()
    book_model = BookModel(id=book_id, title="fT", author="Af", isbn="1234567890", description="D", language=Language.EN.value,genre=Genre.FICTION.value)
    mock_repo = AsyncMock()
    mock_repo.get.return_value = book_model

    service = BookService(mock_repo, AsyncMock())

    # Act
    book = await service.get_book(book_id)

    # Assert
    assert book.id == book_id
    mock_repo.get.assert_called_once_with(book_id)



@pytest.mark.asyncio
async def test_list_books_repo_error():
    mock_repo = AsyncMock()
    mock_repo.get_all.side_effect = RepositoryError("DB fail")
    mock_producer = AsyncMock()
    
    service = BookService(repo=mock_repo, producer=mock_producer)
    with pytest.raises(ServiceError):
        await service.list_books()


@pytest.mark.asyncio
async def test_get_book_found():
    book_id = uuid4()
    mock_book = BookModel(id=book_id, title="Tf", author="Af", isbn="1234567890", description="D", language=Language.EN.value,genre=Genre.FICTION.value)
    
    mock_repo = AsyncMock()
    mock_repo.get.return_value = mock_book
    mock_producer = AsyncMock()
    
    service = BookService(repo=mock_repo, producer=mock_producer)
    book = await service.get_book(book_id)
    
    assert isinstance(book, Book)
    assert book.id == book_id


@pytest.mark.asyncio
async def test_get_book_not_found():
    book_id = uuid4()
    mock_repo = AsyncMock()
    mock_repo.get.return_value = None

    service = BookService(mock_repo, AsyncMock())

    with pytest.raises(BookNotFoundError):
        await service.get_book(book_id)



@pytest.mark.asyncio
async def test_update_book_success():
    book_id = uuid4()
    original_book = BookModel(
        id=book_id, title="Old", author="Af", isbn="1234567890", description="Old", language=Language.EN.value,genre=Genre.FICTION.value
    )
    updated_data = BookUpdate(title="New Title")

    mock_repo = AsyncMock()
    mock_repo.get.return_value = original_book
    mock_repo.update.return_value = original_book  # можно имитировать возврат того же объекта

    service = BookService(mock_repo, AsyncMock())

    result = await service.update_book(book_id, updated_data)

    assert result.title == "New Title"
    mock_repo.update.assert_called_once()


@pytest.mark.asyncio
async def test_update_book_not_found():
    book_id = uuid4()
    update_data = BookUpdate(title="New Title")
    
    mock_repo = AsyncMock()
    mock_repo.get.return_value = None
    mock_producer = AsyncMock()
    service = BookService(repo=mock_repo, producer=mock_producer)
    
    with pytest.raises(BookNotFoundError):
        await service.update_book(book_id, update_data)


@pytest.mark.asyncio
async def test_update_book_isbn_conflict():
    book_id = uuid4()
    existing_book = BookModel(id=book_id, title="Old", author="Ag", isbn="1231231233", description="", language=Language.EN.value,genre=Genre.FICTION.value)
    update_data = BookUpdate(isbn="1234567890123")
    
    mock_repo = AsyncMock()
    mock_repo.get.return_value = existing_book
    err = RepositoryError(original_error=IntegrityError("UNIQUE constraint failed: isbn", None, None))
    mock_repo.update.side_effect = err
    
    mock_producer = AsyncMock()
    service = BookService(repo=mock_repo, producer=mock_producer)
    
    with pytest.raises(ISBNAlreadyExistsError):
        await service.update_book(book_id, update_data)


@pytest.mark.asyncio
async def test_delete_book_success():
    book_id = uuid4()
    
    mock_repo = AsyncMock()
    mock_repo.delete.return_value = 1
    
    mock_producer = AsyncMock()
    service = BookService(repo=mock_repo, producer=mock_producer)
    
    result = await service.delete_book(book_id)
    assert result is None
    mock_producer.send_event.assert_called_once_with(book_id, "deleted")


@pytest.mark.asyncio
async def test_delete_book_not_found():
    book_id = uuid4()
    
    mock_repo = AsyncMock()
    mock_repo.delete.return_value = 0
    
    mock_producer = AsyncMock()
    service = BookService(repo=mock_repo, producer=mock_producer)
    
    with pytest.raises(BookNotFoundError):
        await service.delete_book(book_id)


@pytest.mark.asyncio
async def test_delete_book_repo_error():
    book_id = uuid4()
    
    mock_repo = AsyncMock()
    mock_repo.delete.side_effect = RepositoryError("DB error")
    
    mock_producer = AsyncMock()
    service = BookService(repo=mock_repo, producer=mock_producer)
    
    with pytest.raises(ServiceError):
        await service.delete_book(book_id)
