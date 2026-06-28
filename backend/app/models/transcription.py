from typing import Any, TYPE_CHECKING
import uuid
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

if TYPE_CHECKING:
    from .consultation import Consultation


class Transcription(Base):
    """
    SQLAlchemy model representing the transcribed consultation dialog and audio URLs.
    """
    __tablename__ = "transcriptions"

    consultation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("consultations.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    audio_url: Mapped[str] = mapped_column(String(512), nullable=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=True)
    diarized_text: Mapped[Any] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False
    )

    # Relationships
    consultation: Mapped["Consultation"] = relationship("Consultation", back_populates="transcription")
