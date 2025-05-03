import pytest_asyncio
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from app.main import app

@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(base_url="http://test", transport=transport) as client:
        yield client

import pytest_asyncio
from sqlmodel import SQLModel
from app.db.session import engine

@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.details.create_all)
