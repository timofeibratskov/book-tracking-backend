from fastapi import FastAPI
from src.users.router import router


app = FastAPI()
app.include_router(router)