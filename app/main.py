# Die Hauptdatei lädt die FastAPI und legt fest, auf welchen Adressen die Docs erreichbar sind
# Sie setzt auch Metadaten für die Docs fest

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import router as api_v1_router
from app.core.config import settings
import logging

# Logging Konfiguration für Debugging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Aufbau der FastAPI
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

    # CORS -> StandardCORS Config für FastAPI damit diese im Browser laufen kann
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Router -> Registrierung der API, damit diese Verfügbar ist
    app.include_router(
        api_v1_router,
        prefix="/api/v1"
    )

    # Health Check -> Registrierung des Health Checks in der API
    from app.api import health
    app.include_router(health.router)

    return app


app = create_app()
