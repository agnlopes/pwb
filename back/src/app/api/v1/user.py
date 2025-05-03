from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.security import get_current_user
from app.db.session import get_session
from app.models.user import User, UserCreate, UserUpdate
from app.services import user as user_service

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/{uid}", response_model=User)
async def get_user(
    uid: UUID,
    session: AsyncSession = Depends(get_session()),
    user: User = Depends(get_current_user),
):
    return await user_service.get(session, user, str(uid))


@router.get("/", response_model=List[User])
async def list_users(
    session: AsyncSession = Depends(get_session()),
    user: User = Depends(get_current_user),
):
    return await user_service.list_all(session, user)


@router.post("/", response_model=User)
async def create_user(
    data: UserCreate,
    session: AsyncSession = Depends(get_session()),
    user: User = Depends(get_current_user),
):
    return await user_service.create(session, user, data)


@router.put("/{uid}", response_model=User)
async def update_user(
    uid: UUID,
    data: UserUpdate,
    session: AsyncSession = Depends(get_session()),
    user: User = Depends(get_current_user),
):
    return await user_service.update(session, user, str(uid), data)


@router.delete("/{uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    uid: UUID,
    session: AsyncSession = Depends(get_session()),
    user: User = Depends(get_current_user),
):
    await user_service.delete(session, user, str(uid))
