from datetime import timedelta, datetime
from fastapi import APIRouter, Depends
import jwt

from app.utils.v1_auth import (
    verify_token,
    verify_master_token,
    create_token
)
from app.core.config import settings
from app.schemas.base import BaseResponse, ErrorResponse
from app.schemas.token import (
    TokenRequest,
    TokenResponse,
    TokenDecodeRequest,
    TokenPayload,
)

router = APIRouter()


@router.post("/token/generate", response_model=TokenResponse, summary="JWTトークンを生成する。")
async def generate_token(
    token_request: TokenRequest,
    _: None = Depends(verify_master_token)
):
    """
    - `MASTER_TOKEN` で認証してください。
    """
    try:
        expires_delta = (
            timedelta(hours=token_request.expire_hours)
            if token_request.expire_hours
            else None
        )
        token = create_token(
            username=token_request.username,
            expires_delta=expires_delta
        )
        return TokenResponse(data={"token": token})
    except Exception as e:
        return TokenResponse(errors=[ErrorResponse(message=str(e))])


@router.post("/token/decode", response_model=BaseResponse, summary="JWTトークンをデコードする。")
async def decode_token(
    token_request: TokenDecodeRequest,
    _: None = Depends(verify_master_token)
):
    """
    - `MASTER_TOKEN` で認証してください。
    - トークンが期限切れであっても実行します。
    """
    try:
        payload = jwt.decode(
            token_request.token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": False}
        )
        if "exp" not in payload or "iat" not in payload:
            raise jwt.InvalidTokenError("Token missing required fields")

        token_payload = TokenPayload(
            sub=payload["sub"],
            iat=datetime.fromtimestamp(payload["iat"]),
            exp=datetime.fromtimestamp(payload["exp"])
        )
        return BaseResponse(data=token_payload.model_dump())
    except jwt.InvalidTokenError as e:
        return BaseResponse(errors=[ErrorResponse(message=str(e))])
    except Exception as e:
        return BaseResponse(errors=[ErrorResponse(message=str(e))])


@router.get("/token/test", response_model=BaseResponse, summary="Tokenをテストする。")
async def test_token(payload: dict = Depends(verify_token)):
    try:
        return BaseResponse(data={
            "message": "You have access!",
            "sub": payload["sub"],
            "iat": datetime.fromtimestamp(payload["iat"]),
            "exp": datetime.fromtimestamp(payload["exp"])
        })
    except Exception as e:
        return BaseResponse(errors=[ErrorResponse(message=str(e))])
