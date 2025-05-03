from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.security import get_current_user
from app.db.session import get_session
from app.models.asset import AssetType, AssetTypeCreate, AssetTypeUpdate
from app.models.user import User
from app.services import asset_type as asset_type_service

router = APIRouter(prefix="/asset-type", tags=["Asset Type"])


@router.post("/", response_model=AssetType)
async def create_asset_type(
    data: AssetTypeCreate,
    session: AsyncSession = Depends(get_session()),
    user: User = Depends(get_current_user),
):
    return await asset_type_service.create(session, user, data)


@router.get("/{uid}", response_model=AssetType)
async def get_asset_type(
    uid: UUID,
    session: AsyncSession = Depends(get_session()),
    user: User = Depends(get_current_user),
):
    return await asset_type_service.get(session, user, str(uid))


@router.put("/{uid}", response_model=AssetType)
async def update_asset_type(
    uid: UUID,
    data: AssetTypeUpdate,
    session: AsyncSession = Depends(get_session()),
    user: User = Depends(get_current_user),
):
    return await asset_type_service.update(session, user, str(uid), data)


@router.delete("/{uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset_type(
    uid: UUID,
    session: AsyncSession = Depends(get_session()),
    user: User = Depends(get_current_user),
):
    await asset_type_service.delete(session, user, str(uid))


@router.get("/", response_model=List[AssetType])
async def list_asset_types(
    session: AsyncSession = Depends(get_session()),
    user: User = Depends(get_current_user),
):
    return await asset_type_service.list_all(session, user)
