from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from src.users.service import UserService
from src.users.schemas import UserResponse, UserRequest, Token
from src.dependencies import get_user_service
from src.auth import security
from authx import RequestToken

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=Token)
async def create_user(
    user_creds: UserRequest,
    service: UserService = Depends(get_user_service),
):
    user = await service.login(user_creds)
    token = security.create_access_token(
        uid=str(user.id),
        data={"role": user.role.value},
    )
    return {"access_token": token, "token_type": "bearer"}


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    token: RequestToken = Depends(security.access_token_required),
    service: UserService = Depends(get_user_service),
):
    if str(token.sub) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user.",
        )
    await service.delete_user(user_id)


@router.get("/me", response_model=UserResponse)
async def get_me(
    token: RequestToken = Depends(security.access_token_required),
    service: UserService = Depends(get_user_service),
):
    return await service.get_user(UUID(token.sub))


@router.post("/login", response_model=Token)
async def login(
    user_creds: UserRequest,
    service: UserService = Depends(get_user_service),
):
    user = await service.login(user_creds)
    token = security.create_access_token(
        uid=str(user.id),
        data={"role": user.role.value},
    )
    return {"access_token": token, "token_type": "bearer"}
