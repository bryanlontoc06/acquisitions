import uuid
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.status import HTTP_201_CREATED

from .. import dbModels
from ..auth.auth import create_access_token, hash_password, verify_password
from ..core.config import settings
from ..db.database import get_db
from ..schemas.token import Token
from ..schemas.users import LoginResponse, UserCreate, UserPrivate

router = APIRouter()


@router.post("/register", response_model=UserPrivate, status_code=HTTP_201_CREATED)
async def register_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(dbModels.User).where(
            func.lower(dbModels.User.email) == user.email.lower()
        )
    )
    existing_email = result.scalars().first()
    logger.info(f"🔍 Checking for existing email: {user.email}")
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = dbModels.User(
        uid=uuid.uuid4(),
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        role=user.role,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/authenticate", response_model=LoginResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    logger.info("--- [ START SESSION ] ---")
    logger.info("event: SESSION")
    logger.info(f"payload: {form_data.__dict__}")
    # Look up user by email (case-insensitive)
    # Note: OAuth2PasswordRequestForm uses "username" field, but we treat it as email
    result = await db.execute(
        select(dbModels.User).where(
            func.lower(dbModels.User.email) == form_data.username.lower()
        )
    )
    user = result.scalars().first()

    # Verify user exists and password is correct
    # Don't reveal which one failed (security best practice)
    if not user or not verify_password(form_data.password, user.password):
        logger.warning(
            f"event: LOGIN_FAILED | payload: {{'email': '{form_data.username}'}}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_minutes = settings.access_token_expire_minutes
    refresh_token_days = settings.refresh_token_expire_days
    if not refresh_token_days:
        try:
            refresh_token_days = int(refresh_token_days)
        except ValueError:
            logger.error(
                f"Invalid REFRESH_TOKEN_EXPIRE_DAYS value: {refresh_token_days}. Using default of 7 days."
            )
            refresh_token_days = 7

    base_data = {
        "id": user.uid,
        "email": user.email,
    }

    access_token_expires = timedelta(minutes=access_token_minutes)
    # Create access token (for simplicity, we are not creating a separate refresh token here)
    access_token = create_access_token(
        data={**base_data, "token_type": "access"},
        expires_delta=access_token_expires,
    )

    # Refresh Token (optional, can be implemented similarly to access token with a longer expiration)
    refresh_token = create_access_token(
        data={**base_data, "token_type": "refresh"},
        expires_delta=timedelta(days=int(refresh_token_days)),
    )

    # ID Token (contains user info, can be used by frontend)
    id_token = create_access_token(
        data={**base_data, "name": user.name, "role": user.role, "token_type": "id"},
        expires_delta=timedelta(minutes=access_token_minutes),
    )
    logger.info("✅ Session created")
    logger.info("--- [ END SESSION ] ---")
    return LoginResponse(
        token=Token(
            access_token=access_token,
            refresh_token=refresh_token,
            id_token=id_token,
            expires_in=access_token_minutes * 60,  # convert minutes to seconds
            token_type="bearer",
        )
    )
