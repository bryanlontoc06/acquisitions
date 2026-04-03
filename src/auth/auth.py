from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from loguru import logger
from pwdlib import PasswordHash

from ..core.config import settings

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    # Placeholder for password hashing logic
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    # Placeholder for password verification logic
    return password_hash.verify(password, hashed_password)


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    logger.debug(
        f"Creating access token with data: {to_encode} and expires_delta: {expires_delta}"
    )
    # Set the token expiration time
    if expires_delta:
        # Use UTC timezone for consistent expiration handling
        expire = datetime.now(UTC) + expires_delta
    else:
        # Default to 30 minutes if no expiration is provided
        expire = datetime.now(UTC) + timedelta(
            minutes=int(settings.access_token_expire_minutes)
        )

    to_encode.update({"exp": expire})
    # Encode the token using the secret key and algorithm
    secret_key: str = settings.secret_key.get_secret_value()
    algorithm: str = settings.algorithm
    encoded_jwt: str = jwt.encode(  # type: ignore[no-untyped-call]
        payload=to_encode, key=secret_key, algorithm=algorithm
    )
    return encoded_jwt


def verify_access_token(token: str) -> dict[str, Any] | None:
    """Verify a JWT access token and return the subject (user ID) if valid."""
    try:
        secret_key: str = settings.secret_key.get_secret_value()
        algorithm: str = settings.algorithm
        payload: dict[str, Any] = jwt.decode(  # type: ignore[no-untyped-call]
            jwt=token,
            key=secret_key,
            algorithms=[algorithm],
            options={"require": ["exp", "sub"]},
        )
        return payload  # Successfully decoded token, return the payload
    except jwt.ExpiredSignatureError:
        logger.warning("Access token has expired.")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Invalid access token.")
        return None
