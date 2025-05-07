from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from jose import jwt
from datetime import datetime, timedelta
import logging
from app.models.user import User
from app.auth.security import verify_password, get_password_hash
from app.db.session import get_session
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/backdoor-register", status_code=201)
async def register_user(
    username: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    """Register a new user with username and password."""
    existing = await session.exec(select(User).where(User.email == username))
    if existing.first():
        raise HTTPException(status_code=400, detail="User already exists")
    user = User(
        username=username, email=username, hashed_password=get_password_hash(password)
    )
    session.add(user)
    await session.commit()
    return {"msg": "user created"}


@router.post("/token")
async def login_for_access_token(
    username: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    """
    Login endpoint that accepts form data with:
    - username: The user's username
    - password: The user's password

    Note: The data must be sent as form data (application/x-www-form-urlencoded)
    """
    logger.info(f"Attempting login for user: {username}")
    result = await session.exec(select(User).where(User.email == username))
    user = result.first()

    if not user:
        logger.warning(f"User not found: {username}")
        raise HTTPException(status_code=401, detail="Incorrect credentials")

    logger.info(f"Found user: {user.username}")
    password_verified = verify_password(password, user.hashed_password)
    logger.info(f"Password verification result: {password_verified}")

    if not password_verified:
        logger.warning(f"Invalid password for user: {username}")
        raise HTTPException(status_code=401, detail="Incorrect credentials")

    token_data = {"sub": str(user.id), "exp": datetime.utcnow() + timedelta(minutes=60)}
    token = jwt.encode(token_data, settings.SEC_SECRET_KEY, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}


def create_access_token(data: dict) -> str:
    """Create a new access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.SEC_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    token = jwt.encode(
        to_encode, settings.SEC_SECRET_KEY, algorithm=settings.SEC_ALGORITHM
    )
    return token
