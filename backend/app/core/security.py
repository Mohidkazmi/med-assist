# =========================================================================
# AI Medical Scribe Platform - Authentication Security Utilities
# =========================================================================
# Pure cryptographic helpers — no FastAPI dependencies here.
# These functions are consumed by the service layer and FastAPI dependencies.
# =========================================================================

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

# ---------------------------------------------------------------------------
# Password hashing context
# ---------------------------------------------------------------------------
# CryptContext handles algorithm selection and automatic rehashing when
# stronger algorithms become available.
# ---------------------------------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """
    Hash a plain-text password using bcrypt.

    Args:
        plain_password: The raw password string from the user.

    Returns:
        A bcrypt-hashed string safe to store in the database.
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a stored bcrypt hash.

    Args:
        plain_password:  The raw password submitted during login.
        hashed_password: The bcrypt hash stored in the database.

    Returns:
        True if the password matches the hash, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a signed JWT access token.

    The payload is copied so the original dict is never mutated.
    Expiry defaults to settings.ACCESS_TOKEN_EXPIRE_MINUTES if not provided.

    Args:
        data:          Arbitrary claims to embed in the token (e.g. {"sub": email}).
        expires_delta: Optional custom TTL for this token.

    Returns:
        A signed JWT string.
    """
    payload = data.copy()

    if expires_delta is not None:
        expire = datetime.now(tz=timezone.utc) + expires_delta
    else:
        expire = datetime.now(tz=timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    payload.update({"exp": expire})

    encoded_jwt = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt
