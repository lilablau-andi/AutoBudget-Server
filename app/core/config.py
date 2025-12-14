from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Zentrale Konfiguration für die FastAPI-Anwendung.
    Lädt Werte aus der .env-Datei im Projekt-Root.
    """

    # -------------------------------------------------
    # Allgemein
    # -------------------------------------------------
    PROJECT_NAME: str = "Personal Finance Manager"
    API_V1_STR: str = "/api/v1"

    # -------------------------------------------------
    # Supabase
    # -------------------------------------------------
    SUPABASE_URL: str
    SUPABASE_KEY: str
    DATABASE_URL: str

    # -------------------------------------------------
    # CORS
    # -------------------------------------------------
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
    ]

    # -------------------------------------------------
    # Pydantic v2 Konfiguration
    # -------------------------------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="forbid",
    )

# Singleton-Instanz
settings = Settings()
