from fastapi import FastAPI
from src.books.router import router

app = FastAPI()

app.include_router(router)
