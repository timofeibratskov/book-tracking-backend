from src.users.repository import IUserRepository 
from src.users.schemas import UserResponse, UserRequest,UserRole
from src.users.models import UserModel
from uuid import UUID
from passlib.context import CryptContext

class UserService:
    def __init__(self, repo: IUserRepository):
        self._repo = repo
        self._pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


    async def create_user(self, user_req: UserRequest) -> UserResponse:
        if await self._repo.get_by_email(user_req.email):
            raise ValueError("Email already exists")
        
        user_model = UserModel(
            email=user_req.email,
            password=user_req.password 
            )
        user =  await self._repo.create(user_model)
        return UserResponse(
            id=user.id,                
            email=user.email,
            role=UserRole.user
            )
        #  password=self._pwd_context.hash(user_req.password)


    async def delete_user(self, id: UUID) -> bool:
            deleted_count = await self._repo.delete(id)
            if deleted_count == 0:
                raise ValueError("User not found")
            return True
        

    async def get_user(self, id: UUID) -> UserResponse:
            user = await self._repo.get_by_id(id)
            if not user:
                raise ValueError("User not found")
            return UserResponse(
                 id=user.id,
                 email=user.email,
                 role=user.role
            )
        

    async def login(self, user_req: UserRequest) -> UserResponse:
        user = await self._repo.get_by_email(user_req.email)
        if not user:
            raise ValueError("User not found")
        if user.password != user_req.password:
            raise ValueError("Invalid credentials")
        return UserResponse(
            id=user.id,
            email=user.email,
            role=user.role
        )
            