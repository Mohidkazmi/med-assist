# =========================================================================
# AI Medical Scribe Platform - Patient Service
# =========================================================================
# Orchestrates all Patient business logic.
# Responsibilities:
#   - Validates domain-level constraints (not DB/schema-level)
#   - Delegates all data access to PatientRepository
#   - Converts ORM objects to Pydantic response schemas
#   - Raises descriptive HTTPExceptions for all error paths
#
# SOLID:
#   Single Responsibility — business rules for patients only.
#   Open/Closed — new business rules extend this class; callers unchanged.
#   Dependency Inversion — depends on PatientRepository interface, not ORM.
# =========================================================================

import uuid
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.patient_repository import PatientRepository
from app.schemas.common import PaginatedResponse
from app.schemas.patient import (
    PatientCreate,
    PatientResponse,
    PatientUpdate,
)


class PatientService:
    """
    Orchestrates all Patient-related business operations.

    Injected with an AsyncSession so it remains stateless and testable.
    """

    def __init__(self, db: AsyncSession) -> None:
        self._repo = PatientRepository(db)

    async def list_patients(
        self,
        *,
        page: int = 1,
        size: int = 20,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
    ) -> PaginatedResponse[PatientResponse]:
        """
        Return a paginated, optionally filtered and sorted list of patients.

        Args:
            page:       Page number (1-indexed).
            size:       Items per page (capped at 100).
            first_name: Optional partial-match search on first name.
            last_name:  Optional partial-match search on last name.
            sort_by:    Field to sort by.
            sort_dir:   Sort direction ('asc' or 'desc').

        Returns:
            PaginatedResponse containing PatientResponse items and metadata.
        """
        # Enforce max page size to protect the DB from huge queries
        size = min(size, 100)
        skip = (page - 1) * size

        patients, total = await self._repo.get_all(
            skip=skip,
            limit=size,
            first_name=first_name,
            last_name=last_name,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )

        items = [PatientResponse.model_validate(p) for p in patients]
        return PaginatedResponse.create(items=items, total=total, page=page, size=size)

    async def get_patient(self, patient_id: uuid.UUID) -> PatientResponse:
        """
        Retrieve a single patient by UUID. Raises 404 if not found.

        Args:
            patient_id: The UUID of the patient to retrieve.

        Returns:
            PatientResponse schema.

        Raises:
            HTTPException 404: If no patient with the given ID exists.
        """
        patient = await self._repo.get_by_id(patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with id '{patient_id}' was not found.",
            )
        return PatientResponse.model_validate(patient)

    async def create_patient(self, patient_create: PatientCreate) -> PatientResponse:
        """
        Create and persist a new patient record.

        Args:
            patient_create: Validated creation payload.

        Returns:
            PatientResponse of the newly created patient.
        """
        patient = await self._repo.create(patient_create)
        return PatientResponse.model_validate(patient)

    async def update_patient(
        self,
        patient_id: uuid.UUID,
        patient_update: PatientUpdate,
    ) -> PatientResponse:
        """
        Partially update an existing patient record.

        Only fields explicitly sent in the request body are updated.
        Raises 404 if no patient with the given ID exists.

        Args:
            patient_id:     The UUID of the patient to update.
            patient_update: The update payload (all fields optional).

        Returns:
            PatientResponse of the updated patient.

        Raises:
            HTTPException 404: If no patient with the given ID exists.
        """
        patient = await self._repo.get_by_id(patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with id '{patient_id}' was not found.",
            )
        updated = await self._repo.update(patient, patient_update)
        return PatientResponse.model_validate(updated)

    async def delete_patient(self, patient_id: uuid.UUID) -> None:
        """
        Permanently delete a patient record.

        Raises 404 if the patient does not exist.

        Args:
            patient_id: The UUID of the patient to delete.

        Raises:
            HTTPException 404: If no patient with the given ID exists.
        """
        patient = await self._repo.get_by_id(patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with id '{patient_id}' was not found.",
            )
        await self._repo.delete(patient)
