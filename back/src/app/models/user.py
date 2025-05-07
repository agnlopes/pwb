from uuid import UUID

from sqlmodel import Field

from app.models import (GenericCreate, GenericFilter, GenericListResponse,
                        GenericModel, GenericRead, GenericResponse,
                        GenericUpdate)


class User(GenericModel, table=True):
    """
    User model
    """

    __tablename__ = "user"

    username: str = Field(index=True, nullable=False, unique=True)
    email: str = Field(index=True, nullable=False, unique=True)
    hashed_password: str
    # portfolios: List["Portfolio"] = Relationship(back_populates="user")


class UserCreate(GenericCreate):
    """
    Create User request
    """

    username: str
    email: str
    password: str


class UserUpdate(GenericUpdate):
    """
    Update User request
    """

    username: str | None = None
    email: str | None = None


class UserRead(GenericRead):
    """
    Read User response
    """

    id: UUID
    username: str
    email: str | None = None


class UserResponse(GenericResponse):
    """
    User response
    """

    data: UserRead


class UserListResponse(GenericListResponse):
    """
    User list response
    """

    data: list[UserRead]
    total: int
    page: int = 1


class UserFilter(GenericFilter):
    """
    User filter
    """

    username: str | None = None
    email: str | None = None
    page: int = 1
    limit: int = 10
