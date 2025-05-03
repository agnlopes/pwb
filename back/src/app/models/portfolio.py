from typing import List, Optional
from uuid import UUID

from sqlalchemy import Column, ForeignKey, String
from sqlmodel import Field, Relationship, SQLModel

from app.models.mixins import TimestampMixin, UUIDMixin


class Portfolio(UUIDMixin, TimestampMixin, SQLModel, table=True):
    name: str
    user_id: UUID = Field(sa_column=Column(String, ForeignKey("user.id"), nullable=False))
    user: Optional["User"] = Relationship(back_populates="portfolios")
    holdings: List["Holding"] = Relationship(back_populates="portfolio")


class PortfolioCreate(SQLModel):
    name: str
    user_id: UUID

    model_config = {  # pyright: ignore
        "json_schema_extra": {"examples": [{'name': 'My Portfolio', 'user_id': '22222222-2222-2222-2222-222222222222'}]}
    }


class PortfolioUpdate(SQLModel):
    pass


class PortfolioRead(SQLModel):
    id: UUID
    name: str
    user_id: UUID
