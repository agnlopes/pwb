from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID
from app.models.portfolio import Portfolio
from app.db.session import get_session
from app.auth.security import get_current_user
from app.models.user import User

from app.models.portfolio import Portfolio
router = APIRouter(prefix="/portfolio", tags=["Portfolio"])

@router.get("/{uid}", response_model=Portfolio)
async def get_portfolio(
    uid: UUID,
    session: AsyncSession = Depends(get_session()),
    user: User = Depends(get_current_user)
):
    portfolio = await session.get(Portfolio, uid)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio

@router.get("/", response_model=list[Portfolio])
async def list_portfolios(
    session: AsyncSession = Depends(get_session()),
    user: User = Depends(get_current_user)
):
    result = await session.exec(select(Portfolio))
    return result.all()


@router.post("/", response_model=Portfolio, status_code=201)
async def create_portfolio(
    portfolio: Portfolio,
    session: AsyncSession = Depends(get_session()),
    user: User = Depends(get_current_user)
):
    session.add(portfolio)
    await session.commit()
    await session.refresh(portfolio)
    from app.utils.actions import log_user_action
    await log_user_action(session, user.id, "create", "portfolio", portfolio.id)
    return portfolio

@router.put("/{uid}", response_model=Portfolio)
async def update_portfolio(
    uid: UUID,
    updated: Portfolio,
    session: AsyncSession = Depends(get_session()),
    user: User = Depends(get_current_user)
):
    portfolio = await session.get(Portfolio, uid)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    for key, value in updated.dict(exclude_unset=True).items():
        setattr(portfolio, key, value)
    session.add(portfolio)
    await session.commit()
    await session.refresh(portfolio)
    from app.utils.actions import log_user_action, record_portfolio_change
    await log_user_action(session, user.id, "update", "portfolio", portfolio.id)
    await record_portfolio_change(session, portfolio.id, "update", { "name": portfolio.name })
    return portfolio

@router.delete("/{uid}", status_code=204)
async def delete_portfolio(
    uid: UUID,
    session: AsyncSession = Depends(get_session()),
    user: User = Depends(get_current_user)
):
    portfolio = await session.get(Portfolio, uid)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    await session.delete(portfolio)
    await session.commit()
