from typing import List
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from app.models.mixins import TimestampMixin, UUIDMixin


class User(UUIDMixin, TimestampMixin, SQLModel, table=True):
    username: str = Field(index=True, nullable=False)
    email: str = Field(index=True, nullable=False, unique=True)
    hashed_password: str
    portfolios: List["Portfolio"] = Relationship(back_populates="user")


class UserCreate(SQLModel):
    username: str
    email: str
    password: str

    model_config = { #pyright ignore
        "json_schema_extra": {
            "examples": [{'username': 'johndoe', 'email': 'johndoe@example.com', 'password': 'supersecret123'}]
        }
    }


class UserUpdate(UserCreate):
    pass


class UserRead(SQLModel):
    id: UUID
    username: str
    email: str
