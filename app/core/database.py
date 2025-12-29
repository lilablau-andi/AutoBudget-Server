#DB Connection, Engine, Session/Connection Bereitstellen

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings


# -------------------------------------------------
# SQLAlchemy Base
# -------------------------------------------------

class Base(DeclarativeBase):
    """
    Basisklasse für alle ORM-Modelle.
    """
    pass


# -------------------------------------------------
# Engine
# -------------------------------------------------

engine = create_engine(
    settings.DATABASE_URL,

    # --- Pool-Stabilität ---
    pool_pre_ping=True,        # prüft Connection vor Nutzung
    pool_recycle=1800,         # 🔥 zwingend (30 Minuten)
    pool_size=5,               # Grundpool
    max_overflow=10,           # Peak-Last
    pool_timeout=10,           # schneller Fehler statt Hängen

    # --- Debug ---
    echo=False,

    # --- Netzwerk ---
    connect_args={
        "connect_timeout": 5,
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
        "application_name": "fastapi-api",  # 🔍 extrem hilfreich in Supabase Logs
    },
)


# -------------------------------------------------
# Session Factory
# -------------------------------------------------

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


# -------------------------------------------------
# Dependency für FastAPI
# -------------------------------------------------

def get_db():
    """
    Stellt eine DB-Session für einen Request bereit.
    Wird via Depends() in Endpoints verwendet.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
