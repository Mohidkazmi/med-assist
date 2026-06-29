# =========================================================================
# AI Medical Scribe Platform - User Repository
# =========================================================================
# The repository layer is the ONLY place in the application that speaks
# directly to the database for user data. All SQL/ORM operations live here.
#
# SOLID: Single Responsibility — data access only.
#        Dependency Inversion — consumers depend on this class's interface,
#        not on SQLAlchemy directly.
# =========================================================================

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate


class UserRepository:
    """
    Async repository for User model database operations.

    Each method receives an AsyncSession injected by FastAPI's dependency
    system, keeping the repository stateless and easily testable.
    """

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user by email address.

        Args:
            email: The email to query (case-sensitive, unique in DB).

        Returns:
            The User ORM object if found, else None.
        """
        result = await self._db.execute(
            select(User).where(User.email == email)
        )
        return result.scalars().first()

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Retrieve a user by primary key (UUID).

        Args:
            user_id: The UUID primary key of the user.

        Returns:
            The User ORM object if found, else None.
        """
        result = await self._db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalars().first()

    async def create(self, user_create: UserCreate, hashed_password: str) -> User:
        """
        Persist a new user record to the database.

        The caller is responsible for hashing the password BEFORE
        passing it here — this repository never receives plain-text passwords.

        Args:
            user_create:     Validated UserCreate schema from the request.
            hashed_password: The bcrypt-hashed password string.

        Returns:
            The newly created and refreshed User ORM object.
        """
        db_user = User(
            email=user_create.email,
            hashed_password=hashed_password,
            is_active=True,
        )
        self._db.add(db_user)
        await self._db.commit()
        await self._db.refresh(db_user)
        return db_user
