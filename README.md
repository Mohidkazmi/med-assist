# AI Medical Scribe Platform

This repository contains the foundation for the **AI Medical Scribe Platform**, a system designed to transcribe, analyze, and summarize clinical consultations between doctors and patients.

---

## Project Structure

A monorepo structure is used to logically divide the frontend and backend architectures:

```text
med-assist/
├── backend/                  # Python/FastAPI service (transcription & AI processing pipelines)
│   ├── app/                  # Application core, config, api, and business logic
│   ├── main.py               # Backend main entrypoint
│   ├── Dockerfile            # Backend Docker build instructions
│   └── requirements.txt      # Python dependencies list
├── frontend/                 # React client-facing web application
│   ├── src/                  # Components, pages, routing, and assets
│   ├── Dockerfile            # Node dev environment container setup
│   ├── vite.config.ts        # Vite build tool settings
│   └── package.json          # Script runners and frontend dependencies
├── docker/                   # Custom configuration templates and Docker build context files
│   └── postgres/
│       └── init.sql          # SQL script executed automatically on container initialization
├── docs/                     # Platform architecture diagrams and documentation
├── prompts/                  # Version-controlled development prompts registry
├── .env.example              # Template for environment variables (version controlled)
├── .env                      # Local environment configurations (contains secrets; gitignored)
├── .gitignore                # Global gitignore configuration
└── docker-compose.yml        # Docker composition settings for local dependencies
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
*(The default credentials generated in `.env` are ready for out-of-the-box local development.)*

---

## Command Reference

### Start Services (Detached Mode)
To spin up the Postgres database and pgAdmin in the background:
```bash
docker compose up -d
```

### Stop Services
To stop running containers and release resources without deleting persistent volumes:
```bash
docker compose down
```

To stop containers **and delete all volumes** (WARNING: This destroys database state):
```bash
docker compose down -v
```

### View Logs
To follow stdout/stderr outputs for all containers in real time:
```bash
docker compose logs -f
```

To view logs for a specific service (e.g., database only):
```bash
docker compose logs -f postgres
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
     * **Host name/address:** `postgres` (This is the container name resolvable within the Docker network)
     * **Port:** `5432` (Internal Docker network port; use `5433` if connecting directly from your host machine)
     * **Maintenance database:** `med_scribe_dev` (matching `POSTGRES_DB` in `.env`)
     * **Username:** `scribe_admin` (matching `POSTGRES_USER` in `.env`)
     * **Password:** `secure_development_password_99` (matching `POSTGRES_PASSWORD` in `.env`)
     * Click **Save**.

### 2. Verify Services Operation
To verify that the database, backend, and frontend services are running and healthy:

#### Method A: Docker Compose Health Status
Run the following command to check container health statuses:
```bash
docker compose ps
```
The output should indicate `healthy` under the STATUS column for the database and backend containers, and `running` for the frontend container.

#### Method B: Execute SQL Query via Docker CLI (Database Verification)
Run a test query directly inside the container without external tools:
```bash
docker exec -i med_assist_postgres psql -U scribe_admin -d med_scribe_dev -c "SELECT version();"
```
If the connection is successful, it will return the installed version of PostgreSQL.

#### Method C: Backend Health Check Endpoint
Query the health check endpoint from your host machine (using port `8001` or your configured `BACKEND_PORT`):
```bash
curl -i http://localhost:8001/health
```
If successful, it returns:
```json
{
  "status": "healthy",
  "service": "AI Medical Scribe Platform"
}
```

#### Method D: Frontend Web App Interface
Open your browser and navigate to the frontend port (exposes port `5173` to your host):
* URL: [http://localhost:5173](http://localhost:5173)
* Verify that you see the homepage header "AI Medical Scribe Platform", the "Backend Status: (Not Connected Yet)" badge, and a button to navigate to the Login placeholder screen.
