from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from authx.exceptions import MissingTokenError, JWTDecodeError
from src.users.exceptions import (
    UserNotFoundError,
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    ServiceError,
)


async def missing_token_exception_handler(request: Request, exc: MissingTokenError):
    return JSONResponse(
        status_code=HTTP_401_UNAUTHORIZED,
        content={"detail": "Authorization token is missing."},
    )


async def jwt_decode_exception_handler(request: Request, exc: JWTDecodeError):
    if "expired" in str(exc).lower():
        detail = "Token has expired"
    else:
        detail = "Invalid or malformed token"
    return JSONResponse(
        status_code=HTTP_401_UNAUTHORIZED,
        content={"detail": detail},
    )


async def user_not_found_exception_handler(request: Request, exc: UserNotFoundError):
    return JSONResponse(
        status_code=HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


async def email_exists_exception_handler(request: Request, exc: EmailAlreadyExistsError):
    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


async def invalid_credentials_exception_handler(request: Request, exc: InvalidCredentialsError):
    return JSONResponse(
        status_code=HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc)},
    )


async def service_error_handler(request: Request, exc: ServiceError):
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )


def register_user_exception_handlers(app):
    app.add_exception_handler(MissingTokenError, missing_token_exception_handler)
    app.add_exception_handler(JWTDecodeError, jwt_decode_exception_handler)
    app.add_exception_handler(UserNotFoundError, user_not_found_exception_handler)
    app.add_exception_handler(EmailAlreadyExistsError, email_exists_exception_handler)
    app.add_exception_handler(InvalidCredentialsError, invalid_credentials_exception_handler)
    app.add_exception_handler(ServiceError, service_error_handler)
