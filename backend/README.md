# AI Medical Scribe Platform - Backend Service

This is the backend API service for the **AI Medical Scribe Platform** built with **FastAPI** and **Python 3.12**.

---

## Folder Structure

The application layout is structured around scalable enterprise python architectural patterns:

```text
backend/
├── app/
│   ├── api/                  # API endpoints and route controllers
│   ├── core/                 # App configurations (config.py), security, and constants
│   ├── db/                   # Database engines and session setup (SQLAlchemy)
│   ├── models/               # SQLAlchemy ORM models definitions
│   ├── schemas/              # Pydantic schemas for request/response serialization
│   ├── services/             # Core business logic processing (e.g. Scribe audio analyzer)
│   ├── repositories/         # Repository pattern for DB access abstraction
│   ├── ai/                   # AI/ML interfaces (Whisper integration, LLM prompts)
│   └── utils/                # Helper utilities and shared functions
├── main.py                   # FastAPI initialization and local ASGI runner
├── requirements.txt          # Package dependencies
└── Dockerfile                # Production-ready slim Docker container definition
```

---

## Core Technologies & Dependencies

* **FastAPI (0.111.x)**: High-performance, modern web framework for building APIs with Python based on standard type hints.
* **Uvicorn (0.30.x)**: Lightning-fast ASGI server implementation used to run the FastAPI application.
* **Pydantic v2 (2.7.x)**: Data validation and settings management using Python type annotations.
* **SQLAlchemy (2.0.x)**: SQL Toolkit and Object Relational Mapper for database queries.
* **Alembic (1.13.x)**: Lightweight database migration tool for SQLAlchemy schema changes.
* **asyncpg (0.29.x)**: Fast, asynchronous database interface library for PostgreSQL.

---

## Local Development Setup

### 1. Python Environment Setup
1. Create a virtual environment using Python 3.12:
   ```bash
   python3.12 -m venv venv
   ```
2. Activate the virtual environment:
   * **macOS / Linux:**
     ```bash
     source venv/bin/activate
     ```
   * **Windows:**
     ```bash
     venv\Scripts\activate
     ```
3. Install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

### 2. Running Locally (Without Docker)
To start the hot-reloading development server:
```bash
python main.py
```
Or use the Uvicorn CLI directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Verification & Testing

Verify that the backend service is healthy by sending a GET request:

* **Using curl:**
  ```bash
  # For local python/uvicorn run:
  curl -i http://localhost:8000/health
  # For Docker Compose run:
  curl -i http://localhost:8001/health
  ```
* **Expected Response:**
  ```json
  {
    "status": "healthy",
    "service": "AI Medical Scribe Platform"
  }
  ```

* **Interactive API Documentation:**
  When running locally in `development` mode, navigate to:
  * Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs) (or [http://localhost:8001/docs](http://localhost:8001/docs) via Docker)
  * ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc) (or [http://localhost:8001/redoc](http://localhost:8001/redoc) via Docker)
