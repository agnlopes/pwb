from typing import List
from uuid import uuid4

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.asset import AssetType, AssetTypeCreate, AssetTypeUpdate
from app.models.user import User
from app.services.base import get_object_or_404
from app.utils.logging import log_activity


async def get(session: AsyncSession, user: User, uid: str) -> AssetType:
    obj = await get_object_or_404(session, AssetType, uid)
    await log_activity(session, user, "get", "asset_type", obj.id, f"Get asset_type {obj.name}", obj.model_dump())
    return obj


async def list_all(session: AsyncSession, user: User) -> List[AssetType]:
    result = await session.exec(select(AssetType))
    objs = result.all()
    await log_activity(session, user, "list_all", "asset_type", None, "List all asset_types")
    return list(objs)


async def create(session: AsyncSession, user: User, data: AssetTypeCreate) -> AssetType:
    obj = AssetType(**data.model_dump(), id=uuid4())
    await session.commit()
    await session.refresh(obj)
    await log_activity(session, user, "create", "asset_type", obj.id, f"Create asset_type {obj.name}", obj.model_dump())
    return obj


async def update(session: AsyncSession, user: User, uid: str, data: AssetTypeUpdate) -> AssetType:
    obj = await get_object_or_404(session, AssetType, uid)
    update_data = data.model_dump(exclude_unset=True)
    changes = {
        "from": {key: getattr(obj, key) for key in update_data.keys()},
        "to": update_data,
    }
    for key, value in update_data.items():
        setattr(obj, key, value)
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    await log_activity(session, user, "update", "asset_type", obj.id, f"Update asset_type {obj.name}", changes)
    return obj


async def delete(session: AsyncSession, user: User, uid: str) -> None:
    obj = await get_object_or_404(session, AssetType, uid)
    await session.delete(obj)
    await session.commit()
    await log_activity(session, user, "delete", "asset_type", obj.id, f"Delete asset_type {obj.name}", obj.model_dump())
