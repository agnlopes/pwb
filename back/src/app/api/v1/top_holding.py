from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID
from app.models.etf import TopHolding
from app.db.session import get_session
from app.auth.security import get_current_user
from app.models.user import User
from app.core.config import settings


from app.models.etf import TopHolding
router = APIRouter(prefix="/top_holding", tags=["top_holding"])

@router.get("/", response_model=list[TopHolding])
async def list_top_holdings(
    session: AsyncSession = Depends(get_session()),
    user: User = Depends(get_current_user)
):
    result = await session.exec(select(TopHolding))
    return result.all()

@router.get("/{uid}", response_model=TopHolding)
async def get_top_holding(
    uid: UUID,
    session: AsyncSession = Depends(get_session()),
    user: User = Depends(get_current_user)
):
    top_holding = await session.get(TopHolding, uid)
    if not top_holding:
        raise HTTPException(status_code=404, detail="TopHolding not found")
    return top_holding

@router.post("/", response_model=TopHolding, status_code=201)
async def create_top_holding(
    top_holding: TopHolding,
    session: AsyncSession = Depends(get_session()),
    user: User = Depends(get_current_user)
):
    session.add(top_holding)
    await session.commit()
    await session.refresh(top_holding)
    from app.utils.actions import log_user_action
    await log_user_action(session, user.id, "create", "top_holding", top_holding.id)
    return top_holding

@router.put("/{uid}", response_model=TopHolding)
async def update_top_holding(
    uid: UUID,
    updated: TopHolding,
    session: AsyncSession = Depends(get_session()),
    user: User = Depends(get_current_user)
):
    top_holding = await session.get(TopHolding, uid)
    if not top_holding:
        raise HTTPException(status_code=404, detail="TopHolding not found")
    for key, value in updated.dict(exclude_unset=True).items():
        setattr(top_holding, key, value)
    session.add(top_holding)
    await session.commit()
    await session.refresh(top_holding)
    from app.utils.actions import log_user_action
    await log_user_action(session, user.id, "update", "top_holding", top_holding.id)
    return top_holding

@router.delete("/{uid}", status_code=204)
async def delete_top_holding(
    uid: UUID,
    session: AsyncSession = Depends(get_session()),
    user: User = Depends(get_current_user)
):
    top_holding = await session.get(TopHolding, uid)
    if not top_holding:
        raise HTTPException(status_code=404, detail="TopHolding not found")
    await session.delete(top_holding)
    await session.commit()