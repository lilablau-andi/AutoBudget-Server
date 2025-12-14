from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import router as api_v1_router
from app.core.config import settings


def create_app() -> FastAPI:
    """
    Application factory.
    Ermöglicht sauberes Setup und spätere Tests.
    """
    app = FastAPI(
        title="Personal Finance Manager API",
        description="Backend API für eine Web-App zur Verwaltung persönlicher Finanzen",
        version="1.0.0",
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # -----------------------------
    # CORS
    # -----------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -----------------------------
    # Router
    # -----------------------------
    app.include_router(
        api_v1_router,
        prefix="/api/v1"
    )

    # -----------------------------
    # Health Check
    # -----------------------------
    @app.get("/health", tags=["Health"])
    async def health_check():
        return {"status": "ok"}

    return app


app = create_app()
