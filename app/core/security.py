# Auth Datei. Jeder Endpoint weiß, welcher User gerade anfragt. 
# Das läuft über Depends(get_current_user) in den API Dateien.
# Autor: Andrej Bobb

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

# Standardfunktion um Autorization auszulesen
security_scheme = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme), #Standard Supabase Config
) -> str:
    """
    Liest die User-ID (sub) aus dem Supabase JWT.
    """

    token = credentials.credentials

    # Wir gleichen den JWT ab
    try:
        payload = jwt.decode(
            token,
            key="",
            options={
                "verify_signature": False,
                "verify_aud": False,
            },
        )
    except JWTError: #Fehler Unautorisiert, wenn JWT nicht passt
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültiger Token",
        )

    # Wir suchen die user_id im geliefertem Payload
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID nicht im token gefunden",
        )

    return user_id
