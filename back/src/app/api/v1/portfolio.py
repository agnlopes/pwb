from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.security import get_current_user
from app.db.session import get_session
from app.models.portfolio import Portfolio, PortfolioCreate, PortfolioUpdate
from app.models.user import User
from app.services import portfolio as portfolio_service

router = APIRouter(prefix="/Portfolio", tags=["Portfolio"])


@router.post("/", response_model=Portfolio)
async def create_portfolio(
    data: PortfolioCreate,
    session: AsyncSession = Depends(get_session()),
    user: User = Depends(get_current_user),
):
    return await portfolio_service.create(session, user, data)


@router.get("/{uid}", response_model=Portfolio)
async def get_portfolio(
    uid: UUID,
    session: AsyncSession = Depends(get_session()),
    user: User = Depends(get_current_user),
):
    return await portfolio_service.get(session, user, str(uid))


@router.put("/{uid}", response_model=Portfolio)
async def update_portfolio(
    uid: UUID,
    data: PortfolioUpdate,
    session: AsyncSession = Depends(get_session()),
    user: User = Depends(get_current_user),
):
    return await portfolio_service.update(session, user, str(uid), data)


@router.delete("/{uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio(
    uid: UUID,
    session: AsyncSession = Depends(get_session()),
    user: User = Depends(get_current_user),
):
    await portfolio_service.delete(session, user, str(uid))


@router.get("/", response_model=List[Portfolio])
async def list_portfolios(
    session: AsyncSession = Depends(get_session()),
    user: User = Depends(get_current_user),
):
    return await portfolio_service.list_all(session, user)
