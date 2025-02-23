from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings
from app.schemas.token import TokenPayload

security = HTTPBearer()


def create_token(username: str, expires_delta: timedelta) -> str:
    expire = datetime.utcnow() + expires_delta

    to_encode = {
        "sub": username,
        "exp": expire,
        "iat": datetime.utcnow()
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_master_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> None:
    if credentials.credentials != settings.MASTER_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid master token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def decode_token_with_payload(token: str, verify_exp: bool = False) -> TokenPayload:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": verify_exp}
        )
        if "exp" not in payload or "iat" not in payload:
            raise jwt.InvalidTokenError("Token missing required fields")

        return TokenPayload(
            sub=payload["sub"],
            iat=datetime.fromtimestamp(payload["iat"]),
            exp=datetime.fromtimestamp(payload["exp"])
        )
    except jwt.InvalidTokenError as e:
        raise jwt.InvalidTokenError(str(e))
