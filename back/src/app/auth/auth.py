from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from jose import jwt
from datetime import datetime, timedelta
from app.models.user import User
from app.auth.security import verify_password, get_password_hash
from app.db.session import get_session
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/backdoor-register", status_code=201)
async def register_user(
    username: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_session())
):
    existing = await session.exec(select(User).where(User.email == username))
    if existing.first():
        raise HTTPException(status_code=400, detail="User already exists")
    user = User(username=username, email=username, hashed_password=get_password_hash(password))
    session.add(user)
    await session.commit()
    return {"msg": "user created"}

@router.post("/token")
async def login_for_access_token(
    username: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_session())
):
    result = await session.exec(select(User).where(User.email == username))
    user = result.first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect credentials")

    token_data = {
        "sub": str(user.id),
        "exp": datetime.utcnow() + timedelta(minutes=60)
    }
    token = jwt.encode(token_data, settings.SECRET_KEY, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}
