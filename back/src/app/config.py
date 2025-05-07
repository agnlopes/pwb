# src/app/core/config.py
import os
from typing import List, Optional, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # Project settings
    PROJECT_NAME: str = "Portfolio Workbench"
    VERSION: str = "0.1.0"
    API_VERSION: str = "v1"
    DESCRIPTION: str
    API_PREFIX: str = f"/api/{API_VERSION}"
    ENV: str = "dev"
    DEBUG: bool = True

    # Security settings
    SEC_ALGORITHM: str = "HS256"
    SEC_SECRET_KEY: str
    SEC_TOKEN_EXPIRE_MINUTES: int = 30
    SEC_CORS_ORIGINS: List[str] = ["http://localhost:8000"]

    # Logging settings
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_FORMAT: str = "json"  # or "text"
    LOG_DIR: str = "logs"
    LOG_FILE: str = os.path.join(LOG_DIR, "app.log")
    LOG_MAX_BYTES: int = 5_000_000  # 5MB
    LOG_BACKUP_COUNT: int = 3
    LOG_STDOUT_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = (
        "WARNING"
    )
    LOG_USER_ACTIONS: Literal["all", "write"] = (
        "write"  # Log all actions or only write operations
    )

    # Metrics settings
    METRICS_ENABLED: bool = True
    METRICS_PREFIX: Optional[str] = None  # Optional prefix for all metrics

    # Tracing settings
    TRACING_ENABLED: bool = True
    TRACING_HEADER: str = "X-Correlation-ID"
    TRACING_GENERATE_IF_MISSING: bool = True
    TRANSACTION_HEADER: str = "X-Transaction-ID"  # Header for transaction grouping

    # Database settings
    DB_TYPE: Literal["sqlite", "postgresql"] = "sqlite"
    DB_URL: str
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    DB_ECHO: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow",  # Allow extra fields in the .env file
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set API_PREFIX based on API_VERSION
        self.API_PREFIX = f"/api/{self.API_VERSION}"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
