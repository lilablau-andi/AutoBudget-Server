# DB Verbindung Session/Connection Bereitstellen
# Autor: Andrej Bobb

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings


# -------------------------------------------------
# SQLAlchemy Base. SQLAlchemy ist unser ORM, damit wir
# in Python-Code mit der Datenbank sprechen können, anstatt
# SQL zu nutzen.
# -------------------------------------------------

class Base(DeclarativeBase):
    """
    Basisklasse für alle ORM-Modelle.
    """
    pass


# -------------------------------------------------
# Engine: Fundament für das DB-System. Die Engine
# kennt die DB Adresse und führt das SQL aus.
# -------------------------------------------------

engine = create_engine(
    settings.DATABASE_URL,

    # --- Pool-Stabilität ---
    # Ein Pool ist eine Sammlung offener Datenbankverbindungen, 
    # Verbindungen bleiben offen, somit höhere Schnelligkeit und weniger Timeouts
    pool_pre_ping=True,        # prüft Connection vor Nutzung
    pool_recycle=1800,         # Pools dürfen nur max 30 Min alt sein. Idle-TCP Verbindungen werden automatisch geschlossen
    pool_size=5,               # Grundpool
    max_overflow=10,           # Peak-Last
    pool_timeout=10,           # schneller Fehler statt Hängen

    # --- Debug ---
    echo=False,

    # --- Netzwerk ---
    # Netzwerkkonfiguration
    connect_args={
        "connect_timeout": 5, #Maximale Zeit, um DB Verbindung aufzubauen
        "keepalives": 1, #Aktive TCP Kanäle
        "keepalives_idle": 30, #Nach 30 Inaktivität-Sekunden wird gepingt 
        "keepalives_interval": 10, #Abstand zwischen Keepalive-Pings, 10 Sek.
        "keepalives_count": 5, #Wie oft wird gepingt, bevor Verbindung tot ist.
        "application_name": "fastapi-api", 
    },
)


# -------------------------------------------------
# Session: Standardparameter für SQLAlchemy. 
# Wir sprechen quasi immer nur mit einer Session und nie direkt 
# mit der Engine
# -------------------------------------------------

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


# -------------------------------------------------
# Dependency für FastAPI. FastAPI erstellt die Session und macht die API Nutzbar
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
