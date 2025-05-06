from app.api.v1 import get_router
from app.models.asset_type import (
    AssetType,
    AssetTypeCreate,
    AssetTypeFilter,
    AssetTypeRead,
    AssetTypeUpdate,
)
from app.services import GenericService

service = GenericService(AssetType)
router = get_router(
    service=service,
    model_name="asset_type",
    create_schema=AssetTypeCreate,
    update_schema=AssetTypeUpdate,
    read_schema=AssetTypeRead,
    filter_schema=AssetTypeFilter,
)
