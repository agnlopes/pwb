from datetime import datetime, UTC
from typing import Optional
from uuid import UUID

from sqlalchemy import JSON
from sqlmodel import Field, SQLModel


class PortfolioLedger(SQLModel, table=True):
    """Model for tracking changes to portfolios."""

    id: Optional[int] = Field(default=None, primary_key=True)
    portfolio_id: UUID = Field(description="ID of the portfolio that was changed")
    change_type: str = Field(
        description="Type of change (e.g., 'create', 'update', 'delete')"
    )
    details: dict = Field(sa_type=JSON, description="Details about the change")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the change was made",
    )
