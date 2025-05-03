from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings


engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

def get_session():
    async def _get_session():
        async with SessionLocal() as session:
            yield session
    return _get_session
