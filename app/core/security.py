from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError


security_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> str:
    """
    Liest die User-ID (sub) aus dem Supabase JWT.
    Signaturprüfung wird bewusst übersprungen (Uni-Projekt).
    """

    token = credentials.credentials

    try:
        # ❗ Signaturprüfung bewusst deaktiviert
        payload = jwt.decode(
            token,
            key=None,
            options={
                "verify_signature": False,
                "verify_aud": False,
            },
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token",
        )

    return user_id
