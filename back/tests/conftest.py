import asyncio
import os
from typing import AsyncGenerator

import pytest
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.testclient import TestClient

from app.core.config import settings
from app.db.session import SessionLocal
from app.main import app

# Ensure tests use SQLite
os.environ["DATABASE_TYPE"] = "sqlite"
os.environ["SQLITE_DB"] = "sqlite+aiosqlite:///./test.db"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_db():
    """Create a test database session."""
    session = SessionLocal()
    try:
        # Create all tables
        await session.run_sync(SQLModel.metadata.create_all)
        yield session
    finally:
        # Drop all tables
        await session.run_sync(SQLModel.metadata.drop_all)
        await session.close()


@pytest.fixture
async def db_session(test_db: AsyncSession) -> AsyncSession:
    """Create a database session for testing."""
    session = SessionLocal()
    try:
        yield session
    finally:
        await session.rollback()
        await session.close()


@pytest.fixture
def client() -> TestClient:
    """Create a test client."""
    return TestClient(app) 