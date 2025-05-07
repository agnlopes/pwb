from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1 import GenericRouter
from app.auth.security import get_current_user
from app.db.session import get_session
from app.models.asset_type import (AssetType, AssetTypeCreate, AssetTypeFilter,
                                   AssetTypeRead, AssetTypeUpdate)
from app.models.user import User
from app.services.asset_type import AssetTypeService

service = AssetTypeService(AssetType)

router = GenericRouter(
    service=service,
    model_name="asset_type",
    create_schema=AssetTypeCreate,
    update_schema=AssetTypeUpdate,
    read_schema=AssetTypeRead,
    filter_schema=AssetTypeFilter,
)

router.add_custom_route(
    path="/by_name/{name}",
    method="get",
    response_model=AssetTypeRead,
    handler=service.get_by_name,
)
