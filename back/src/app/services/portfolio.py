from typing import List
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.portfolio import Portfolio, PortfolioCreate, PortfolioUpdate
from app.models.user import User
from app.services.base import get_object_or_404
from app.utils.logging import log_user_action


async def get(session: AsyncSession, user: User, uid: str) -> Portfolio:
    obj = await get_object_or_404(session, Portfolio, uid)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")
    await log_user_action(session, user.id, "get", "portfolio", obj.id, obj.model_dump())
    return obj


async def list_all(session: AsyncSession, user: User) -> List[Portfolio]:
    result = await session.exec(select(Portfolio))
    objs = result.all()
    await log_user_action(session, user.id, "list_all", "portfolio", None, None) 
    return list(objs)

async def create(session: AsyncSession, user: User, data: PortfolioCreate) -> Portfolio:
    obj = Portfolio(**data.model_dump(), id=uuid4())
    await session.commit()
    await session.refresh(obj)
    await log_user_action(session, user.id, "create", "portfolio", obj.id, obj.model_dump())
    return obj


async def update(session: AsyncSession, user: User, uid: str, data: PortfolioUpdate) -> Portfolio:
    obj = await get_object_or_404(session, Portfolio, uid)
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
    details_dict = obj.model_dump().update(changes)
    await log_user_action(session, user.id, "update", "portfolio", obj.id, details_dict)
    return obj


async def delete(session: AsyncSession, user: User, uid: str) -> None:
    obj = await get_object_or_404(session, Portfolio, uid)
    await session.delete(obj)
    await session.commit()
    await log_user_action(session, user.id, "delete", "portfolio", obj.id, obj.model_dump())
