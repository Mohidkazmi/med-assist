# =========================================================================
# AI Medical Scribe Platform - Declarative Base Registry
# =========================================================================

# This module imports all model metadata to ensure they are registered
# under the declarative Base class prior to running database migrations.
from app.db.base_class import Base  # noqa
from app.models.user import User  # noqa
from app.models.doctor import DoctorProfile  # noqa
from app.models.patient import Patient  # noqa
from app.models.appointment import Appointment  # noqa
from app.models.consultation import Consultation  # noqa
from app.models.transcription import Transcription  # noqa
from app.models.medical_note import MedicalNote  # noqa
