from typing import Optional, List
from uuid import UUID
from sqlmodel import Field, SQLModel, Relationship
from app.models.mixins import UUIDMixin, TimestampMixin
from sqlalchemy import Column, ForeignKey, String


class Holding(UUIDMixin, TimestampMixin, SQLModel, table=True):
    quantity: float
    portfolio_id: UUID = Field(sa_column=Column(String, ForeignKey("portfolio.id"), nullable=False))
    asset_id: UUID = Field(sa_column=Column(String, ForeignKey("asset.id"), nullable=False))
    portfolio: Optional["Portfolio"] = Relationship(back_populates="holdings")
    asset: Optional["Asset"] = Relationship()

class HoldingCreate(SQLModel):
    pass

    model_config = {
        "json_schema_extra": {
            "examples": [
                {'quantity': 10, 'portfolio_id': '33333333-3333-3333-3333-333333333333', 'asset_id': '44444444-4444-4444-4444-444444444444'}
            ]
        }
    }

class HoldingUpdate(SQLModel):
    pass


class HoldingRead(SQLModel):
    pass

