
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status


async def get_object_or_404(session: AsyncSession, model, object_id):
    result = await session.execute(select(model).where(model.id == object_id))
    obj = result.scalar_one_or_none()
    if obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{model.__name__} not found")
    return obj
