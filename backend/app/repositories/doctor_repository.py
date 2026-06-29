# =========================================================================
# AI Medical Scribe Platform - Doctor Repository
# =========================================================================
# All SQL/ORM operations for the DoctorProfile model live here.
# Follows the same stateless, session-injected pattern as PatientRepository.
# =========================================================================

import uuid
from typing import List, Optional, Tuple

from sqlalchemy import asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.doctor import DoctorProfile
from app.schemas.doctor import DoctorCreate, DoctorUpdate


# Columns that are valid sort targets for the DoctorProfile resource
_DOCTOR_SORTABLE_COLUMNS: dict[str, any] = {
    "first_name": DoctorProfile.first_name,
    "last_name": DoctorProfile.last_name,
    "specialty": DoctorProfile.specialty,
    "created_at": DoctorProfile.created_at,
}


class DoctorRepository:
    """
    Async repository for DoctorProfile model database operations.

    Designed for injection by FastAPI's dependency system.
    Each method receives a pre-connected AsyncSession and performs a
    focused, single-purpose database operation.
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
        specialty: Optional[str] = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
    ) -> Tuple[List[DoctorProfile], int]:
        """
        Retrieve a filtered, sorted, paginated list of doctor profiles.

        Supports simultaneous filtering on first name, last name, and specialty.
        All text searches are case-insensitive partial matches (ILIKE).

        Args:
            skip:      Records offset for pagination.
            limit:     Maximum records per page.
            first_name: Optional partial filter on first name.
            last_name:  Optional partial filter on last name.
            specialty:  Optional partial filter on medical specialty.
            sort_by:   Column to sort by.
            sort_dir:  'asc' or 'desc'.

        Returns:
            Tuple of (list of DoctorProfile ORM objects, total matching count).
        """
        base_stmt = select(DoctorProfile)

        # --- Apply search filters ---
        filters = []
        if first_name:
            filters.append(DoctorProfile.first_name.ilike(f"%{first_name}%"))
        if last_name:
            filters.append(DoctorProfile.last_name.ilike(f"%{last_name}%"))
        if specialty:
            filters.append(DoctorProfile.specialty.ilike(f"%{specialty}%"))
        if filters:
            base_stmt = base_stmt.where(*filters)

        # --- Count query ---
        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total_result = await self._db.execute(count_stmt)
        total: int = total_result.scalar_one()

        # --- Apply sorting ---
        sort_col = _DOCTOR_SORTABLE_COLUMNS.get(sort_by, DoctorProfile.created_at)
        order_fn = asc if sort_dir == "asc" else desc
        base_stmt = base_stmt.order_by(order_fn(sort_col))

        # --- Apply pagination ---
        base_stmt = base_stmt.offset(skip).limit(limit)

        result = await self._db.execute(base_stmt)
        doctors = list(result.scalars().all())

        return doctors, total

    async def get_by_id(self, doctor_id: uuid.UUID) -> Optional[DoctorProfile]:
        """
        Retrieve a single doctor profile by UUID primary key.

        Args:
            doctor_id: The UUID primary key of the DoctorProfile.

        Returns:
            DoctorProfile ORM object, or None if not found.
        """
        result = await self._db.execute(
            select(DoctorProfile).where(DoctorProfile.id == doctor_id)
        )
        return result.scalars().first()

    async def get_by_user_id(self, user_id: uuid.UUID) -> Optional[DoctorProfile]:
        """
        Check whether a doctor profile already exists for a given user.

        Used during creation to enforce the one-to-one User → DoctorProfile
        constraint at the service layer (before the DB constraint fires).

        Args:
            user_id: The UUID of the parent User record.

        Returns:
            DoctorProfile ORM object if it exists, else None.
        """
        result = await self._db.execute(
            select(DoctorProfile).where(DoctorProfile.user_id == user_id)
        )
        return result.scalars().first()

    async def create(self, doctor_create: DoctorCreate) -> DoctorProfile:
        """
        Persist a new doctor profile record.

        The referenced user_id must already exist in the users table —
        referential integrity is enforced at the database level via FK.

        Args:
            doctor_create: Validated DoctorCreate schema from the request body.

        Returns:
            The newly created and DB-refreshed DoctorProfile ORM object.
        """
        db_doctor = DoctorProfile(
            user_id=doctor_create.user_id,
            first_name=doctor_create.first_name,
            last_name=doctor_create.last_name,
            specialty=doctor_create.specialty,
        )
        self._db.add(db_doctor)
        await self._db.commit()
        await self._db.refresh(db_doctor)
        return db_doctor

    async def update(
        self, doctor: DoctorProfile, doctor_update: DoctorUpdate
    ) -> DoctorProfile:
        """
        Apply a partial update to an existing doctor profile.

        Only explicitly-set fields are written; unset fields retain their values.

        Args:
            doctor:        Existing DoctorProfile ORM object to mutate.
            doctor_update: Update payload (all fields optional).

        Returns:
            The updated and DB-refreshed DoctorProfile ORM object.
        """
        update_data = doctor_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(doctor, field, value)

        self._db.add(doctor)
        await self._db.commit()
        await self._db.refresh(doctor)
        return doctor

    async def delete(self, doctor: DoctorProfile) -> None:
        """
        Permanently delete a doctor profile record.

        Cascades to linked Appointments and Consultations via DB constraints.

        Args:
            doctor: The DoctorProfile ORM object to delete.
        """
        await self._db.delete(doctor)
        await self._db.commit()
