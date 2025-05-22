from fastapi import FastAPI
from src.users.router import router
from src.openapi_config import configure_swagger
from src.exception_handlers import register_user_exception_handlers


app = FastAPI()
app.include_router(router)

configure_swagger(app)
register_user_exception_handlers(app)
