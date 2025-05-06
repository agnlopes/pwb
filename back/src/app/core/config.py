# src/app/core/config.py
import os
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str
    VERSION: str
    DESCRIPTION: str
    API_PREFIX: str = "/api/v1"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    SECRET_KEY: str
    LOG_DIR: str = "logs"
    LOG_FILE: str = os.path.join(LOG_DIR, "app.log")
    
    # Database settings
    DATABASE_TYPE: str
    DATABASE_URL: Optional[str] = None
    SQLITE_DB: str
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    DB_ECHO: bool = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.DATABASE_URL is None:
            self.DATABASE_URL = self.SQLITE_DB

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields in the .env file


settings = Settings()
