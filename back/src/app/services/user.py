from typing import List
from uuid import uuid4

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.user import User, UserCreate, UserUpdate
from app.services.base import get_object_or_404
from app.utils.logging import log_activity


async def get(session: AsyncSession, user: User, uid: str) -> User:
    obj = await get_object_or_404(session, User, uid)
    await log_activity(session, user, "get", "user", obj.id, f"Get user {obj.id}", obj.model_dump())
    return obj


async def list_all(session: AsyncSession, user: User) -> List[User]:
    result = await session.exec(select(User))
    objs = result.all()
    await log_activity(session, user, "list_all", "user", None, "List all users")
    return list(objs)


async def create(session: AsyncSession, user: User, data: UserCreate) -> User:
    obj = User(**data.model_dump(), id=uuid4())
    await session.commit()
    await session.refresh(obj)
    await log_activity(
        session, user, "create", "user", obj.id, f"Create user {obj.username} ({obj.email})", obj.model_dump()
    )
    return obj


async def update(session: AsyncSession, user: User, uid: str, data: UserUpdate) -> User:
    obj = await get_object_or_404(session, User, uid)
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
    await log_activity(session, user, "update", "user", obj.id, "Update user {obj.username}", changes)
    return obj


async def delete(session: AsyncSession, user: User, uid: str) -> None:
    obj = await get_object_or_404(session, User, uid)
    await session.delete(obj)
    await session.commit()
    await log_activity(session, user, "delete", "user", obj.id, f" Delete user {obj.name}", obj.model_dump())
