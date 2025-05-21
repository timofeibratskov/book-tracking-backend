from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from src.users.service import UserService
from src.users.schemas import  UserResponse, UserRequest, Token
from src.dependencies import get_user_service
from src.users.models import UserRole
from src.auth import security
from authx import RequestToken
import traceback

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=Token)
async def create_user(
    user_data: UserRequest,
    service: UserService = Depends(get_user_service),
):
    try:
        user = await service.create_user(user_data)
        token = security.create_access_token(
            uid=str(user.id),
            role=user.role
        )
        return {"access_token": token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    token: RequestToken = Depends(security.access_token_required),
    service: UserService = Depends(get_user_service)
):
    try:
        await service.delete_user(token.sub)
    except ValueError:
        raise HTTPException(404, detail="User not found")


@router.get("/me", response_model=UserResponse)
async def get_me(
    token: RequestToken = Depends(security.access_token_required),
    service: UserService = Depends(get_user_service)
):
    try:
        return await service.get_user(UUID(token.sub))
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print("Ошибка при получении пользователя:")
        traceback.print_exc()  # Вывод полного трейсбэка
        raise HTTPException(status_code=401, detail=f"Invalid token or user not found: {e}")


@router.post("/login")
async def login(
    user_creds: UserRequest, 
    service: UserService = Depends(get_user_service)
):
    try:
        user = await service.login(user_creds)
        token = security.create_access_token(
            uid=str(user.id),
            role=user.role
        )
        return {"access_token": token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(401, detail=str(e))