from src.users.repository import IUserRepository 
from src.users.schemas import UserResponse, UserRequest, UserRole
from src.users.models import UserModel
from uuid import UUID
from passlib.context import CryptContext
from src.users.exceptions import (
    UserNotFoundError, 
    EmailAlreadyExistsError, 
    RepositoryError,
    InvalidCredentialsError,
    ServiceError
)

class UserService:
    def __init__(self, repo: IUserRepository):
        self._repo = repo
        self._pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def create_user(self, user_req: UserRequest) -> UserResponse:
        try:
            existing_user = await self._repo.get_by_email(user_req.email)
            if existing_user:
                raise EmailAlreadyExistsError(user_req.email)

            user_model = UserModel(
                email=user_req.email,
                password=self._pwd_context.hash(user_req.password),
                role=UserRole.user  
            )
            created_user = await self._repo.create(user_model)
            return UserResponse(
                id=created_user.id,
                email=created_user.email,
                role=created_user.role
            )
        except RepositoryError as e:
            raise ServiceError(f"Repository error occurred while creating user: {e}", original_error=e) from e
        except Exception as e:
            raise ServiceError("Unexpected error occurred while creating user", original_error=e) from e

    async def get_user(self, user_id: UUID) -> UserResponse:
        try:
            user = await self._repo.get_by_id(user_id)
            if not user:
                raise UserNotFoundError(str(user_id))
            return UserResponse(
                id=user.id,
                email=user.email,
                role=user.role
            )
        except RepositoryError as e:
            raise ServiceError(f"Repository error occurred while fetching user: {e}", original_error=e) from e
        except UserNotFoundError:
            raise
        except Exception as e:
            raise ServiceError("Unexpected error occurred while fetching user", original_error=e) from e

    async def delete_user(self, user_id: UUID) -> None:
        try:
            deleted_count = await self._repo.delete(user_id)
            if deleted_count == 0:
                raise UserNotFoundError(str(user_id))
        except RepositoryError as e:
            raise ServiceError(f"Repository error occurred while deleting user: {e}", original_error=e) from e
        except UserNotFoundError:
            raise
        except Exception as e:
            raise ServiceError("Unexpected error occurred while deleting user", original_error=e) from e

    async def login(self, user_req: UserRequest) -> UserResponse:
        try:
            user = await self._repo.get_by_email(user_req.email)
            if not user:
                raise UserNotFoundError(user_req.email)
            if not self._pwd_context.verify(user_req.password, user.password):
                raise InvalidCredentialsError()
            return UserResponse(
                id=user.id,
                email=user.email,
                role=user.role
            )
        except RepositoryError as e:
            raise ServiceError(f"Repository error occurred during login attempt: {e}", original_error=e) from e
        except (UserNotFoundError, InvalidCredentialsError):
            raise
        except Exception as e:
            raise ServiceError("Unexpected error occurred during login attempt", original_error=e) from e
