# Phase 1.1: Backend Skeleton Prompt

Below is the exact development prompt used to initialize the FastAPI backend service skeleton for the **AI Medical Scribe Platform** monorepo:

```markdown
You are a Senior Python Backend Architect.

First inspect the entire repository.

Understand the current architecture.

Do not recreate existing files.

Modify only the files necessary for this task.

Project:
AI Medical Scribe Platform

Current State:
- Docker working
- PostgreSQL working
- pgAdmin working
- Phase 0 completed

Goal:
Implement ONLY the backend skeleton.

Requirements:

Backend Technology:
- Python 3.12
- FastAPI
- Uvicorn
- Pydantic v2
- SQLAlchemy 2.x
- Alembic

Create the following structure:

backend/

├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── repositories/
│   ├── ai/
│   └── utils/
│
├── main.py
├── requirements.txt
├── Dockerfile
└── README.md

Requirements:

1. Configure FastAPI application.
2. Create GET /health endpoint.
3. Response must be:

{
  "status": "healthy",
  "service": "AI Medical Scribe Platform"
}

4. Configure Uvicorn development server.
5. Create requirements.txt.
6. Create Dockerfile.
7. Add backend service to docker-compose.yml.
8. Enable hot reload for development.
9. Use environment variables where appropriate.
10. No database connection yet.
11. No authentication.
12. No business logic.
13. No AI implementation.

After implementation:

- Explain every file created.
- Explain every dependency added.
- Explain how to run backend.
- Explain how to test /health endpoint.
- Explain Docker integration.
- Stop after Phase 1.1.
```
