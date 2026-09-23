from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from ..models import User
from ..schemas import RegisterUser, ResponseUser
from ..db import get_async_session
from ..auth import hash_password, verify_password, create_access_token, get_current_user

import logging
logger = logging.getLogger(__name__)

router = APIRouter()
@router.post(
    "/register",
    response_model=ResponseUser)

async def register(
    data:RegisterUser,
    session:AsyncSession=Depends(get_async_session)
):
    result = await session.execute(select(User).where(User.email == data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    user = User(
        email=data.email,
        username=data.username,
        hashed_password=hash_password(data.password)
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    logger.info("User registration completed")

    return user

@router.post("/login")
async def log_in(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(
        select(User).where(User.email == form_data.username)
    )

    existing_user = result.scalar_one_or_none()

    if existing_user is None:
        logger.warning("Failed login attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    password_is_valid = verify_password(
        form_data.password,
        existing_user.hashed_password
    )

    if not password_is_valid:
        logger.warning("Failed login attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    token = create_access_token(
        {"sub": str(existing_user.id)}
    )

    logger.info("User logged in successfully")

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.get(
    "/me",
    response_model=ResponseUser
)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user
   