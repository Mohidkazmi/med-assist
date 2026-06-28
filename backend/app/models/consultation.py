from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
import uuid
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

if TYPE_CHECKING:
    from .doctor import DoctorProfile
    from .patient import Patient
    from .appointment import Appointment
    from .transcription import Transcription
    from .medical_note import MedicalNote


class Consultation(Base):
    """
    SQLAlchemy model representing clinical consultation sessions.
    """
    __tablename__ = "consultations"

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
    appointment_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("appointments.id", ondelete="SET NULL"),
        unique=True,
        nullable=True
    )
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    end_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="recording",
        nullable=False
    )

    # Relationships
    doctor: Mapped["DoctorProfile"] = relationship("DoctorProfile", back_populates="consultations")
    patient: Mapped["Patient"] = relationship("Patient", back_populates="consultations")
    appointment: Mapped[Optional["Appointment"]] = relationship("Appointment", back_populates="consultation")
    
    transcription: Mapped[Optional["Transcription"]] = relationship(
        "Transcription",
        back_populates="consultation",
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    medical_notes: Mapped[List["MedicalNote"]] = relationship(
        "MedicalNote",
        back_populates="consultation",
        cascade="all, delete-orphan"
    )
