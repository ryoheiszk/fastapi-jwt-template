from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings
from app.core.logger import logger
from app.schemas.token import TokenPayload

security = HTTPBearer()


def create_token(username: str, expires_delta: timedelta = None) -> str:
    """
    指定されたユーザー名とオプションの有効期限でJWTトークンを生成します。

    Args:
        username: トークンに含めるユーザー名
        expires_delta: トークンの有効期限（指定がない場合はデフォルト値を使用）

    Returns:
        生成されたJWTトークン
    """
    if expires_delta is None:
        expires_delta = timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)

    expire = datetime.utcnow() + expires_delta

    to_encode = {
        "sub": username,
        "exp": expire,
        "iat": datetime.utcnow()
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """
    JWTトークンを検証し、ペイロードを返します。

    Args:
        credentials: HTTPAuthorizationCredentials

    Returns:
        検証されたトークンのペイロード

    Raises:
        HTTPException: トークンが無効または期限切れの場合
    """
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError as e:
        logger.error(f"Token has expired: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_master_key(credentials: HTTPAuthorizationCredentials = Security(security)) -> None:
    """
    マスタートークンを検証します。

    Args:
        credentials: HTTPAuthorizationCredentials

    Raises:
        HTTPException: マスタートークンが無効の場合
    """
    if credentials.credentials != settings.MASTER_KEY:
        logger.error(f"Invalid master token")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid master token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def decode_token_with_payload(token: str, verify_exp: bool = True) -> TokenPayload:
    """
    JWTトークンをデコードし、TokenPayloadオブジェクトを返します。

    Args:
        token: デコードするJWTトークン
        verify_exp: 有効期限を検証するかどうか

    Returns:
        TokenPayloadオブジェクト

    Raises:
        jwt.InvalidTokenError: トークンが無効の場合
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
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
        logger.error(f"Invalid token: {str(e)}")
        raise jwt.InvalidTokenError(str(e))
