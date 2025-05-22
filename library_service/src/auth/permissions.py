from fastapi import Depends, HTTPException, status
from authx import RequestToken, TokenPayload

from src.auth.auth import security


def require_admin(payload: TokenPayload = Depends(security.access_token_required)):
    if "admin" not in getattr(payload, "role", []):
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return payload

def require_authenticated(token: RequestToken = Depends(security.access_token_required)):
    return token

