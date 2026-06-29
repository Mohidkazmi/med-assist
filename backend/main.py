import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.db.base  # noqa: F401 — registers all ORM models with SQLAlchemy mapper
from app.api.v1.router import api_v1_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API service for AI Medical Scribe Platform",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.ENVIRONMENT == "development" else None,
)

# Set up CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# ---------------------------------------------------------------------------
# Mount versioned API router
# ---------------------------------------------------------------------------
# All endpoints under /api/v1/* are registered here.
# ---------------------------------------------------------------------------
app.include_router(api_v1_router, prefix=settings.API_V1_STR)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Service health check endpoint.
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME
    }


# Root endpoint redirection / welcome message
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": f"Welcome to the {settings.PROJECT_NAME} Backend API.",
        "documentation": "/docs" if settings.ENVIRONMENT == "development" else "hidden"
    }


if __name__ == "__main__":
    # This block allows running the backend directly using python main.py
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False,
    )
