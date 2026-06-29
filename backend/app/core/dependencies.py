# =========================================================================
# AI Medical Scribe Platform - FastAPI Authentication Dependencies
# =========================================================================
# This module provides reusable FastAPI dependency functions for
# route-level authentication guards. Any endpoint that requires an
# authenticated user simply declares:
#
#   current_user: User = Depends(get_current_user)
#
# The dependency resolves the JWT → email → User automatically.
# =========================================================================

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import TokenData

# ---------------------------------------------------------------------------
# OAuth2 scheme
# ---------------------------------------------------------------------------
# tokenUrl points to the login endpoint so Swagger UI can auto-populate
# the "Authorize" dialog with the correct URL.
# ---------------------------------------------------------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    FastAPI dependency that resolves a Bearer token to an authenticated User.

    Flow:
      1. Extract the Bearer token from the Authorization header.
      2. Decode and validate the JWT signature and expiry.
      3. Extract the 'sub' (email) claim from the payload.
      4. Load the User from the database by email.
      5. Return the User ORM object on success.

    Raises:
        HTTPException 401: On any JWT error (expired, invalid signature,
                           missing claim, or user not found in DB).

    Args:
        token: Raw JWT string extracted by OAuth2PasswordBearer.
        db:    Async DB session injected by get_db.

    Returns:
        The authenticated User ORM object.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)

    except JWTError:
        # Catches expired tokens, bad signatures, malformed JWTs, etc.
        raise credentials_exception

    repo = UserRepository(db)
    user = await repo.get_by_email(token_data.email)  # type: ignore[arg-type]

    if user is None:
        raise credentials_exception

    return user
