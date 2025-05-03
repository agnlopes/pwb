from typing import List, Optional
from uuid import UUID
from sqlmodel import Field, SQLModel, Relationship
from app.models.mixins import UUIDMixin, TimestampMixin
from sqlalchemy import Column, ForeignKey, String


class ETF(UUIDMixin, TimestampMixin, SQLModel, table=True):
    name: str
    symbol: str
    top_holdings: List["TopHolding"] = Relationship(back_populates="etf")


class TopHolding(UUIDMixin, TimestampMixin, SQLModel, table=True):
    symbol: str
    weight: float
    etf_id: UUID = Field(sa_column=Column(String, ForeignKey("etf.id"), nullable=False))
    etf: Optional[ETF] = Relationship(back_populates="top_holdings")

class EtfCreate(SQLModel):
    pass

    model_config = {
        "json_schema_extra": {
            "examples": [
                {'name': 'S&P 500 ETF', 'symbol': 'SPY'}
            ]
        }
    }

class EtfUpdate(SQLModel):
    pass


class EtfRead(SQLModel):
    pass

