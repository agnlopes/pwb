from typing import List, Optional
from uuid import UUID

from sqlalchemy import Column, ForeignKey, String
from sqlmodel import Field, Relationship, SQLModel

from app.models.mixins import TimestampMixin, UUIDMixin


class Asset(UUIDMixin, TimestampMixin, SQLModel, table=True):
    symbol: str
    name: str
    price: float
    asset_type_id: UUID = Field(sa_column=Column(String, ForeignKey("assettype.id"), nullable=False))
    asset_type: Optional["AssetType"] = Relationship(back_populates="assets")


class AssetCreate(SQLModel):
    symbol: str
    name: str
    price: float
    asset_type_id: UUID

    model_config = {  # pyright: ignore
        "json_schema_extra": {
            "examples": [
                {'symbol': 'AAPL', 'name': 'Apple Inc.', 'asset_type_id': '11111111-1111-1111-1111-111111111111'}
            ]
        }
    }


class AssetUpdate(SQLModel):
    pass


class AssetRead(SQLModel):
    pass

class AssetType(UUIDMixin, TimestampMixin, SQLModel, table=True):
    name: str
    assets: List["Asset"] = Relationship(back_populates="asset_type")




class AssetTypeCreate(SQLModel):
    name: str
    model_config = {"json_schema_extra": {"examples": [{'name': 'Stock'}]}}  # pyright: ignore


class AssetTypeUpdate(AssetTypeCreate):
    pass


class AssetTypeRead(SQLModel):
    name: str
