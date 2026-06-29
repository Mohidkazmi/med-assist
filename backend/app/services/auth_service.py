# =========================================================================
# AI Medical Scribe Platform - Authentication Service
# =========================================================================
# The service layer orchestrates business logic. It:
#   - Calls the repository for data access
#   - Calls security utilities for hashing / token creation
#   - Raises meaningful HTTP exceptions for auth failures
#   - Never returns raw DB models to API handlers (converts to schemas)
#
# SOLID: Open/Closed — new auth strategies can be added without modifying
#        this class; Dependency Inversion — depends on repository interface.
# =========================================================================

from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import Token, UserCreate, UserResponse


class AuthService:
    """
    Orchestrates all authentication-related business logic.

    Receives an injected AsyncSession so it remains stateless and testable.
    """

    def __init__(self, db: AsyncSession) -> None:
        self._repo = UserRepository(db)

    async def register(self, user_create: UserCreate) -> UserResponse:
        """
        Register a new user account.

        Steps:
          1. Check whether the email is already taken.
          2. Hash the plain-text password with bcrypt.
          3. Persist the new user via the repository.
          4. Return a safe UserResponse (no password fields).

        Raises:
            HTTPException 409: If a user with the given email already exists.

        Args:
            user_create: Validated registration data from the request body.

        Returns:
            UserResponse schema of the newly created user.
        """
        existing_user = await self._repo.get_by_email(user_create.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email address already exists.",
            )

        hashed = hash_password(user_create.password)
        new_user = await self._repo.create(user_create, hashed)
        return UserResponse.model_validate(new_user)

    async def login(self, email: str, password: str) -> Token:
        """
        Authenticate a user and return a signed JWT access token.

        Steps:
          1. Load the user by email.
          2. Verify the plain-text password against the stored hash.
          3. Reject inactive accounts.
          4. Create and return a JWT access token.

        Raises:
            HTTPException 401: If credentials are invalid or account is inactive.
            HTTPException 403: If the account is deactivated.

        Args:
            email:    The user's email address.
            password: Plain-text password from the login form.

        Returns:
            Token schema containing the signed JWT and token_type="bearer".
        """
        user = await self._repo.get_by_email(email)

        # Use a generic error message to avoid leaking whether an email exists
        credentials_error = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

        if not user:
            raise credentials_error

        if not verify_password(password, user.hashed_password):
            raise credentials_error

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been deactivated. Contact support.",
            )

        access_token = create_access_token(
            data={"sub": user.email},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return Token(access_token=access_token, token_type="bearer")

    @staticmethod
    def get_me(current_user: User) -> UserResponse:
        """
        Return the profile of the currently authenticated user.

        This is a lightweight static method because the user is already
        loaded by the get_current_user dependency before reaching here.

        Args:
            current_user: The User ORM object resolved by the auth dependency.

        Returns:
            UserResponse schema representation of the authenticated user.
        """
        return UserResponse.model_validate(current_user)
