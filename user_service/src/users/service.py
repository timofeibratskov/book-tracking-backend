from src.users.repository import IUserRepository 
from src.users.schemas import UserResponse, UserRequest
from src.users.models import UserModel, UserRole
from uuid import UUID

class UserService:
    def __init__(self, repo: IUserRepository):
        self._repo = repo


    async def create_user(self, user_req: UserRequest) -> UserResponse:
        if await self._repo.get_by_email(user_req.email):
            raise ValueError("Email already exists")
        
        user_model = UserModel(
            email=user_req.email,
            password=user_req.password
            )
        user = await self._repo.create(user_model)
       
        return UserResponse(
            id=user.id,
            email= user.email
                            )

    async def delete_user(self, user_id: UUID) -> None:
        return await self._repo.delete(user_id)

    async def get_user(self, user_id: UUID) -> UserResponse:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        return UserResponse(id=user.id, email=user.email)

    async def login(self, user_req: UserRequest) -> UserResponse:
        user = await self._repo.get_by_email(user_req.email)
        if not user:
            raise ValueError("User not found")
        if user.password != user_req.password:
            raise ValueError("Invalid credentials")
        return UserResponse(
            id=user.id,
            email=user.email
            )