from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from authx.exceptions import MissingTokenError
from src.library.exceptions import (
    InvalidUUIDError,
    BookStatusNotFoundError,
    BookNotAvailableError,
    BookNotBorrowedError,
    ServiceError,
)


async def missing_token_exception_handler(request: Request, exc: MissingTokenError):
    return JSONResponse(
        status_code=HTTP_401_UNAUTHORIZED,
        content={"detail": "Authorization header with Bearer token is required"},
    )


async def invalid_uuid_handler(request: Request, exc: InvalidUUIDError):
    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


async def book_status_not_found_handler(request: Request, exc: BookStatusNotFoundError):
    return JSONResponse(
        status_code=HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


async def book_not_available_handler(request: Request, exc: BookNotAvailableError):
    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


async def book_not_borrowed_handler(request: Request, exc: BookNotBorrowedError):
    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


async def service_error_handler(request: Request, exc: ServiceError):
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )


def register_exception_handlers(app):
    app.add_exception_handler(MissingTokenError, missing_token_exception_handler)
    app.add_exception_handler(InvalidUUIDError, invalid_uuid_handler)
    app.add_exception_handler(BookStatusNotFoundError, book_status_not_found_handler)
    app.add_exception_handler(BookNotAvailableError, book_not_available_handler)
    app.add_exception_handler(BookNotBorrowedError, book_not_borrowed_handler)
    app.add_exception_handler(ServiceError, service_error_handler)
