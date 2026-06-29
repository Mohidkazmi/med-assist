# =========================================================================
# AI Medical Scribe Platform - User Pydantic Schemas
# =========================================================================
# These schemas define the data contracts between the HTTP layer and the
# application layer. They are distinct from SQLAlchemy models intentionally —
# the ORM model owns the database, the schema owns the API surface.
# =========================================================================

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# ---------------------------------------------------------------------------
# Request Schemas (inbound)
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    """
    Schema for the POST /auth/register request body.

    The password is accepted as plain-text here; it will be hashed
    by the service layer before any persistence occurs.
    """
    email: EmailStr = Field(..., examples=["doctor@hospital.com"])
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        examples=["SecurePass@123"],
        description="Plain-text password. Minimum 8 characters.",
    )


class UserLogin(BaseModel):
    """
    Schema for direct JSON login (non-OAuth2 form variant).
    The OAuth2 form endpoint uses FastAPI's OAuth2PasswordRequestForm instead.
    """
    email: EmailStr
    password: str


# ---------------------------------------------------------------------------
# Response Schemas (outbound — never expose hashed_password)
# ---------------------------------------------------------------------------

class UserResponse(BaseModel):
    """
    Safe user representation returned to API consumers.

    The hashed_password field is intentionally absent from this schema.
    """
    id: uuid.UUID
    email: EmailStr
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}  # Allow ORM model → schema conversion


# ---------------------------------------------------------------------------
# Token Schemas
# ---------------------------------------------------------------------------

class Token(BaseModel):
    """
    Response body for POST /auth/login.
    Follows the OAuth2 bearer token response convention.
    """
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """
    Internal representation of the decoded JWT payload.
    The 'sub' claim stores the user's email address.
    """
    email: str | None = None
