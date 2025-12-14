from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    # Allgemein
    PROJECT_NAME: str = "Personal Finance Manager"
    API_V1_STR: str = "/api/v1"

    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="forbid",  # absichtlich streng
    )

settings = Settings()