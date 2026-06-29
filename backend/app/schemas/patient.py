# =========================================================================
# AI Medical Scribe Platform - Patient Pydantic Schemas
# =========================================================================
# Defines the data contracts for the Patient resource:
#   PatientCreate   — request body for POST /patients
#   PatientUpdate   — request body for PUT /patients/{id} (all fields optional)
#   PatientResponse — outbound response (no internal DB fields exposed)
# =========================================================================

import uuid
from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Allowed values for controlled fields
# ---------------------------------------------------------------------------

GENDER_VALUES = Literal["male", "female", "other", "prefer_not_to_say"]

PATIENT_SORT_FIELDS = Literal["first_name", "last_name", "date_of_birth", "created_at"]

SORT_DIRECTIONS = Literal["asc", "desc"]


# ---------------------------------------------------------------------------
# Request Schemas (inbound)
# ---------------------------------------------------------------------------

class PatientCreate(BaseModel):
    """
    Schema for POST /patients request body.

    All fields are required to create a minimal, valid patient record.
    """

    first_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        examples=["John"],
        description="Patient's legal first name.",
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        examples=["Doe"],
        description="Patient's legal last name.",
    )
    date_of_birth: date = Field(
        ...,
        examples=["1990-05-15"],
        description="Date of birth in YYYY-MM-DD format.",
    )
    gender: GENDER_VALUES = Field(
        ...,
        examples=["male"],
        description="Patient's gender identity.",
    )


class PatientUpdate(BaseModel):
    """
    Schema for PUT /patients/{id} request body.

    All fields are optional — only the provided fields will be updated.
    This implements a partial-update (PATCH-style) pattern via a PUT verb.
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
    date_of_birth: Optional[date] = Field(
        None,
        description="Updated date of birth.",
    )
    gender: Optional[GENDER_VALUES] = Field(
        None,
        description="Updated gender identity.",
    )


# ---------------------------------------------------------------------------
# Response Schemas (outbound)
# ---------------------------------------------------------------------------

class PatientResponse(BaseModel):
    """
    Safe patient representation returned to API consumers.

    Includes all demographic fields plus audit timestamps.
    """

    id: uuid.UUID
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
