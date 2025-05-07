from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import String, cast

from app.models import GenericFilter, GenericModel

T = TypeVar("T", bound=GenericModel)

CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=SQLModel)
FilterSchemaType = TypeVar("FilterSchemaType", bound=GenericFilter)


class GenericService(Generic[T, CreateSchemaType, UpdateSchemaType, FilterSchemaType]):
    """
    Generic service class that provides CRUD operations for any model.
    """

    def __init__(self, model: Type[T]):
        self.model = model

    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> T:
        """Create a new instance of the model."""
        obj_data = obj_in.model_dump(exclude_unset=True)
        db_obj = self.model(**obj_data)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        return db_obj

    async def get_by_id(self, db: AsyncSession, obj_id: UUID) -> Optional[T]:
        """Get an instance of the model by ID."""
        statement = select(self.model).where(self.model.id == obj_id, self.model.is_active)
        result = await db.exec(statement)
        db_obj = result.first()

        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"{self.model.__name__} with ID {obj_id} not found"
            )
        return db_obj

    async def get_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        filters: Optional[FilterSchemaType] = None,
    ) -> List[T]:
        """Get all instances of the model with pagination, sorting, and filtering."""
        statement = select(self.model).where(self.model.is_active)

        # Apply filters if provided
        if filters:
            filter_data = filters.model_dump(exclude_unset=True, exclude_none=True)
            # Remove pagination and sorting params from filter data
            filter_data.pop("page", None)
            filter_data.pop("page_size", None)
            filter_data.pop("sort_by", None)
            filter_data.pop("sort_order", None)

            for field_name, value in filter_data.items():
                if hasattr(self.model, field_name):
                    field = getattr(self.model, field_name)
                    # For string fields, use LIKE for substring search
                    if isinstance(value, str):
                        statement = statement.where(cast(field, String).ilike(f"%{value}%"))
                    else:
                        statement = statement.where(field == value)

        # Apply sorting
        sort_field = sort_by if sort_by and hasattr(self.model, sort_by) else "id"
        if sort_order.lower() == "desc":
            statement = statement.order_by(getattr(self.model, sort_field).desc())
        else:
            statement = statement.order_by(getattr(self.model, sort_field).asc())

        # Apply pagination
        statement = statement.offset(skip).limit(limit)
        result = await db.exec(statement)
        return list(result.all())

    async def count(self, db: AsyncSession, filters: Optional[FilterSchemaType] = None) -> int:
        """Count all instances of the model with filtering."""
        statement = select(self.model).where(self.model.is_active)

        # Apply filters if provided
        if filters:
            filter_data = filters.model_dump(exclude_unset=True, exclude_none=True)
            # Remove pagination and sorting params from filter data
            filter_data.pop("page", None)
            filter_data.pop("page_size", None)
            filter_data.pop("sort_by", None)
            filter_data.pop("sort_order", None)

            for field_name, value in filter_data.items():
                if hasattr(self.model, field_name):
                    field = getattr(self.model, field_name)
                    # For string fields, use LIKE for substring search
                    if isinstance(value, str):
                        statement = statement.where(cast(field, String).ilike(f"%{value}%"))
                    else:
                        statement = statement.where(field == value)

        result = await db.exec(statement)
        return len(result.all())

    async def update(self, db: AsyncSession, obj_id: UUID, obj_in: Union[UpdateSchemaType, Dict[str, Any]]) -> Optional[T]:
        """Update an instance of the model."""
        # Get current object
        db_obj = await self.get_by_id(db, obj_id)

        # Convert input to dict if it's not already
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        # Update the object attributes
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        return db_obj

    async def delete(self, db: AsyncSession, obj_id: UUID, hard_delete: bool = False) -> Optional[T]:
        """
        Delete an instance of the model.
        By default, this is a soft delete (setting is_active=False).
        Set hard_delete=True to permanently remove from database.
        """
        db_obj = await self.get_by_id(db, obj_id)

        if hard_delete:
            await db.delete(db_obj)
        else:
            setattr(db_obj, "is_active", False)
            db.add(db_obj)

        await db.commit()
        return db_obj

    async def restore(self, db: AsyncSession, obj_id: UUID) -> T:
        """Restore a soft-deleted instance of the model."""
        # Custom query to find inactive object
        statement = select(self.model).where(self.model.id == obj_id, not self.model.is_active)
        result = await db.exec(statement)
        db_obj = result.first()

        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inactive {self.model.__name__} with ID {obj_id} not found",
            )

        setattr(db_obj, "is_active", True)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        return db_obj
