import asyncio

from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.security import get_password_hash
from app.db.session import engine
from app.models.asset import AssetType
from app.models.user import User


async def seed_asset_types(session: AsyncSession):
    result = await session.exec(select(AssetType))
    if result.first():
        return

    for name in ["stock", "crypto", "etf", "cash", "fixed-income", "custom"]:
        session.add(AssetType(name=name))
    await session.commit()

async def seed_root_user(session: AsyncSession):
    result = await session.exec(select(User).where(User.email == "root@localhost"))
    if result.first():
        return

    user = User(
        username="root@localhost",
        email="root@localhost",
        hashed_password=get_password_hash("topsecret123")
    )
    session.add(user)
    await session.commit()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.details.create_all)

    async with AsyncSession(engine) as session:
        await seed_asset_types(session)
        await seed_root_user(session)

if __name__ == "__main__":
    asyncio.run(init_db())
