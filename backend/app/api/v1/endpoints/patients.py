# =========================================================================
# AI Medical Scribe Platform - Patient API Endpoints
# =========================================================================
# Five CRUD endpoints for the Patient resource.
# Every endpoint requires a valid JWT Bearer token.
#
# GET    /patients          — list with pagination, search, sort
# GET    /patients/{id}     — retrieve single patient
# POST   /patients          — create new patient
# PUT    /patients/{id}     — partial update existing patient
# DELETE /patients/{id}     — delete patient (cascades to appointments)
# =========================================================================

import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.patient import (
    PATIENT_SORT_FIELDS,
    SORT_DIRECTIONS,
    PatientCreate,
    PatientResponse,
    PatientUpdate,
)
from app.services.patient_service import PatientService

router = APIRouter()


# ---------------------------------------------------------------------------
# GET /patients  — list with pagination, search, sorting
# ---------------------------------------------------------------------------

@router.get(
    "",
    response_model=PaginatedResponse[PatientResponse],
    status_code=status.HTTP_200_OK,
    summary="List patients",
    description=(
        "Returns a paginated list of patients. "
        "Supports partial-match search on first and last name (case-insensitive). "
        "Results are sortable by any patient field."
    ),
    responses={
        200: {"description": "Paginated list of patients"},
        401: {"description": "Invalid or missing JWT token"},
    },
)
async def list_patients(
    db: Annotated[AsyncSession, Depends(get_db)],
    _current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    size: int = Query(default=20, ge=1, le=100, description="Items per page (max 100)"),
    first_name: Optional[str] = Query(
        default=None,
        description="Partial case-insensitive filter on first name",
        max_length=100,
    ),
    last_name: Optional[str] = Query(
        default=None,
        description="Partial case-insensitive filter on last name",
        max_length=100,
    ),
    sort_by: PATIENT_SORT_FIELDS = Query(
        default="created_at",
        description="Field to sort results by",
    ),
    sort_dir: SORT_DIRECTIONS = Query(
        default="desc",
        description="Sort direction: 'asc' for ascending, 'desc' for descending",
    ),
) -> PaginatedResponse[PatientResponse]:
    """
    **GET /patients**

    Retrieve a paginated list of all patient records.

    ### Search
    - `first_name`: partial, case-insensitive match (e.g. `jo` matches `John`, `Joanna`)
    - `last_name`:  partial, case-insensitive match

    ### Sorting
    - `sort_by`: one of `first_name`, `last_name`, `date_of_birth`, `created_at`
    - `sort_dir`: `asc` or `desc` (default: `desc`)

    ### Pagination
    - Response includes `total`, `page`, `size`, and `pages` metadata.
    """
    service = PatientService(db)
    return await service.list_patients(
        page=page,
        size=size,
        first_name=first_name,
        last_name=last_name,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )


# ---------------------------------------------------------------------------
# GET /patients/{id}  — retrieve single patient
# ---------------------------------------------------------------------------

@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
    status_code=status.HTTP_200_OK,
    summary="Get patient by ID",
    description="Retrieve a single patient record by their UUID.",
    responses={
        200: {"description": "Patient record found"},
        401: {"description": "Invalid or missing JWT token"},
        404: {"description": "Patient not found"},
    },
)
async def get_patient(
    patient_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _current_user: Annotated[User, Depends(get_current_user)],
) -> PatientResponse:
    """
    **GET /patients/{patient_id}**

    Retrieve a single patient record by UUID.

    Returns `404 Not Found` if no patient with the given ID exists.
    """
    service = PatientService(db)
    return await service.get_patient(patient_id)


# ---------------------------------------------------------------------------
# POST /patients  — create new patient
# ---------------------------------------------------------------------------

@router.post(
    "",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new patient",
    description="Register a new patient record with full demographic information.",
    responses={
        201: {"description": "Patient successfully created"},
        401: {"description": "Invalid or missing JWT token"},
        422: {"description": "Validation error in request body"},
    },
)
async def create_patient(
    patient_create: PatientCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _current_user: Annotated[User, Depends(get_current_user)],
) -> PatientResponse:
    """
    **POST /patients**

    Create a new patient record.

    ### Required fields
    - `first_name` — 1–100 characters
    - `last_name`  — 1–100 characters
    - `date_of_birth` — `YYYY-MM-DD` format
    - `gender` — one of: `male`, `female`, `other`, `prefer_not_to_say`

    Returns the created patient with HTTP 201.
    """
    service = PatientService(db)
    return await service.create_patient(patient_create)


# ---------------------------------------------------------------------------
# PUT /patients/{id}  — partial update
# ---------------------------------------------------------------------------

@router.put(
    "/{patient_id}",
    response_model=PatientResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a patient",
    description=(
        "Partially update a patient record. "
        "Only the fields included in the request body are modified. "
        "Omitted fields retain their current values."
    ),
    responses={
        200: {"description": "Patient successfully updated"},
        401: {"description": "Invalid or missing JWT token"},
        404: {"description": "Patient not found"},
        422: {"description": "Validation error in request body"},
    },
)
async def update_patient(
    patient_id: uuid.UUID,
    patient_update: PatientUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _current_user: Annotated[User, Depends(get_current_user)],
) -> PatientResponse:
    """
    **PUT /patients/{patient_id}**

    Partially update an existing patient record.

    All fields are optional — send only the fields you wish to change.
    Returns `404 Not Found` if no patient with the given ID exists.
    """
    service = PatientService(db)
    return await service.update_patient(patient_id, patient_update)


# ---------------------------------------------------------------------------
# DELETE /patients/{id}  — delete patient
# ---------------------------------------------------------------------------

@router.delete(
    "/{patient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a patient",
    description=(
        "Permanently delete a patient record. "
        "Cascades to all linked appointments and consultations."
    ),
    responses={
        204: {"description": "Patient successfully deleted"},
        401: {"description": "Invalid or missing JWT token"},
        404: {"description": "Patient not found"},
    },
)
async def delete_patient(
    patient_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """
    **DELETE /patients/{patient_id}**

    Permanently delete a patient and all related records.

    Returns `204 No Content` on success.
    Returns `404 Not Found` if no patient with the given ID exists.
    """
    service = PatientService(db)
    await service.delete_patient(patient_id)
