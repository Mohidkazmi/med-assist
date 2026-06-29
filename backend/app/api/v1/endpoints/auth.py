# =========================================================================
# AI Medical Scribe Platform - Authentication API Endpoints
# =========================================================================
# Three endpoints covering the complete auth lifecycle:
#   POST /auth/register  — create a new account
#   POST /auth/login     — authenticate and receive a JWT token
#   GET  /auth/me        — retrieve the current user's profile (protected)
# =========================================================================

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserResponse
from app.services.auth_service import AuthService

router = APIRouter()


# ---------------------------------------------------------------------------
# POST /auth/register
# ---------------------------------------------------------------------------

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    description=(
        "Creates a new user record. The plain-text password is hashed with "
        "bcrypt before storage. Returns the created user profile (no password)."
    ),
    responses={
        201: {"description": "User successfully registered"},
        409: {"description": "Email address is already in use"},
    },
)
async def register(
    user_create: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """
    **POST /auth/register**

    Register a new platform user.

    - **email**: Must be a valid email address, unique across the platform.
    - **password**: Minimum 8 characters. Stored only as a bcrypt hash.

    Returns the new user's profile on success (HTTP 201).
    Returns HTTP 409 if the email is already registered.
    """
    service = AuthService(db)
    return await service.register(user_create)


# ---------------------------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------------------------

@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Login and obtain a JWT access token",
    description=(
        "Accepts OAuth2 form-encoded credentials (username = email, password). "
        "Returns a signed JWT bearer token on success."
    ),
    responses={
        200: {"description": "Login successful — JWT token returned"},
        401: {"description": "Invalid credentials"},
        403: {"description": "Account is deactivated"},
    },
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    """
    **POST /auth/login**

    Authenticate with email and password via OAuth2 form encoding.

    The `username` field in the form body is used as the email address
    (standard OAuth2 convention).

    Returns:
        `access_token`: A signed JWT string.
        `token_type`:   Always `"bearer"`.
    """
    service = AuthService(db)
    # OAuth2PasswordRequestForm uses 'username' for the email field
    return await service.login(email=form_data.username, password=form_data.password)


# ---------------------------------------------------------------------------
# GET /auth/me
# ---------------------------------------------------------------------------

@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current authenticated user profile",
    description=(
        "Returns the profile of the user identified by the provided Bearer token. "
        "Requires a valid, non-expired JWT in the Authorization header."
    ),
    responses={
        200: {"description": "Authenticated user profile"},
        401: {"description": "Missing, invalid, or expired token"},
    },
)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    """
    **GET /auth/me**

    Retrieve the profile of the currently authenticated user.

    Requires:
        Authorization: Bearer <access_token>

    Returns the user's `id`, `email`, `is_active`, and `created_at`.
    The password hash is never returned.
    """
    return AuthService.get_me(current_user)
