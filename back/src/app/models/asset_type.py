from uuid import UUID

from app.models import (
    GenericCreate,
    GenericFilter,
    GenericListResponse,
    GenericModel,
    GenericRead,
    GenericResponse,
    GenericUpdate,
)


class AssetType(GenericModel, table=True):
    """
    AssetType model
    """

    __tablename__ = "asset_type"

    name: str
    description: str | None = None


class AssetTypeCreate(GenericCreate):
    """
    Create AssetType request
    """

    name: str
    description: str | None = None


class AssetTypeUpdate(GenericUpdate):
    """
    Update AssetType request
    """

    name: str | None = None
    description: str | None = None


class AssetTypeRead(GenericRead):
    """
    Read AssetType response
    """

    id: UUID
    name: str
    description: str | None = None


class AssetTypeResponse(GenericResponse):
    """
    AssetType response
    """

    data: AssetTypeRead


class AssetTypeListResponse(GenericListResponse):
    """
    AssetType list response
    """

    data: list[AssetTypeRead]
    total: int
    page: int = 1


class AssetTypeFilter(GenericFilter):
    """
    AssetType filter
    """

    name: str | None = None
    description: str | None = None
    page: int = 1
    limit: int = 10
