from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException

from app.auth.jwt import (
    verify_token,
    verify_master_token,
    create_token,
    decode_token_with_payload
)
from app.core.logger import logger
from app.schemas.base import BaseResponse, ErrorResponse
from app.schemas.token import (
    TokenRequest,
    TokenResponse,
    TokenDecodeRequest
)

router = APIRouter()


@router.post("/generate", response_model=TokenResponse, summary="JWTトークンを生成する。")
async def generate_token(
    token_request: TokenRequest,
    _: None = Depends(verify_master_token)
):
    """
    マスタートークンで認証してJWTトークンを生成します。

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
        logger.debug(f"Token generated: {token_request.expire_hours}hours, {token}")
        return TokenResponse(data={"token": token})
    except Exception as e:
        logger.error(f"Token generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Token generation failed: {str(e)}"
        )


@router.post("/decode", response_model=BaseResponse, summary="JWTトークンをデコードする。")
async def decode_token(
    token_request: TokenDecodeRequest,
    _: None = Depends(verify_master_token)
):
    """
    マスタートークンで認証してJWTトークンをデコードします。

    - `MASTER_TOKEN` で認証してください。
    - トークンが期限切れでも実行します。
    """
    try:
        token_payload = decode_token_with_payload(token_request.token, verify_exp=False)
        return BaseResponse(data=token_payload.model_dump())
    except Exception as e:
        logger.error(f"Token decode failed: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Token decode failed: {str(e)}"
        )


@router.get("/test", response_model=BaseResponse, summary="Tokenをテストする。")
async def test_token(payload: dict = Depends(verify_token)):
    """
    生成したトークンで認証をテストします。

    - 生成したトークンで認証してください。
    """
    try:
        return BaseResponse(data={
            "message": "You have access!",
            "sub": payload["sub"],
            "iat": datetime.fromtimestamp(payload["iat"]),
            "exp": datetime.fromtimestamp(payload["exp"])
        })
    except Exception as e:
        logger.error(f"Token test failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Token test failed: {str(e)}"
        )
