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
    pool_pre_ping=True,   # prüft Verbindungen automatisch
    echo=False,           # auf True setzen für SQL-Debugging
    connect_args={
        "connect_timeout": 10,
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    }
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
