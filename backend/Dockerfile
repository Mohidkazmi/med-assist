# =========================================================================
# AI Medical Scribe Platform - Backend Service Dockerfile
# =========================================================================

# Use the official Python 3.12 slim-buster image for a smaller build footprint
FROM python:3.12-slim as base

# Setup environment variables
# PIP_NO_CACHE_DIR: Disables pip caching to keep image size small
# PYTHONUNBUFFERED: Prevents Python from buffering stdout/stderr (crucial for container logs)
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc files inside the container
ENV PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Install system dependencies if needed (e.g. gcc for compiling raw deps, libpq-dev for Postgres driver)
# Note: slim-buster requires apt updates. We clean them up immediately to keep image size low.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements to leverage Docker cache layers
COPY requirements.txt .

# Install dependencies using wheels
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy rest of the application files
COPY . .

# Expose FastAPI server port
EXPOSE 8000

# Default execution command (development hot-reload is enabled via docker-compose overrides/commands)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
