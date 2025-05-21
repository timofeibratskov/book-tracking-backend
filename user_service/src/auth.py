from authx import AuthX, AuthXConfig
from src.config import settings

config = AuthXConfig(
JWT_SECRET_KEY=settings.JWT_KEY,
JWT_ALGORITHM="HS256",
JWT_ACCESS_TOKEN_EXPIRES=3600,
JWT_TOKEN_LOCATION=["headers"]
)

security = AuthX(config)