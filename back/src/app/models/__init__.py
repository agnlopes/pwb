from datetime import datetime, timezone
from typing import ClassVar, Generic, List, Optional, TypeVar
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

# Type variable for the model
T = TypeVar("T")


def utc_now() -> datetime:
    """Get the current UTC time."""
    return datetime.now(timezone.utc)


class IdMixin(SQLModel):
    """Mixin for models with UUID primary key."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)


class TimestampMixin(SQLModel):
    """Mixin for models with created_at and modified_at timestamps."""

    created_at: datetime = Field(default_factory=utc_now, nullable=False)
    modified_at: datetime = Field(default_factory=utc_now, nullable=False)


class GenericModel(IdMixin, TimestampMixin, SQLModel):
    """Base SQLModel with common fields for all models."""

    __tablename__: ClassVar[Optional[str]] = None
    is_active: bool = Field(default=True)


# Generic schemas for CRUD operations
class GenericCreate(SQLModel):
    """Generic schema for creating resources."""

    pass


class GenericRead(SQLModel):
    """Generic schema for reading resources."""

    id: UUID
    created_at: datetime
    modified_at: datetime
    is_active: bool


class GenericUpdate(SQLModel):
    """Generic schema for updating resources."""

    modified_at: datetime = Field(default_factory=utc_now)
    is_active: Optional[bool] = None


class GenericResponse(SQLModel, Generic[T]):
    """Generic schema for single item responses."""

    data: T
    message: str = "Success"


class GenericListResponse(SQLModel, Generic[T]):
    """Generic schema for list responses."""

    items: List[T]
    total: int
    page: int = 1
    page_size: int = 100
    message: str = "Success"


class GenericFilter(SQLModel):
    """Generic schema for filtering resources."""

    is_active: Optional[bool] = None
    page: int = 1
    page_size: int = 100
    sort_by: Optional[str] = None
    sort_order: Optional[str] = "asc"
