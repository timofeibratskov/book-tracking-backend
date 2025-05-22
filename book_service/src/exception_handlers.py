from fastapi import Request
from fastapi.responses import JSONResponse
from starlette import status
from authx.exceptions import MissingTokenError, JWTDecodeError

from src.books.exceptions import (
    BookNotFoundError,
    ISBNAlreadyExistsError,
    ServiceError,
    RepositoryError,
    InvalidUUIDError,
    ConcurrentUpdateError,
)


async def missing_token_handler(request: Request, exc: MissingTokenError):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Authorization header with Bearer token is required"},
    )

async def jwt_decode_handler(request: Request, exc: JWTDecodeError):
    detail = "Token has expired" if "expired" in str(exc).lower() else "Invalid or malformed token"
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": detail},
    )

async def forbidden_handler(request: Request, exc: PermissionError):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": "You do not have permission to perform this action"},
    )

async def book_not_found_handler(request: Request, exc: BookNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )

async def isbn_conflict_handler(request: Request, exc: ISBNAlreadyExistsError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc)},
    )

async def concurrent_update_handler(request: Request, exc: ConcurrentUpdateError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc)},
    )

async def invalid_uuid_handler(request: Request, exc: InvalidUUIDError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": str(exc)},
    )

async def service_error_handler(request: Request, exc: ServiceError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )

async def repository_error_handler(request: Request, exc: RepositoryError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )




def register_exception_handlers(app):
    app.add_exception_handler(MissingTokenError, missing_token_handler)
    app.add_exception_handler(JWTDecodeError, jwt_decode_handler)
    app.add_exception_handler(PermissionError, forbidden_handler)

    app.add_exception_handler(BookNotFoundError, book_not_found_handler)
    app.add_exception_handler(ISBNAlreadyExistsError, isbn_conflict_handler)
    app.add_exception_handler(ConcurrentUpdateError, concurrent_update_handler)
    app.add_exception_handler(InvalidUUIDError, invalid_uuid_handler)
    app.add_exception_handler(ServiceError, service_error_handler)
    app.add_exception_handler(RepositoryError, repository_error_handler)