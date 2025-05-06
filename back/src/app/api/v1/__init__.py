from typing import Callable, Generic, Optional, Type, TypeVar
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.security import get_current_user
from app.db.session import get_session
from app.models import (
    GenericCreate,
    GenericFilter,
    GenericListResponse,
    GenericRead,
    GenericResponse,
    GenericUpdate,
)
from app.models.user import User
from app.services import GenericService

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=GenericCreate)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=GenericUpdate)
FilterSchemaType = TypeVar("FilterSchemaType", bound=GenericFilter)
ReadSchemaType = TypeVar("ReadSchemaType", bound=GenericRead)


def get_router(
    *,
    service: GenericService,
    model_name: str,
    create_schema: Type[CreateSchemaType],
    update_schema: Type[UpdateSchemaType],
    read_schema: Type[ReadSchemaType],
    filter_schema: Type[FilterSchemaType],
) -> APIRouter:
    router = APIRouter(prefix=f"/{model_name}", tags=[model_name.title().replace("_", " ")])

    @router.post("/", response_model=GenericResponse[read_schema])
    async def create_item(
        obj_in: create_schema,
        db: AsyncSession = Depends(get_session),
        user: User = Depends(get_current_user)
    ):
        obj = await service.create(db, obj_in)
        return GenericResponse(data=obj)

    @router.get("/{uid}", response_model=GenericResponse[read_schema])
    async def get_item(
        item_id: UUID,
        db: AsyncSession = Depends(get_session),
        user: User = Depends(get_current_user)
    ):
        obj = await service.get_by_id(db, item_id)
        return GenericResponse(data=obj)

    @router.post("/list", response_model=GenericListResponse[read_schema])
    async def list_items(
        filters: filter_schema,
        db: AsyncSession = Depends(get_session),
        user: User = Depends(get_current_user)
    ):
        skip = (filters.page - 1) * filters.page_size
        items = await service.get_all(
            db,
            filters=filters,
            skip=skip,
            limit=filters.page_size,
            sort_by=filters.sort_by,
            sort_order=filters.sort_order or "asc",
        )
        total = await service.count(db, filters=filters)
        return GenericListResponse(items=items, total=total, page=filters.page, page_size=filters.page_size)

    @router.put("/{uid}", response_model=GenericResponse[read_schema])
    async def update_item(
        item_id: UUID,
        obj_in: update_schema,
        db: AsyncSession = Depends(get_session),
        user: User = Depends(get_current_user)
    ):
        obj = await service.update(db, item_id, obj_in)
        return GenericResponse(data=obj)

    @router.delete("/{uid}", response_model=GenericResponse[read_schema])
    async def delete_item(
        item_id: UUID,
        hard_delete: bool = Query(False),
        db: AsyncSession = Depends(get_session),
        user: User = Depends(get_current_user)
    ):
        obj = await service.delete(db, item_id, hard_delete)
        return GenericResponse(data=obj)

    @router.put("/{uid}/restore", response_model=GenericResponse[read_schema])
    async def restore_item(
        item_id: UUID,
        db: AsyncSession = Depends(get_session),
        user: User = Depends(get_current_user)
    ):
        obj = await service.restore(db, item_id)
        return GenericResponse(data=obj)

    return router
