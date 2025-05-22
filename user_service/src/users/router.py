from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from src.users.service import UserService
from src.users.schemas import UserResponse, UserRequest, Token
from src.dependencies import get_user_service
from src.auth import security
from authx import RequestToken,TokenPayload
from src.users.exceptions import (
    UserNotFoundError, 
    EmailAlreadyExistsError, 
    InvalidCredentialsError,
    ServiceError
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=Token)
async def create_user(
    user_creds: UserRequest,
    service: UserService = Depends(get_user_service),
):
    try:
        user = await service.login(user_creds)
        token = security.create_access_token(
            uid=str(user.id),
            data={
            "role": user.role.value, 
            }
        )  

        return {"access_token": token, "token_type": "bearer"}
    except EmailAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{e.args[0]}' already registered."
        )
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while creating user."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error occurred."
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    token: RequestToken = Depends(security.access_token_required),
    service: UserService = Depends(get_user_service)
):
    try:
        if str(token.sub) != str(user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this user.")
        await service.delete_user(user_id)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    except ServiceError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while deleting user."
        )


@router.get("/me", response_model=UserResponse)
async def get_me(
    token: RequestToken = Depends(security.access_token_required),
    service: UserService = Depends(get_user_service)
):
    try:
        return await service.get_user(UUID(token.sub))
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    except ServiceError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error.")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or user not found."
        )


@router.post("/login")
async def login(
    user_creds: UserRequest,
    service: UserService = Depends(get_user_service)
):
    try:
        user = await service.login(user_creds)
        token = security.create_access_token(
            uid=str(user.id),
            data={
            "role": user.role.value, 
    }
        )
        return {"access_token": token, "token_type": "bearer"}
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found."
        )
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials."
        )
    except ServiceError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login."
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error occurred during login."
        )
