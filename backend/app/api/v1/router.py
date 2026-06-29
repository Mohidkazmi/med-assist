# =========================================================================
# AI Medical Scribe Platform - API v1 Central Router
# =========================================================================
# This module is the single aggregation point for all v1 API routers.
# To add a new resource, import its router here and include it below.
# =========================================================================

from fastapi import APIRouter

from app.api.v1.endpoints import auth, doctors, patients

# Root router for all /api/v1/* routes
api_v1_router = APIRouter()

# ---------------------------------------------------------------------------
# Authentication routes
# /api/v1/auth/register  POST
# /api/v1/auth/login     POST
# /api/v1/auth/me        GET
# ---------------------------------------------------------------------------
api_v1_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
)

# ---------------------------------------------------------------------------
# Patient CRUD routes  (all JWT-protected)
# /api/v1/patients       GET, POST
# /api/v1/patients/{id}  GET, PUT, DELETE
# ---------------------------------------------------------------------------
api_v1_router.include_router(
    patients.router,
    prefix="/patients",
    tags=["Patients"],
)

# ---------------------------------------------------------------------------
# Doctor CRUD routes  (all JWT-protected)
# /api/v1/doctors        GET, POST
# /api/v1/doctors/{id}   GET, PUT, DELETE
# ---------------------------------------------------------------------------
api_v1_router.include_router(
    doctors.router,
    prefix="/doctors",
    tags=["Doctors"],
)
