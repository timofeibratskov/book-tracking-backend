from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from src.users.service import UserService
from src.users.schemas import  UserResponse, UserRequest
from src.dependencies import get_user_service

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserRequest,
    service: UserService = Depends(get_user_service)
):
    try:
        return await service.create_user(user_data)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))

@router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service)
):
    if not await service.delete_user(user_id):
        raise HTTPException(404, detail="User not found")
    return {"message": "User deleted"}

@router.get("/{id}", response_model=UserResponse)
async def get_current_user(
    id: UUID, 
    service: UserService = Depends(get_user_service)
):
    try:
        return await service.get_user(id)
    except ValueError as e:
        raise HTTPException(404, detail=str(e))

@router.post("/login", response_model=UserResponse)
async def login(
    user: UserRequest,
    service: UserService = Depends(get_user_service)
):
    try:
        return await service.login(user)
    except ValueError as e:
        raise HTTPException(401, detail=str(e))