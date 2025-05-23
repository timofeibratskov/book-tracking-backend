import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from src.users.service import UserService
from src.users.schemas import UserRequest, UserRole
from src.users.exceptions import (
    EmailAlreadyExistsError,
    UserNotFoundError,
    InvalidCredentialsError,
    ServiceError,
)

@pytest.fixture
def mock_repo():
    return AsyncMock()

@pytest.fixture
def user_service(mock_repo):
    return UserService(mock_repo)

@pytest.mark.asyncio
async def test_create_user_success(user_service, mock_repo):
    mock_repo.get_by_email.return_value = None

    fake_user_id = uuid4()
    created_user = AsyncMock()
    created_user.id = fake_user_id
    created_user.email = "test@example.com"
    created_user.role = UserRole.user

    mock_repo.create.return_value = created_user

    user_req = UserRequest(email="test@example.com", password="password123")
    user_resp = await user_service.create_user(user_req)

    assert user_resp.email == user_req.email
    assert user_resp.role == UserRole.user
    assert user_resp.id == fake_user_id
    mock_repo.get_by_email.assert_awaited_once_with(user_req.email)
    mock_repo.create.assert_awaited_once()

@pytest.mark.asyncio
async def test_create_user_email_already_exists(user_service, mock_repo):
    mock_repo.get_by_email.return_value = AsyncMock()

    user_req = UserRequest(email="exist@example.com", password="pass")

    with pytest.raises(EmailAlreadyExistsError):
        await user_service.create_user(user_req)

@pytest.mark.asyncio
async def test_get_user_success(user_service, mock_repo):
    fake_user_id = uuid4()
    found_user = AsyncMock()
    found_user.id = fake_user_id
    found_user.email = "found@example.com"
    found_user.role = UserRole.admin

    mock_repo.get_by_id.return_value = found_user

    user_resp = await user_service.get_user(fake_user_id)

    assert user_resp.id == fake_user_id
    assert user_resp.email == found_user.email
    assert user_resp.role == UserRole.admin
    mock_repo.get_by_id.assert_awaited_once_with(fake_user_id)

@pytest.mark.asyncio
async def test_get_user_not_found(user_service, mock_repo):
    mock_repo.get_by_id.return_value = None
    fake_user_id = uuid4()

    with pytest.raises(UserNotFoundError):
        await user_service.get_user(fake_user_id)

@pytest.mark.asyncio
async def test_delete_user_success(user_service, mock_repo):
    mock_repo.delete.return_value = 1
    fake_user_id = uuid4()

    await user_service.delete_user(fake_user_id)

    mock_repo.delete.assert_awaited_once_with(fake_user_id)

@pytest.mark.asyncio
async def test_delete_user_not_found(user_service, mock_repo):
    mock_repo.delete.return_value = 0
    fake_user_id = uuid4()

    with pytest.raises(UserNotFoundError):
        await user_service.delete_user(fake_user_id)

@pytest.mark.asyncio
async def test_login_success(user_service, mock_repo):
    fake_user_id = uuid4()
    user_in_db = AsyncMock()
    user_in_db.id = fake_user_id
    user_in_db.email = "login@example.com"
    user_in_db.role = UserRole.user
    # Хеш пароля для "password123"
    user_in_db.password = user_service._pwd_context.hash("password123")

    mock_repo.get_by_email.return_value = user_in_db

    user_req = UserRequest(email="login@example.com", password="password123")
    user_resp = await user_service.login(user_req)

    assert user_resp.email == user_req.email
    assert user_resp.id == fake_user_id
    assert user_resp.role == UserRole.user

@pytest.mark.asyncio
async def test_login_user_not_found(user_service, mock_repo):
    mock_repo.get_by_email.return_value = None
    user_req = UserRequest(email="missing@example.com", password="pass")

    with pytest.raises(UserNotFoundError):
        await user_service.login(user_req)

@pytest.mark.asyncio
async def test_login_invalid_password(user_service, mock_repo):
    user_in_db = AsyncMock()
    user_in_db.email = "user@example.com"
    user_in_db.password = user_service._pwd_context.hash("correct_password")
    user_in_db.id = uuid4()
    user_in_db.role = UserRole.user

    mock_repo.get_by_email.return_value = user_in_db
    user_req = UserRequest(email="user@example.com", password="wrong_password")

    with pytest.raises(InvalidCredentialsError):
        await user_service.login(user_req)
