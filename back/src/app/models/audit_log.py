from datetime import datetime, UTC
from typing import Optional
from uuid import UUID

from sqlalchemy import JSON
from sqlmodel import Field, SQLModel


class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_log"
    """Model for tracking user actions and system events."""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(description="ID of the user who performed the action")
    action: str = Field(description="The action performed")
    target_type: str = Field(
        description="Type of the target object (e.g., 'user', 'portfolio')"
    )
    target_id: UUID = Field(description="ID of the target object")
    details: Optional[dict] = Field(
        default=None, sa_type=JSON, description="Additional details about the action"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the action was performed",
    )
