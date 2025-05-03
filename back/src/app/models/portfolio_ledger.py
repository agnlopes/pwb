from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.sqlite import JSON
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

class PortfolioLedger(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    portfolio_id: UUID = Field(foreign_key="portfolio.id")
    change_type: str  # e.g. "adjust_holding", "rebalance"
    details: str = Field(default="{}")  # JSON describing the change
    timestamp: datetime = Field(default_factory=datetime.utcnow)
