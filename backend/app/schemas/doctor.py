# =========================================================================
# AI Medical Scribe Platform - Doctor Pydantic Schemas
# =========================================================================
# Defines the data contracts for the DoctorProfile resource:
#   DoctorCreate   — request body for POST /doctors
#   DoctorUpdate   — request body for PUT /doctors/{id} (all fields optional)
#   DoctorResponse — outbound response (includes linked user email)
# =========================================================================

import uuid
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Allowed values for controlled fields
# ---------------------------------------------------------------------------

DOCTOR_SORT_FIELDS = Literal["first_name", "last_name", "specialty", "created_at"]

SORT_DIRECTIONS = Literal["asc", "desc"]


# ---------------------------------------------------------------------------
# Request Schemas (inbound)
# ---------------------------------------------------------------------------

class DoctorCreate(BaseModel):
    """
    Schema for POST /doctors request body.

    Requires a `user_id` referencing an existing registered User.
    The caller must first register a user via POST /auth/register,
    then use the returned UUID here to attach the doctor profile.
    """

    user_id: uuid.UUID = Field(
        ...,
        description=(
            "UUID of an existing registered User. "
            "Register the user first via POST /auth/register."
        ),
        examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"],
    )
    first_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        examples=["Sarah"],
        description="Doctor's first name.",
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        examples=["Johnson"],
        description="Doctor's last name.",
    )
    specialty: str = Field(
        ...,
        min_length=1,
        max_length=100,
        examples=["Cardiology"],
        description="Medical specialty (e.g. Cardiology, Neurology, General Practice).",
    )


class DoctorUpdate(BaseModel):
    """
    Schema for PUT /doctors/{id} request body.

    All profile fields are optional — only supplied fields are updated.
    The `user_id` FK is intentionally excluded: it cannot be changed after creation.
    """

    first_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Updated first name.",
    )
    last_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Updated last name.",
    )
    specialty: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Updated medical specialty.",
    )


# ---------------------------------------------------------------------------
# Response Schemas (outbound)
# ---------------------------------------------------------------------------

class DoctorResponse(BaseModel):
    """
    Doctor profile representation returned to API consumers.

    Includes all profile fields, the linked `user_id`, and audit timestamps.
    """

    id: uuid.UUID
    user_id: uuid.UUID
    first_name: str
    last_name: str
    specialty: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
