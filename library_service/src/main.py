from fastapi import FastAPI
from src.library.router import router

app = FastAPI()

app.include_router(router)
