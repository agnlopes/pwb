from typing import Callable, Generic, Optional, Type, TypeVar, List
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
from app.utils.logging import log_user_action

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=GenericCreate)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=GenericUpdate)
FilterSchemaType = TypeVar("FilterSchemaType", bound=GenericFilter)
ReadSchemaType = TypeVar("ReadSchemaType", bound=GenericRead)


class GenericRouter(APIRouter, Generic[ModelType, CreateSchemaType, UpdateSchemaType, FilterSchemaType, ReadSchemaType]):
    """
    Generic router class that provides CRUD operations for any model.
    """

    def __init__(
        self,
        *,
        service: GenericService,
        model_name: str,
        create_schema: Type[CreateSchemaType],
        update_schema: Type[UpdateSchemaType],
        read_schema: Type[ReadSchemaType],
        filter_schema: Type[FilterSchemaType],
    ):
        super().__init__(prefix=f"/{model_name}", tags=[model_name.title().replace("_", " ")])
        self.service = service
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.read_schema = read_schema
        self.filter_schema = filter_schema
        self.model_name = model_name

        # Register routes
        self._register_crud_routes()
        self._register_custom_routes()

    def _register_crud_routes(self):
        """Register standard CRUD routes."""
        self._register_create_route()
        self._register_get_route()
        self._register_list_route()
        self._register_search_route()
        self._register_update_route()
        self._register_patch_route()
        self._register_delete_route()
        self._register_restore_route()

    def _register_custom_routes(self):
        """Register custom routes. Override this method in subclasses to add custom routes."""
        pass

    def _register_create_route(self):
        @self.post("/", response_model=GenericResponse[self.read_schema])
        async def create_item(
            obj_in: self.create_schema,
            db: AsyncSession = Depends(get_session),
            user: User = Depends(get_current_user)
        ):
            obj = await self.service.create(db, obj_in)
            await log_user_action(
                session=db,
                user_id=user.id,
                action="create",
                method="POST",
                path=f"/{self.model_name}/",
                target_type=self.model_name,
                target_id=obj.id,
                details={"data": obj_in.dict()},
            )
            return GenericResponse(data=obj)

    def _register_get_route(self):
        @self.get("/{uid}", response_model=GenericResponse[self.read_schema])
        async def get_item(
            item_id: UUID,
            db: AsyncSession = Depends(get_session),
            user: User = Depends(get_current_user)
        ):
            obj = await self.service.get_by_id(db, item_id)
            await log_user_action(
                session=db,
                user_id=user.id,
                action="get",
                method="GET",
                path=f"/{self.model_name}/{item_id}",
                target_type=self.model_name,
                target_id=item_id,
            )
            return GenericResponse(data=obj)

    def _register_list_route(self):
        @self.get("/", response_model=GenericListResponse[self.read_schema])
        async def list_items(
            page: int = Query(1, ge=1),
            page_size: int = Query(10, ge=1, le=100),
            sort_by: str | None = None,
            sort_order: str = "asc",
            db: AsyncSession = Depends(get_session),
            user: User = Depends(get_current_user)
        ):
            """List all items with basic pagination and sorting."""
            skip = (page - 1) * page_size
            items = await self.service.get_all(
                db,
                skip=skip,
                limit=page_size,
                sort_by=sort_by,
                sort_order=sort_order,
            )
            total = await self.service.count(db)
            await log_user_action(
                session=db,
                user_id=user.id,
                action="list",
                method="GET",
                path=f"/{self.model_name}/",
                target_type=self.model_name,
                details={
                    "page": page,
                    "page_size": page_size,
                    "sort_by": sort_by,
                    "sort_order": sort_order,
                    "total": total,
                },
            )
            return GenericListResponse(items=items, total=total, page=page, page_size=page_size)

    def _register_search_route(self):
        @self.post("/search", response_model=GenericListResponse[self.read_schema])
        async def search_items(
            filters: self.filter_schema = Depends(),
            db: AsyncSession = Depends(get_session),
            user: User = Depends(get_current_user)
        ):
            """Search items with filtering, pagination, and sorting."""
            skip = (filters.page - 1) * filters.page_size
            items = await self.service.get_all(
                db,
                filters=filters,
                skip=skip,
                limit=filters.page_size,
                sort_by=filters.sort_by,
                sort_order=filters.sort_order or "asc",
            )
            total = await self.service.count(db, filters=filters)
            await log_user_action(
                session=db,
                user_id=user.id,
                action="search",
                method="POST",
                path=f"/{self.model_name}/search",
                target_type=self.model_name,
                details={
                    "filters": filters.dict(),
                    "total": total,
                },
            )
            return GenericListResponse(items=items, total=total, page=filters.page, page_size=filters.page_size)

    def _register_update_route(self):
        @self.put("/{uid}", response_model=GenericResponse[self.read_schema])
        async def update_item(
            item_id: UUID,
            obj_in: self.update_schema,
            db: AsyncSession = Depends(get_session),
            user: User = Depends(get_current_user)
        ):
            obj = await self.service.update(db, item_id, obj_in)
            await log_user_action(
                session=db,
                user_id=user.id,
                action="update",
                method="PUT",
                path=f"/{self.model_name}/{item_id}",
                target_type=self.model_name,
                target_id=item_id,
                details={"data": obj_in.dict()},
            )
            return GenericResponse(data=obj)

    def _register_patch_route(self):
        @self.patch("/{uid}", response_model=GenericResponse[self.read_schema])
        async def patch_item(
            item_id: UUID,
            obj_in: self.update_schema,
            db: AsyncSession = Depends(get_session),
            user: User = Depends(get_current_user)
        ):
            obj = await self.service.patch(db, item_id, obj_in)
            await log_user_action(
                session=db,
                user_id=user.id,
                action="patch",
                method="PATCH",
                path=f"/{self.model_name}/{item_id}",
                target_type=self.model_name,
                target_id=item_id,
                details={"data": obj_in.dict()},
            )
            return GenericResponse(data=obj)

    def _register_delete_route(self):
        @self.delete("/{uid}", response_model=GenericResponse[self.read_schema])
        async def delete_item(
            item_id: UUID,
            hard_delete: bool = Query(False),
            db: AsyncSession = Depends(get_session),
            user: User = Depends(get_current_user)
        ):
            obj = await self.service.delete(db, item_id, hard_delete)
            await log_user_action(
                session=db,
                user_id=user.id,
                action="delete",
                method="DELETE",
                path=f"/{self.model_name}/{item_id}",
                target_type=self.model_name,
                target_id=item_id,
                details={"hard_delete": hard_delete},
            )
            return GenericResponse(data=obj)

    def _register_restore_route(self):
        @self.put("/{uid}/restore", response_model=GenericResponse[self.read_schema])
        async def restore_item(
            item_id: UUID,
            db: AsyncSession = Depends(get_session),
            user: User = Depends(get_current_user)
        ):
            obj = await self.service.restore(db, item_id)
            await log_user_action(
                session=db,
                user_id=user.id,
                action="restore",
                method="PUT",
                path=f"/{self.model_name}/{item_id}/restore",
                target_type=self.model_name,
                target_id=item_id,
            )
            return GenericResponse(data=obj)

    def add_custom_route(
        self,
        path: str,
        method: str,
        response_model: Type,
        handler: Callable,
        **kwargs
    ):
        """Add a custom route to the router."""
        route_method = getattr(self, method.lower())
        route_method(path, response_model=response_model, **kwargs)(handler)