from uuid import uuid4, UUID
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field


def utc_now():
    return datetime.now(timezone.utc)

class TimestampMixin(SQLModel):
    created_at: datetime = Field(default_factory=utc_now, nullable=False)
    modified_at: datetime = Field(default_factory=utc_now, nullable=False)

class UUIDMixin(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
