from datetime import datetime
from typing import Optional, TYPE_CHECKING
import uuid
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

if TYPE_CHECKING:
    from .doctor import DoctorProfile
    from .patient import Patient
    from .consultation import Consultation


class Appointment(Base):
    """
    SQLAlchemy model representing appointments between doctors and patients.
    """
    __tablename__ = "appointments"

    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("doctor_profiles.id", ondelete="CASCADE"),
        nullable=False
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False
    )
    appointment_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="scheduled",
        nullable=False
    )

    # Relationships
    doctor: Mapped["DoctorProfile"] = relationship("DoctorProfile", back_populates="appointments")
    patient: Mapped["Patient"] = relationship("Patient", back_populates="appointments")
    
    consultation: Mapped[Optional["Consultation"]] = relationship(
        "Consultation",
        back_populates="appointment",
        uselist=False,
        cascade="all, delete-orphan"
    )
