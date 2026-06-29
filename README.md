# AI Medical Scribe Platform

This repository contains the foundation for the **AI Medical Scribe Platform**, a system designed to transcribe, analyze, and summarize clinical consultations between doctors and patients.

---

## Project Structure

A monorepo structure is used to logically divide the frontend and backend architectures:

```text
med-assist/
├── backend/                  # Python/FastAPI service (transcription & AI processing pipelines)
│   ├── app/                  # Application core, config, api, and business logic
│   │   ├── api/v1/           # Versioned API routers and endpoint handlers
│   │   │   ├── endpoints/    # Individual resource endpoint modules
│   │   │   │   └── auth.py   # POST /register, POST /login, GET /me
│   │   │   └── router.py     # Central aggregation router for v1
│   │   ├── core/             # Config, security utilities, FastAPI dependencies
│   │   │   ├── config.py     # Pydantic-settings Settings class (JWT + DB)
│   │   │   ├── security.py   # hash_password, verify_password, create_access_token
│   │   │   └── dependencies.py # get_current_user FastAPI dependency
│   │   ├── db/               # SQLAlchemy engine, session factory, Base class
│   │   ├── models/           # ORM models (User, DoctorProfile, Patient, …)
│   │   ├── repositories/     # Data access layer (UserRepository)
│   │   ├── schemas/          # Pydantic request/response schemas (user.py)
│   │   └── services/         # Business logic orchestration (AuthService)
│   ├── main.py               # Backend main entrypoint
│   ├── Dockerfile            # Backend Docker build instructions
│   └── requirements.txt      # Python dependencies list
├── frontend/                 # React client-facing web application
├── docker/                   # Custom configuration templates
├── docs/                     # Platform architecture diagrams and documentation
├── .env.example              # Template for environment variables (version controlled)
├── .env                      # Local environment configurations (gitignored)
└── docker-compose.yml        # Docker composition settings for local development
```

---

## Infrastructure Overview

We use **Docker Compose** to locally orchestrate our development infrastructure:
1. **PostgreSQL 16**: Relational database storing patient metadata, transcription logs, and system audits.
2. **pgAdmin 4**: Web-based administration tool for Postgres management.
3. **Backend Service (FastAPI)**: REST API layer serving endpoints and coordinating transcription workflows (exposed on host port `8001` to resolve conflicts, default `8000`).

All services are connected via an isolated Docker bridge network (`med_assist_net`) and persist configurations across container restarts.

---

## Getting Started

### 1. Prerequisites
Ensure you have the following installed on your machine:
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Docker Compose)
* [Git](https://git-scm.com/)

### 2. Environment Configuration
Copy the environment variables template and configure your local settings:
```bash
cp .env.example .env
```

Generate a strong JWT secret key and add it to `.env`:
```bash
openssl rand -hex 32
# Copy the output and set it as JWT_SECRET_KEY in .env
```

---

## Command Reference

### Start Services (Detached Mode)
```bash
docker compose up -d
```

### Stop Services
```bash
docker compose down
```

To stop containers **and delete all volumes** (WARNING: destroys database state):
```bash
docker compose down -v
```

### View Logs
```bash
docker compose logs -f
# Or for a specific service:
docker compose logs -f backend
```

---

## Phase 3 — Authentication & Authorization

### New Environment Variables

Add the following to your `.env` file (these are already in `.env.example`):

| Variable | Description | Example |
|---|---|---|
| `JWT_SECRET_KEY` | Secret used to sign JWTs. **Must be 32+ random bytes.** | `openssl rand -hex 32` |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime in minutes | `30` |

---

### API Endpoints

#### `POST /api/v1/auth/register`
Create a new user account.

**Request body:**
```json
{
  "email": "doctor@hospital.com",
  "password": "SecurePass@123"
}
```

**Success response (201):**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "email": "doctor@hospital.com",
  "is_active": true,
  "created_at": "2026-06-28T12:00:00Z"
}
```

**Error (409):** Email already registered.

---

#### `POST /api/v1/auth/login`
Authenticate and receive a JWT bearer token.

Uses **OAuth2 form encoding** (`application/x-www-form-urlencoded`).
The `username` field holds the email address (standard OAuth2 convention).

**Success response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error (401):** Invalid credentials. **Error (403):** Account deactivated.

---

#### `GET /api/v1/auth/me`
Retrieve the current user's profile. **Requires a valid Bearer token.**

**Request header:**
```
Authorization: Bearer <access_token>
```

**Success response (200):**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "email": "doctor@hospital.com",
  "is_active": true,
  "created_at": "2026-06-28T12:00:00Z"
}
```

