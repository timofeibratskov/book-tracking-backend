from authx import AuthX, AuthXConfig

config = AuthXConfig(
JWT_SECRET_KEY="super_puper_key",
JWT_ALGORITHM="HS256",
JWT_ACCESS_TOKEN_EXPIRES=3600,
JWT_TOKEN_LOCATION=["headers"]
)
security = AuthX(config)