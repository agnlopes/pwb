# src/app/core/config.py
import os
from typing import List, Optional, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str
    VERSION: str
    DESCRIPTION: str
    API_PREFIX: str = "/api/v1"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    SECRET_KEY: str
    ENV: str = "prod"
    
    # Logging settings
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_FORMAT: str = "json"  # or "text"
    LOG_DIR: str = "logs"
    LOG_FILE: str = os.path.join(LOG_DIR, "app.log")
    LOG_MAX_BYTES: int = 5_000_000  # 5MB
    LOG_BACKUP_COUNT: int = 3
    LOG_STDOUT_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "WARNING"
    LOG_USER_ACTIONS: Literal["all", "write"] = "write"  # Log all actions or only write operations
    
    # Tracing settings
    TRACING_ENABLED: bool = True
    TRACING_HEADER: str = "X-Correlation-ID"
    TRACING_GENERATE_IF_MISSING: bool = True
    
    # Database settings
    DATABASE_TYPE: str
    DATABASE_URL: str
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    DB_ECHO: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"  # Allow extra fields in the .env file
    )


settings = Settings()
