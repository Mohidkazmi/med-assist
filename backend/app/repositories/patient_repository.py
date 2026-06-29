# =========================================================================
# AI Medical Scribe Platform - Patient Repository
# =========================================================================
# All SQL/ORM operations for the Patient model live here.
# The service layer never constructs queries directly — it delegates to this
# class, keeping DB concerns isolated behind a clean interface.
#
# SOLID:
#   Single Responsibility — data access for patients only.
#   Open/Closed — new query methods can be added without touching callers.
#   Dependency Inversion — consumers depend on this class's interface.
# =========================================================================

import uuid
from typing import List, Optional, Tuple

from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate


# Columns that are valid sort targets for the Patient resource
_PATIENT_SORTABLE_COLUMNS: dict[str, any] = {
    "first_name": Patient.first_name,
    "last_name": Patient.last_name,
    "date_of_birth": Patient.date_of_birth,
    "created_at": Patient.created_at,
}


class PatientRepository:
    """
    Async repository for Patient model database operations.

    Accepts an AsyncSession from FastAPI's dependency injection system,
    making each repository instance stateless and independently testable.
    """

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_all(
        self,
        *,
        skip: int = 0,
        limit: int = 20,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
    ) -> Tuple[List[Patient], int]:
        """
        Retrieve a filtered, sorted, paginated list of patients.

        Search is case-insensitive partial-match (SQL ILIKE).
        Sorting falls back to `created_at DESC` for any unrecognised column.

        Args:
            skip:       Number of records to skip (offset).
            limit:      Maximum records to return.
            first_name: Optional partial-match filter on first name.
            last_name:  Optional partial-match filter on last name.
            sort_by:    Column name to sort by.
            sort_dir:   'asc' or 'desc'.

        Returns:
            A tuple of (list of Patient ORM objects, total matching count).
        """
        # Base query
        base_stmt = select(Patient)

        # --- Apply search filters ---
        filters = []
        if first_name:
            filters.append(Patient.first_name.ilike(f"%{first_name}%"))
        if last_name:
            filters.append(Patient.last_name.ilike(f"%{last_name}%"))
        if filters:
            base_stmt = base_stmt.where(*filters)

        # --- Count query (runs before pagination) ---
        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total_result = await self._db.execute(count_stmt)
        total: int = total_result.scalar_one()

        # --- Apply sorting ---
        sort_col = _PATIENT_SORTABLE_COLUMNS.get(sort_by, Patient.created_at)
        order_fn = asc if sort_dir == "asc" else desc
        base_stmt = base_stmt.order_by(order_fn(sort_col))

        # --- Apply pagination ---
        base_stmt = base_stmt.offset(skip).limit(limit)

        result = await self._db.execute(base_stmt)
        patients = list(result.scalars().all())

        return patients, total

    async def get_by_id(self, patient_id: uuid.UUID) -> Optional[Patient]:
        """
        Retrieve a single patient by primary key UUID.

        Args:
            patient_id: The UUID primary key.

        Returns:
            The Patient ORM object, or None if not found.
        """
        result = await self._db.execute(
            select(Patient).where(Patient.id == patient_id)
        )
        return result.scalars().first()

    async def create(self, patient_create: PatientCreate) -> Patient:
        """
        Persist a new patient record.

        Args:
            patient_create: Validated PatientCreate schema from the request body.

        Returns:
            The newly created and DB-refreshed Patient ORM object.
        """
        db_patient = Patient(
            first_name=patient_create.first_name,
            last_name=patient_create.last_name,
            date_of_birth=patient_create.date_of_birth,
            gender=patient_create.gender,
        )
        self._db.add(db_patient)
        await self._db.commit()
        await self._db.refresh(db_patient)
        return db_patient

    async def update(self, patient: Patient, patient_update: PatientUpdate) -> Patient:
        """
        Apply a partial update to an existing patient record.

        Only fields that are explicitly set in `patient_update` are written.
        Unset (None) fields are skipped — preserving their current values.

        Args:
            patient:        The existing Patient ORM object to mutate.
            patient_update: The update payload (all fields optional).

        Returns:
            The updated and DB-refreshed Patient ORM object.
        """
        update_data = patient_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(patient, field, value)

        self._db.add(patient)
        await self._db.commit()
        await self._db.refresh(patient)
        return patient

    async def delete(self, patient: Patient) -> None:
        """
        Permanently delete a patient record.

        Cascades to related Appointments and Consultations via DB constraints.

        Args:
            patient: The Patient ORM object to delete.
        """
        await self._db.delete(patient)
        await self._db.commit()
