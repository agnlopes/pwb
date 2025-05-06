from typing import List, Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.asset_type import (
    AssetType,
    AssetTypeCreate,
    AssetTypeFilter,
    AssetTypeUpdate,
)
from app.services import GenericService


class AssetTypeService(GenericService[AssetType, AssetTypeCreate, AssetTypeUpdate, AssetTypeFilter]):
    """
    Asset Type service for managing asset types.
    Extends the generic service with specific functionality for asset types.
    """

    def __init__(self):
        super().__init__(model=AssetType)

    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[AssetType]:
        """Get an asset type by its name."""
        statement = select(self.model).where(self.model.name == name, self.model.is_active)
        result = await db.exec(statement)
        return result.first()

    async def search_by_name(
        self, db: AsyncSession, name_query: str, skip: int = 0, limit: int = 100
    ) -> List[AssetType]:
        """
        Search asset types by partial name match.
        """
        from sqlalchemy import func

        statement = (
            select(self.model)
            .where(func.lower(self.model.name).contains(func.lower(name_query)), self.model.is_active)
            .offset(skip)
            .limit(limit)
        )

        result = await db.exec(statement)
        return list(result.all())
