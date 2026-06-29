# =========================================================================
# AI Medical Scribe Platform - Doctor API Endpoints
# =========================================================================
# Five CRUD endpoints for the DoctorProfile resource.
# Every endpoint requires a valid JWT Bearer token.
#
# GET    /doctors          — list with pagination, search (name + specialty), sort
# GET    /doctors/{id}     — retrieve single doctor profile
# POST   /doctors          — create new doctor profile (requires existing user_id)
# PUT    /doctors/{id}     — partial update doctor profile
# DELETE /doctors/{id}     — delete doctor profile (NOT the linked user account)
# =========================================================================

import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.doctor import (
    DOCTOR_SORT_FIELDS,
    SORT_DIRECTIONS,
    DoctorCreate,
    DoctorResponse,
    DoctorUpdate,
)
from app.services.doctor_service import DoctorService

router = APIRouter()


# ---------------------------------------------------------------------------
# GET /doctors  — list with pagination, search, sorting
# ---------------------------------------------------------------------------

@router.get(
    "",
    response_model=PaginatedResponse[DoctorResponse],
    status_code=status.HTTP_200_OK,
    summary="List doctor profiles",
    description=(
        "Returns a paginated list of doctor profiles. "
        "Supports partial-match search on first name, last name, and specialty. "
        "Results are sortable by any doctor profile field."
    ),
    responses={
        200: {"description": "Paginated list of doctor profiles"},
        401: {"description": "Invalid or missing JWT token"},
    },
)
async def list_doctors(
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
    specialty: Optional[str] = Query(
        default=None,
        description="Partial case-insensitive filter on medical specialty (e.g. 'cardio')",
        max_length=100,
    ),
    sort_by: DOCTOR_SORT_FIELDS = Query(
        default="created_at",
        description="Field to sort results by",
    ),
    sort_dir: SORT_DIRECTIONS = Query(
        default="desc",
        description="Sort direction: 'asc' for ascending, 'desc' for descending",
    ),
) -> PaginatedResponse[DoctorResponse]:
    """
    **GET /doctors**

    Retrieve a paginated list of all doctor profiles.

    ### Search
    - `first_name`: partial, case-insensitive match
    - `last_name`:  partial, case-insensitive match
    - `specialty`:  partial, case-insensitive match (e.g. `cardio` matches `Cardiology`)

    ### Sorting
    - `sort_by`: one of `first_name`, `last_name`, `specialty`, `created_at`
    - `sort_dir`: `asc` or `desc` (default: `desc`)

    ### Pagination
    - Response includes `total`, `page`, `size`, and `pages` metadata.
    """
    service = DoctorService(db)
    return await service.list_doctors(
        page=page,
        size=size,
        first_name=first_name,
        last_name=last_name,
        specialty=specialty,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )


# ---------------------------------------------------------------------------
# GET /doctors/{id}  — retrieve single doctor profile
# ---------------------------------------------------------------------------

@router.get(
    "/{doctor_id}",
    response_model=DoctorResponse,
    status_code=status.HTTP_200_OK,
    summary="Get doctor profile by ID",
    description="Retrieve a single doctor profile record by their UUID.",
    responses={
        200: {"description": "Doctor profile found"},
        401: {"description": "Invalid or missing JWT token"},
        404: {"description": "Doctor profile not found"},
    },
)
async def get_doctor(
    doctor_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _current_user: Annotated[User, Depends(get_current_user)],
) -> DoctorResponse:
    """
    **GET /doctors/{doctor_id}**

    Retrieve a single doctor profile by UUID.

    Returns `404 Not Found` if no doctor profile with the given ID exists.
    """
    service = DoctorService(db)
    return await service.get_doctor(doctor_id)


# ---------------------------------------------------------------------------
# POST /doctors  — create new doctor profile
# ---------------------------------------------------------------------------

@router.post(
    "",
    response_model=DoctorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new doctor profile",
    description=(
        "Create a doctor profile linked to an existing registered user. "
        "Register the user first via POST /api/v1/auth/register, "
        "then supply the returned user UUID here."
    ),
    responses={
        201: {"description": "Doctor profile successfully created"},
        401: {"description": "Invalid or missing JWT token"},
        404: {"description": "Referenced user_id does not exist"},
        409: {"description": "Doctor profile already exists for this user"},
        422: {"description": "Validation error in request body"},
    },
)
async def create_doctor(
    doctor_create: DoctorCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _current_user: Annotated[User, Depends(get_current_user)],
) -> DoctorResponse:
    """
    **POST /doctors**

    Create a new doctor profile.

    ### Workflow
    1. Register a user: `POST /api/v1/auth/register`
    2. Copy the returned `id` (UUID)
    3. Call this endpoint with that UUID as `user_id`

    ### Required fields
    - `user_id`    — UUID of an existing registered user
    - `first_name` — 1–100 characters
    - `last_name`  — 1–100 characters
    - `specialty`  — 1–100 characters (e.g. `Cardiology`, `Neurology`)

    Returns `404` if the user doesn't exist.
    Returns `409` if a doctor profile already exists for that user.
    """
    service = DoctorService(db)
    return await service.create_doctor(doctor_create)


# ---------------------------------------------------------------------------
# PUT /doctors/{id}  — partial update doctor profile
# ---------------------------------------------------------------------------

@router.put(
    "/{doctor_id}",
    response_model=DoctorResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a doctor profile",
    description=(
        "Partially update a doctor profile record. "
        "Only the fields included in the request body are modified. "
        "The `user_id` FK cannot be changed after creation."
    ),
    responses={
        200: {"description": "Doctor profile successfully updated"},
        401: {"description": "Invalid or missing JWT token"},
        404: {"description": "Doctor profile not found"},
        422: {"description": "Validation error in request body"},
    },
)
async def update_doctor(
    doctor_id: uuid.UUID,
    doctor_update: DoctorUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _current_user: Annotated[User, Depends(get_current_user)],
) -> DoctorResponse:
    """
    **PUT /doctors/{doctor_id}**

    Partially update an existing doctor profile.

    All fields are optional — send only the fields you wish to change.
    The `user_id` link cannot be modified after creation.
    Returns `404 Not Found` if no doctor profile with the given ID exists.
    """
    service = DoctorService(db)
    return await service.update_doctor(doctor_id, doctor_update)


# ---------------------------------------------------------------------------
# DELETE /doctors/{id}  — delete doctor profile
# ---------------------------------------------------------------------------

@router.delete(
    "/{doctor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a doctor profile",
    description=(
        "Permanently delete a doctor profile record. "
        "This does NOT delete the linked user account — "
        "only the profile (appointments and consultations cascade)."
    ),
    responses={
        204: {"description": "Doctor profile successfully deleted"},
        401: {"description": "Invalid or missing JWT token"},
        404: {"description": "Doctor profile not found"},
    },
)
async def delete_doctor(
    doctor_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """
    **DELETE /doctors/{doctor_id}**

    Permanently delete a doctor profile and linked appointments/consultations.

    The linked User account is NOT deleted — only the doctor profile.
    Returns `204 No Content` on success.
    Returns `404 Not Found` if no doctor profile with the given ID exists.
    """
    service = DoctorService(db)
    await service.delete_doctor(doctor_id)
