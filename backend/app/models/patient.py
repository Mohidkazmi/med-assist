from datetime import date
from typing import List, TYPE_CHECKING
from sqlalchemy import Date, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

if TYPE_CHECKING:
    from .appointment import Appointment
    from .consultation import Consultation


class Patient(Base):
    """
    SQLAlchemy model representing patient records and demographics.
    """
    __tablename__ = "patients"

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    gender: Mapped[str] = mapped_column(String(50), nullable=False)

    # Relationships
    appointments: Mapped[List["Appointment"]] = relationship(
        "Appointment",
        back_populates="patient",
        cascade="all, delete-orphan"
    )
    
    consultations: Mapped[List["Consultation"]] = relationship(
        "Consultation",
        back_populates="patient",
        cascade="all, delete-orphan"
    )
