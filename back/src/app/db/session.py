from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from app.config import settings

# Create async engine
engine = create_async_engine(settings.DB_URL, echo=True, future=True)

# Create async session factory
SessionLocal = AsyncSession

async def get_session() -> AsyncSession:
    """Get a database session."""
    async with SessionLocal(engine) as session:
        yield session

async def get_session_raw() -> AsyncSession:
    """Get a raw database session without dependency injection."""
    return SessionLocal(engine)
