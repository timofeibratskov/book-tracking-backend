from fastapi import Request
from fastapi.responses import JSONResponse
from authx.exceptions import MissingTokenError
from starlette.status import HTTP_401_UNAUTHORIZED


async def missing_token_exception_handler(request: Request, exc: MissingTokenError):
    return JSONResponse(
        status_code=HTTP_401_UNAUTHORIZED,
        content={"detail": "Authorization header with Bearer token is required"},
    )
