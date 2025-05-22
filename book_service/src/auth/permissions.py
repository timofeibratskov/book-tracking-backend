from fastapi import Depends, HTTPException, status
from authx import RequestToken, TokenPayload

from src.auth.auth import security


async def require_authenticated(token: RequestToken = Depends(security.access_token_required)) -> RequestToken:
    return token


async def require_admin(payload: TokenPayload = Depends(security.access_token_required)) -> TokenPayload:
    if "admin" not in getattr(payload, "role", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return payload
