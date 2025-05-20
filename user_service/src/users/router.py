from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from src.users.service import UserService
from src.users.schemas import  UserResponse, UserRequest, Token
from src.dependencies import get_user_service


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=Token)
async def create_user(
    user_data: UserRequest,
    service: UserService = Depends(get_user_service),
):
    try:
        token = await service.create_user(user_data)
        return {"access_token": token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service)
):
    try:
        await service.delete_user(user_id)
    except ValueError:
        raise HTTPException(404, detail="User not found")

@router.get("/me/{id}", response_model=UserResponse)
async def get_me(
    id:UUID,
    service: UserService = Depends(get_user_service)
):
    try:
        user = await service.get_user(id)
        return UserResponse(id=user.id, email=user.email)
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(401, detail="Invalid token")

@router.post("/login")
async def login(
    user_creds: UserRequest, 
    service: UserService = Depends(get_user_service)
):
    try:
        token = await service.login(user_creds)
        return {"access_token": token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(401, detail=str(e))