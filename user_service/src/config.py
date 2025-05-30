from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

#load_dotenv("D:/Users/Тимофей/PythonProjects/fastapi-library/book_service/.env")


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str


    JWT_KEY: str

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

   
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()