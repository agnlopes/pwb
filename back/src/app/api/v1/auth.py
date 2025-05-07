from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.auth.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from app.db.session import get_session
from app.models.user import User
from app.utils.logging import log_user_action
from app.metrics import track_auth_attempt, track_auth_failure, track_token_operation

router = APIRouter()


@router.post("/token")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_session),
) -> Any:
    """Get access token for user."""
    # Track the attempt first
    track_auth_attempt("password", "attempt")

    try:
        # Find user by email
        result = await db.exec(select(User).where(User.email == username))
        user = result.first()

        if not user or not verify_password(password, user.hashed_password):
            track_auth_attempt("password", "failure")
            track_auth_failure("invalid_credentials")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            track_auth_attempt("password", "failure")
            track_auth_failure("inactive_user")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = create_access_token(data={"sub": user.email})
        track_auth_attempt("password", "success")
        track_token_operation("create", "success")

        # Log successful login
        await log_user_action(
            session=db,
            user_id=user.id,
            action="login",
            method="POST",
            path="/token",
            target_type="user",
            target_id=user.id,
            details={"email": user.email},
        )

        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        track_auth_attempt("password", "failure")
        track_auth_failure("unexpected_error")
        raise e


@router.get("/me")
async def read_users_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> Any:
    """Get current user info."""
    # Log user info access
    await log_user_action(
        session=db,
        user_id=current_user.id,
        action="get_profile",
        method="GET",
        path="/me",
        target_type="user",
        target_id=current_user.id,
    )
    return current_user
