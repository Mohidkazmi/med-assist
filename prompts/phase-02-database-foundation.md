# Phase 2: Database Foundation Prompt

Below is the exact development prompt used to initialize the SQLAlchemy models, configurations, and Alembic migrations for the **AI Medical Scribe Platform** monorepo:

```markdown
PHASE 2 — Database Foundation

We already have:

✔ FastAPI
✔ Docker
✔ PostgreSQL
✔ SQLAlchemy installed
✔ Alembic installed

Now implement ONLY the database foundation.

Requirements:

1. Create SQLAlchemy Base.
2. Configure async SQLAlchemy engine.
3. Configure async session.
4. Create declarative Base.
5. Create models folder.
6. Implement the following models:

- User
- DoctorProfile
- Patient
- Appointment
- Consultation
- MedicalNote
- Transcription

Requirements:

• UUID primary keys
• created_at
• updated_at
• Foreign Keys
• Relationships
• Type hints
• SQLAlchemy 2.0 style

Do NOT implement authentication.

Do NOT implement APIs.

Do NOT implement CRUD.

Do NOT implement frontend.

Only implement models and database configuration.

After implementation:

• Configure Alembic.
• Generate first migration.
• Run migration automatically inside Docker.
• Verify tables are created successfully.

Finally explain:

- every file created
- every relationship
- how to verify migration
- how to inspect tables in pgAdmin
```
