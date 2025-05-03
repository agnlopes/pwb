from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID
from app.models.asset import Asset, AssetCreate
from app.db.session import get_session
from app.auth.security import get_current_user
from app.models.user import User


from app.models.asset import Asset
router = APIRouter(prefix="/asset", tags=["asset"])

@router.get("/", response_model=list[Asset])
async def list_assets(
    session: AsyncSession = Depends(get_session()),
    user: User = Depends(get_current_user)
):
    result = await session.exec(select(Asset))
    return result.all()

@router.get("/{uid}", response_model=Asset)
async def get_asset(
    uid: UUID,
    session: AsyncSession = Depends(get_session()),
    user: User = Depends(get_current_user)
):
    asset = await session.get(Asset, uid)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset

@router.post("/", response_model=Asset, status_code=201)
async def create_asset(
    asset: AssetCreate,
    session: AsyncSession = Depends(get_session()),
    user: User = Depends(get_current_user)
):
    new_asset = Asset.from_orm(asset)
    session.add(new_asset)
    await session.commit()
    await session.refresh(new_asset)
    from app.utils.actions import log_user_action
    await log_user_action(session, user.id, "create", "asset", asset.id)
    return new_asset

@router.put("/{uid}", response_model=Asset)
async def update_asset(
    uid: UUID,
    updated: AssetCreate,
    session: AsyncSession = Depends(get_session()),
    user: User = Depends(get_current_user)
):
    asset = await session.get(Asset, uid)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    for key, value in updated.dict(exclude_unset=True).items():
        setattr(asset, key, value)
    session.add(asset)
    await session.commit()
    await session.refresh(asset)
    from app.utils.actions import log_user_action
    await log_user_action(session, user.id, "update", "asset", asset.id)
    return asset

@router.delete("/{uid}", status_code=204)
async def delete_asset(
    uid: UUID,
    session: AsyncSession = Depends(get_session()),
    user: User = Depends(get_current_user)
):
    asset = await session.get(Asset, uid)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    await session.delete(asset)
    await session.commit()