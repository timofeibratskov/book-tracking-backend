from fastapi import FastAPI
from src.users.router import router
from src.openapi_config import configure_swagger


app = FastAPI()
app.include_router(router)

configure_swagger(app)