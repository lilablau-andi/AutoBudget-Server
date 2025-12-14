from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db

router = APIRouter()

@router.get("/health", tags=["Health"], status_code=status.HTTP_200_OK)
def health_check(db: Session = Depends(get_db)):
    """
    Führt einen einfachen Health Check durch.
    Prüft auch die Datenbankverbindung.
    """
    try:
        # Einfache DB-Abfrage um Verbindung zu prüfen
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "online"}
    except Exception as e:
        # Hier könnte man strukturiertes Logging verwenden
        print(f"Health Check DB Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unreachable"
        )
