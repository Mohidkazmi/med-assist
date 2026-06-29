# =========================================================================
# AI Medical Scribe Platform - Doctor Service
# =========================================================================
# Orchestrates all DoctorProfile business logic.
# Responsibilities:
#   - Validates domain-level constraints (duplicate user linkage, existence)
#   - Delegates data access to DoctorRepository and UserRepository
#   - Converts ORM objects to Pydantic response schemas
#   - Raises descriptive HTTPExceptions for all error paths
# =========================================================================

import uuid
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.doctor_repository import DoctorRepository
from app.repositories.user_repository import UserRepository
from app.schemas.common import PaginatedResponse
from app.schemas.doctor import (
    DoctorCreate,
    DoctorResponse,
    DoctorUpdate,
)


class DoctorService:
    """
    Orchestrates all DoctorProfile-related business operations.

    Injected with an AsyncSession so it remains stateless and testable.
    """

    def __init__(self, db: AsyncSession) -> None:
        self._repo = DoctorRepository(db)
        self._user_repo = UserRepository(db)

    async def list_doctors(
        self,
        *,
        page: int = 1,
        size: int = 20,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        specialty: Optional[str] = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
    ) -> PaginatedResponse[DoctorResponse]:
        """
        Return a paginated, optionally filtered and sorted list of doctor profiles.

        Supports simultaneous filtering on first name, last name, and specialty.

        Args:
            page:       Page number (1-indexed).
            size:       Items per page (capped at 100).
            first_name: Optional partial-match search on first name.
            last_name:  Optional partial-match search on last name.
            specialty:  Optional partial-match search on medical specialty.
            sort_by:    Field to sort by.
            sort_dir:   Sort direction ('asc' or 'desc').

        Returns:
            PaginatedResponse containing DoctorResponse items and metadata.
        """
        size = min(size, 100)
        skip = (page - 1) * size

        doctors, total = await self._repo.get_all(
            skip=skip,
            limit=size,
            first_name=first_name,
            last_name=last_name,
            specialty=specialty,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )

        items = [DoctorResponse.model_validate(d) for d in doctors]
        return PaginatedResponse.create(items=items, total=total, page=page, size=size)

    async def get_doctor(self, doctor_id: uuid.UUID) -> DoctorResponse:
        """
        Retrieve a single doctor profile by UUID. Raises 404 if not found.

        Args:
            doctor_id: The UUID of the DoctorProfile to retrieve.

        Returns:
            DoctorResponse schema.

        Raises:
            HTTPException 404: If no doctor profile with the given ID exists.
        """
        doctor = await self._repo.get_by_id(doctor_id)
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Doctor profile with id '{doctor_id}' was not found.",
            )
        return DoctorResponse.model_validate(doctor)

    async def create_doctor(self, doctor_create: DoctorCreate) -> DoctorResponse:
        """
        Create and persist a new doctor profile.

        Business rules enforced:
          1. The referenced user_id must exist in the users table.
          2. A doctor profile cannot already exist for that user_id (1:1 constraint).

        Args:
            doctor_create: Validated creation payload.

        Returns:
            DoctorResponse of the newly created profile.

        Raises:
            HTTPException 404: If the referenced user_id does not exist.
            HTTPException 409: If a doctor profile already exists for that user.
        """
        # Rule 1: Validate that the referenced user exists
        user = await self._user_repo.get_by_id(doctor_create.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id '{doctor_create.user_id}' was not found. "
                       "Register the user first via POST /api/v1/auth/register.",
            )

        # Rule 2: Enforce one-to-one constraint before the DB FK fires
        existing = await self._repo.get_by_user_id(doctor_create.user_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A doctor profile already exists for user '{doctor_create.user_id}'.",
            )

        doctor = await self._repo.create(doctor_create)
        return DoctorResponse.model_validate(doctor)

    async def update_doctor(
        self,
        doctor_id: uuid.UUID,
        doctor_update: DoctorUpdate,
    ) -> DoctorResponse:
        """
        Partially update an existing doctor profile.

        Only explicitly-sent fields are updated; others retain current values.

        Args:
            doctor_id:     The UUID of the DoctorProfile to update.
            doctor_update: Update payload (all fields optional).

        Returns:
            DoctorResponse of the updated profile.

        Raises:
            HTTPException 404: If no doctor profile with the given ID exists.
        """
        doctor = await self._repo.get_by_id(doctor_id)
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Doctor profile with id '{doctor_id}' was not found.",
            )
        updated = await self._repo.update(doctor, doctor_update)
        return DoctorResponse.model_validate(updated)

    async def delete_doctor(self, doctor_id: uuid.UUID) -> None:
        """
        Permanently delete a doctor profile.

        Does NOT delete the linked User account — only the profile.
        Raises 404 if the doctor profile does not exist.

        Args:
            doctor_id: The UUID of the DoctorProfile to delete.

        Raises:
            HTTPException 404: If no doctor profile with the given ID exists.
        """
        doctor = await self._repo.get_by_id(doctor_id)
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Doctor profile with id '{doctor_id}' was not found.",
            )
        await self._repo.delete(doctor)
