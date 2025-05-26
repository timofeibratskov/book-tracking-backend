from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from src.users.service import UserService
from src.users.schemas import UserResponse, UserRequest, Token
from src.dependencies import get_user_service
from src.auth import security
from authx import RequestToken

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/register",
    response_model=Token,
    status_code=status.HTTP_201_CREATED,
    summary="Зарегистрировать пользователя",
    description="Создаёт нового пользователя и возвращает токен доступа.",
    response_description="Токен доступа",
    responses={
        201: {"description": "Пользователь зарегистрирован"},
        422: {"description": "Ошибка валидации данных"},
        409: {"description": "Пользователь уже существует (если реализовано)"},
    },
)
async def create_user(
    user_creds: UserRequest,
    service: UserService = Depends(get_user_service),
):
    user = await service.create_user(user_creds)
    token = security.create_access_token(
        uid=str(user.id),
        data={"role": user.role.value},
    )
    return {"access_token": token, "token_type": "bearer"}


@router.post(
    "/login",
    response_model=Token,
    summary="Авторизация пользователя",
    description="Аутентифицирует пользователя и возвращает токен доступа.",
    response_description="Токен доступа",
    responses={
        200: {"description": "Успешный вход"},
        401: {"description": "Неверные учетные данные"},
        422: {"description": "Ошибка валидации данных"},
    },
)
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


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Получить текущего пользователя",
    description="Возвращает информацию о текущем авторизованном пользователе.",
    response_description="Данные пользователя",
    responses={
        200: {"description": "Пользователь найден"},
        401: {"description": "Необходима авторизация"},
        404: {"description": "Пользователь не найден"},
    },
)
async def get_me(
    token: RequestToken = Depends(security.access_token_required),
    service: UserService = Depends(get_user_service),
):
    return await service.get_user(UUID(token.sub))


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить пользователя",
    description="Удаляет пользователя по ID. Только сам пользователь может удалить свой аккаунт.",
    response_description="Пользователь удалён",
    responses={
        204: {"description": "Пользователь успешно удалён"},
        401: {"description": "Необходима авторизация"},
        403: {"description": "Недостаточно прав для удаления этого пользователя"},
        404: {"description": "Пользователь не найден"},
    },
)
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