**Error (401):** Missing, invalid, or expired token.

---

### Authentication Flow (Step-by-Step)

```
Client                    FastAPI                   Database
  │                          │                          │
  │── POST /auth/register ──►│                          │
  │   { email, password }    │── UserRepository ───────►│
  │                          │   get_by_email()         │
  │                          │◄── None (not found) ─────│
  │                          │                          │
  │                          │   hash_password()        │
  │                          │── UserRepository ───────►│
  │                          │   create(user, hash)     │
  │                          │◄── User ORM object ──────│
  │◄── 201 UserResponse ─────│                          │
  │                          │                          │
  │── POST /auth/login ─────►│                          │
  │   { username, password } │── UserRepository ───────►│
  │                          │   get_by_email()         │
  │                          │◄── User ORM object ──────│
  │                          │                          │
  │                          │   verify_password()      │
  │                          │   (bcrypt.verify)        │
  │                          │                          │
  │                          │   create_access_token()  │
  │                          │   JWT { sub: email }     │
  │◄── 200 Token ────────────│                          │
  │    { access_token, … }   │                          │
  │                          │                          │
  │── GET /auth/me ─────────►│                          │
  │   Authorization: Bearer  │                          │
  │                          │   get_current_user()     │
  │                          │   jwt.decode(token)      │
  │                          │   → email from 'sub'     │
  │                          │── UserRepository ───────►│
  │                          │   get_by_email(email)    │
  │                          │◄── User ORM object ──────│
  │◄── 200 UserResponse ─────│                          │
```

---

### Docker Verification Commands

#### Build backend image
```bash
docker compose build backend
```

#### Start all services
```bash
docker compose up -d
```

#### Check backend logs
```bash
docker compose logs backend
```

#### Check service health
```bash
docker compose ps
```

---

### Testing with curl

Replace `8001` with your `BACKEND_PORT` if different.

#### 1. Register a new user
```bash
curl -s -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "doctor@hospital.com", "password": "SecurePass@123"}' \
  | python3 -m json.tool
```

#### 2. Login and capture the token
```bash
TOKEN=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=doctor@hospital.com&password=SecurePass@123" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo "Token: $TOKEN"
```

#### 3. Access the protected /me endpoint
```bash
curl -s http://localhost:8001/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

#### 4. Test with an invalid token (should return 401)
```bash
curl -s http://localhost:8001/api/v1/auth/me \
  -H "Authorization: Bearer invalid.token.here" \
  | python3 -m json.tool
```

#### 5. Try to register the same email twice (should return 409)
```bash
curl -s -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "doctor@hospital.com", "password": "AnotherPass@456"}' \
  | python3 -m json.tool
