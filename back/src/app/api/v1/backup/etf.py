from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID
from app.models.etf import ETF
from app.db.session import get_session
from app.models.user import User
from app.auth.security import get_current_user
from app.core.config import settings


from app.models.etf import ETF
router = APIRouter(prefix="/etf", tags=["etf"])

@router.get("/", response_model=list[ETF])
async def list_etfs(session: AsyncSession = Depends(get_session()), user: User = Depends(get_current_user)):
    result = await session.exec(select(ETF))
    return result.all()

@router.get("/{uid}", response_model=ETF)
async def get_etf(uid: UUID, session: AsyncSession = Depends(get_session()), user: User = Depends(get_current_user)):
    etf = await session.get(ETF, uid)
    if not etf:
        raise HTTPException(status_code=404, detail="ETF not found")
    return etf

@router.post("/", response_model=ETF, status_code=201)
async def create_etf(etf: ETF, session: AsyncSession = Depends(get_session()), user: User = Depends(get_current_user)):
    session.add(etf)
    await session.commit()
    await session.refresh(etf)
    from app.utils.actions import log_user_action
    await log_user_action(session, user.id, "create", "etf", etf.id)
    return etf

@router.put("/{uid}", response_model=ETF)
async def update_etf(uid: UUID, updated: ETF, session: AsyncSession = Depends(get_session()), user: User = Depends(get_current_user)):
    etf = await session.get(ETF, uid)
    if not etf:
        raise HTTPException(status_code=404, detail="ETF not found")
    for key, value in updated.dict(exclude_unset=True).items():
        setattr(etf, key, value)
    session.add(etf)
    await session.commit()
    await session.refresh(etf)
    from app.utils.actions import log_user_action
    await log_user_action(session, user.id, "update", "etf", etf.id)
    return etf

@router.delete("/{uid}", status_code=204)
async def delete_etf(uid: UUID, session: AsyncSession = Depends(get_session()), user: User = Depends(get_current_user)):
    etf = await session.get(ETF, uid)
    if not etf:
        raise HTTPException(status_code=404, detail="ETF not found")
    await session.delete(etf)
    await session.commit()