from typing import List, Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy import func
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.security import get_current_user
from app.db.session import get_session
from app.models.asset_type import (AssetType, AssetTypeCreate, AssetTypeFilter,
                                   AssetTypeRead, AssetTypeUpdate)
from app.models.user import User
from app.services import GenericService


class AssetTypeService(
    GenericService[AssetType, AssetTypeCreate, AssetTypeUpdate, AssetTypeFilter]
):
    """
    Asset Type service for managing asset types.
    Extends the generic service with specific functionality for asset types.
    """

    def __init__(self, model: type[AssetType] = AssetType):
        super().__init__(model=model)

    async def get_by_name(
        self,
        name: str,
        db: AsyncSession = Depends(get_session),
        user: User = Depends(get_current_user),
    ) -> AssetTypeRead:
        """Get an asset type by its name."""
        statement = select(self.model).where(
            func.lower(self.model.name).like(func.lower(f"%{name}%")),
            self.model.is_active,
        )
        result = await db.exec(statement)
        asset_type = result.first()

        if not asset_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asset type with name {name} not found",
            )
        return asset_type
