# Token Validierung: Token prüfen, Payload lesen, user_id zurückgeben

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from app.core.config import settings


# FastAPI Security Scheme (Authorization: Bearer <token>)
security_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> str:
    """
    Validiert das Supabase JWT und gibt die User-ID zurück.
    """
    token = credentials.credentials

    try:
        # Supabase JWT validieren
        payload = jwt.decode(
            token,
            settings.SUPABASE_KEY,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    user_id: str | None = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication payload",
        )

    return user_id
