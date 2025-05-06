from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Used for FastAPI
async def get_session():
    async with SessionLocal() as session:
        yield session


# Used for tests or scripts
async def get_session_raw():
    async with SessionLocal() as session:
        return session
