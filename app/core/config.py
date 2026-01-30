# Konfigurationsdatei für das ganze Projekt.
# Autor: Andrej Bobb

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Zentrale Konfiguration für die FastAPI-Anwendung.
    Lädt Werte aus der .env-Datei im Projekt-Root.
    """

    # -------------------------------------------------
    # Allgemein: Projektname und Adresse der API
    # -------------------------------------------------
    PROJECT_NAME: str = "Personal Finance Manager"
    API_V1_STR: str = "/api/v1"

    # -------------------------------------------------
    # Supabase: Typ-Setzung für die SUPABASE Konfiguration
    # -------------------------------------------------
    SUPABASE_URL: str
    SUPABASE_KEY: str
    DATABASE_URL: str

    # -------------------------------------------------
    # CORS: Diese Konfiguration erlaubt unserem Frontend 
    # auf die API zuzugreifen. Wichtig ist, dass das Frontend
    # unter dem Port 3000 läuft. Ohne das wird automatisch
    # geblockt. 
    # -------------------------------------------------
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
    ]

    # -------------------------------------------------
    # Pydantic v2 Konfiguration. Pydantic ist für Typ- und 
    # Datenvalidierung, damit wir mit sauberen Python-Objekten
    # arbeiten. Außerdem werden hier die .env Variablen gelesen.
    # -------------------------------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="forbid",
    )

settings = Settings()