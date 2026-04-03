from datetime import timedelta
from typing import Annotated

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from .. import dbModels
from ..auth.auth import create_access_token
from ..core.config import settings
from ..db.database import get_db
from ..schemas.token import Token, TokenResponse

load_dotenv()
router = APIRouter()

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


@router.post("", response_model=TokenResponse)
async def generate(
    db: Annotated[AsyncSession, Depends(get_db)],
    x_api_key: str = Security(api_key_header),
):
    logger.info("--- [ START CREATE SESSION ] ---")
    logger.info("event: SESSION")
    logger.info(f"payload: {x_api_key}")

    user_result = await db.execute(
        select(dbModels.User).where(dbModels.User.uid == x_api_key)
    )

    user = user_result.scalar_one_or_none()

    if user is None:
        logger.error("event: User not found in database!")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User not found",
        )

    base_data = {
        "id": user.uid,
        "email": user.email,
    }

    access_token = create_access_token(
        data={**base_data, "token_type": "access"},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    refresh_token = create_access_token(
        data={**base_data, "token_type": "refresh"},
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
    )
    # ID Token (contains user info, can be used by frontend)
    id_token = create_access_token(
        data={**base_data, "name": user.name, "role": user.role, "token_type": "id"},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )

    logger.info("event: SESSION")
    logger.info(f"payload: {x_api_key}")
    logger.info("--- [ END CREATE SESSION ] ---")

    return TokenResponse(
        token=Token(
            access_token=access_token,
            refresh_token=refresh_token,
            id_token=id_token,
            expires_in=settings.access_token_expire_minutes
            * 60,  # convert minutes to seconds
            token_type="bearer",
        )
    )
