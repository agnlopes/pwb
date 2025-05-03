from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID
from app.models.holding import Holding
from app.db.session import get_session
from app.auth.security import get_current_user
from app.models.user import User
from app.core.config import settings


from app.models.holding import Holding
router = APIRouter(prefix="/holding", tags=["holding"])

@router.get("/", response_model=list[Holding])
async def list_holdings(
    session: AsyncSession = Depends(get_session()),
    user: User = Depends(get_current_user)
):
    result = await session.exec(select(Holding))
    return result.all()

@router.get("/{uid}", response_model=Holding)
async def get_holding(
    uid: UUID,
    session: AsyncSession = Depends(get_session()),
    user: User = Depends(get_current_user)
):
    holding = await session.get(Holding, uid)
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")
    return holding

@router.post("/", response_model=Holding, status_code=201)
async def create_holding(
    holding: Holding,
    session: AsyncSession = Depends(get_session()),
    user: User = Depends(get_current_user)
):
    session.add(holding)
    await session.commit()
    await session.refresh(holding)
    from app.utils.actions import log_user_action
    await log_user_action(session, user.id, "create", "holding", holding.id)
    return holding

@router.put("/{uid}", response_model=Holding)
async def update_holding(
    uid: UUID,
    updated: Holding,
    session: AsyncSession = Depends(get_session()),
    user: User = Depends(get_current_user)
):
    holding = await session.get(Holding, uid)
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")
    for key, value in updated.dict(exclude_unset=True).items():
        setattr(holding, key, value)
    session.add(holding)
    await session.commit()
    await session.refresh(holding)
    from app.utils.actions import log_user_action
    await log_user_action(session, user.id, "update", "holding", holding.id)
    return holding

@router.delete("/{uid}", status_code=204)
async def delete_holding(
    uid: UUID,
    session: AsyncSession = Depends(get_session()),
    user: User = Depends(get_current_user)
):
    holding = await session.get(Holding, uid)
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")
    await session.delete(holding)
    await session.commit()