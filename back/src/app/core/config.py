# src/app/core/config.py
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Portfolio Workbench"
    API_PREFIX: str = "/api/v1"
    SECRET_KEY: str
    DATABASE_URL: str
    LOG_DIR: str = "logs"
    LOG_FILE: str = os.path.join(LOG_DIR, "app.log")

    class Config:
        env_file = os.getenv("ENV_FILE", ".env")
        env_file_encoding = "utf-8"
        case_sensitive = True
        env_prefix = ""


settings = Settings()