```

---

## Database Management & Verification

### 1. Connect pgAdmin to PostgreSQL
1. Start the Docker containers: `docker compose up -d`
2. Open your web browser and navigate to the pgAdmin portal: [http://localhost:5050](http://localhost:5050)
3. Log in using pgAdmin credentials specified in your `.env` file:
   * **Email:** `admin@medscribe.com` (or your configured `PGADMIN_DEFAULT_EMAIL`)
   * **Password:** `admin_secret_pass_123` (or your configured `PGADMIN_DEFAULT_PASSWORD`)
4. Once inside the dashboard, register the database server:
   * Right-click on **Servers** -> **Register** -> **Server...**
   * **General Tab:**
     * **Name:** `Med Assist Postgres` (or any custom label)
   * **Connection Tab:**
     * **Host name/address:** `postgres` (resolvable within the Docker network)
     * **Port:** `5432` (internal Docker network port; use `5433` from host)
     * **Maintenance database:** `med_scribe_dev`
     * **Username:** `scribe_admin`
     * **Password:** `secure_development_password_99`
     * Click **Save**.

### 2. Verify Services Operation

#### Method A: Docker Compose Health Status
```bash
docker compose ps
```

#### Method B: SQL Query via Docker CLI
```bash
docker exec -i med_assist_postgres psql -U scribe_admin -d med_scribe_dev -c "SELECT version();"
```

#### Method C: Backend Health Check Endpoint
```bash
curl -i http://localhost:8001/health
```
Expected response:
```json
{
  "status": "healthy",
  "service": "AI Medical Scribe Platform"
}
```

#### Method D: Swagger UI
Open [http://localhost:8001/docs](http://localhost:8001/docs) and test endpoints directly via the interactive UI.

---

## Phase 4 — Patient & Doctor Management

### New Files

| File | Purpose |
|---|---|
| `app/schemas/common.py` | Generic `PaginatedResponse[T]` envelope for all list endpoints |
| `app/schemas/patient.py` | `PatientCreate`, `PatientUpdate`, `PatientResponse` schemas |
| `app/schemas/doctor.py` | `DoctorCreate`, `DoctorUpdate`, `DoctorResponse` schemas |
| `app/repositories/patient_repository.py` | CRUD + filtered/paginated queries for `Patient` |
| `app/repositories/doctor_repository.py` | CRUD + filtered/paginated queries for `DoctorProfile` |
| `app/services/patient_service.py` | Business logic orchestration for patient operations |
| `app/services/doctor_service.py` | Business logic orchestration for doctor operations |
| `app/api/v1/endpoints/patients.py` | 5 patient CRUD endpoints (all JWT-protected) |
| `app/api/v1/endpoints/doctors.py` | 5 doctor CRUD endpoints (all JWT-protected) |

---

### Patient Endpoints

All patient endpoints require `Authorization: Bearer <token>`.

#### `GET /api/v1/patients`
List all patients with pagination, filtering, and sorting.

| Query Param | Type | Default | Description |
|---|---|---|---|
| `page` | int | `1` | Page number (1-indexed) |
| `size` | int | `20` | Items per page (max 100) |
| `first_name` | string | — | Case-insensitive partial search |
| `last_name` | string | — | Case-insensitive partial search |
| `sort_by` | string | `created_at` | `first_name` · `last_name` · `date_of_birth` · `created_at` |
| `sort_dir` | string | `desc` | `asc` or `desc` |

**Response (200):**
```json
{
  "items": [{ "id": "...", "first_name": "John", "last_name": "Doe", "date_of_birth": "1990-05-15", "gender": "male", "created_at": "...", "updated_at": "..." }],
  "total": 1,
  "page": 1,
  "size": 20,
  "pages": 1
}
```

#### `GET /api/v1/patients/{id}`
Retrieve a single patient. Returns `404` if not found.

#### `POST /api/v1/patients`
Create a new patient. Returns `201` with the created record.

**Request body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1990-05-15",
  "gender": "male"
}
```
`gender` accepts: `male` · `female` · `other` · `prefer_not_to_say`

#### `PUT /api/v1/patients/{id}`
Partially update a patient. All fields optional. Returns `404` if not found.

#### `DELETE /api/v1/patients/{id}`
Permanently delete a patient. Returns `204 No Content`. Cascades to appointments and consultations.

---

### Doctor Endpoints

All doctor endpoints require `Authorization: Bearer <token>`.

> **Workflow**: Register a user first via `POST /auth/register`, then use the returned `id` as `user_id` in `POST /doctors`.

#### `GET /api/v1/doctors`
List all doctors with pagination, filtering, and sorting.

| Query Param | Type | Default | Description |
|---|---|---|---|
| `page` | int | `1` | Page number |
| `size` | int | `20` | Items per page (max 100) |
| `first_name` | string | — | Case-insensitive partial search |
| `last_name` | string | — | Case-insensitive partial search |
| `specialty` | string | — | Case-insensitive partial search (e.g. `cardio` → `Cardiology`) |
| `sort_by` | string | `created_at` | `first_name` · `last_name` · `specialty` · `created_at` |
| `sort_dir` | string | `desc` | `asc` or `desc` |

#### `GET /api/v1/doctors/{id}`
Retrieve a single doctor profile. Returns `404` if not found.

#### `POST /api/v1/doctors`
Create a doctor profile linked to an existing user.

**Request body:**
```json
{
  "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "first_name": "Sarah",
  "last_name": "Johnson",
  "specialty": "Cardiology"
}
```
Returns `404` if `user_id` doesn't exist. Returns `409` if a profile already exists for that user.

#### `PUT /api/v1/doctors/{id}`
Partially update a doctor profile. `user_id` cannot be changed. Returns `404` if not found.

#### `DELETE /api/v1/doctors/{id}`
Delete the doctor profile only (the linked user account is NOT deleted). Returns `204 No Content`.

---

### Testing via Swagger UI

1. Start services: `docker compose up -d`
2. Open **[http://localhost:8001/docs](http://localhost:8001/docs)**
3. Click **Authorize** → enter credentials via the login form
4. Use the interactive forms to test all 10 endpoints

