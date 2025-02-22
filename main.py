from datetime import datetime, timedelta
from typing import Optional
from enum import Enum
import jwt
from fastapi import FastAPI, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from pydantic import BaseModel


BASE_URL = "/api"

app = FastAPI(
    title="FastAPI Sample",
    description="FastAPI sample with JWT authentication",
    version="0.1.0",
    docs_url=f"{BASE_URL}/docs",
    redoc_url=f"{BASE_URL}/redoc",
    openapi_url=f"{BASE_URL}/openapi.json",
)

router_v1_auth = APIRouter(tags=["v1 Auth"], prefix="/v1/auth")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 定数
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
MASTER_TOKEN = "master_token"


# エラーコード
class ErrorCode(str, Enum):
    INVALID_TOKEN = "AUTH001"
    TOKEN_EXPIRED = "AUTH002"
    INVALID_MASTER_KEY = "AUTH003"


# モデル
class TokenRequest(BaseModel):
    expire_hours: Optional[int] = 8760
    username: str = "user"


class TokenDecodeRequest(BaseModel):
    token: str


class ErrorModel(BaseModel):
    code: str
    message: str
    field: str = ""


class ResponseModel(BaseModel):
    data: dict = {}
    errors: list[ErrorModel] = []


# カスタム例外
class APIException(Exception):
    def __init__(self, status_code: int, code: str, message: str, field: str = ""):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.field = field


# エラーハンドラー
@app.exception_handler(APIException)
async def api_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "data": {},
            "errors": [{"code": exc.code, "message": exc.message, "field": exc.field}],
        },
    )


# Bearer認証
auth_scheme = HTTPBearer(auto_error=True)


def create_token(expire_hours: int, username: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=expire_hours)
    return jwt.encode(
        {"sub": username, "exp": expire, "iat": datetime.utcnow()},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise APIException(
            status_code=401,
            code=ErrorCode.TOKEN_EXPIRED,
            message="Token has expired",
            field="token",
        )
    except jwt.InvalidTokenError:
        raise APIException(
            status_code=401,
            code=ErrorCode.INVALID_TOKEN,
            message="Invalid token provided",
            field="token",
        )


@router_v1_auth.post("/token/generate", summary="Tokenを生成する。")
async def generate_token(
    token_request: TokenRequest, credentials=Security(auth_scheme)
):
    if credentials.credentials != MASTER_TOKEN:
        raise APIException(
            status_code=403,
            code=ErrorCode.INVALID_MASTER_KEY,
            message="Invalid master token",
            field="authorization",
        )

    token = create_token(token_request.expire_hours, token_request.username)
    return ResponseModel(data={"token": token})


@router_v1_auth.post("/token/decode", summary="Tokenをデコードする。")
async def decode_token(
    token_request: TokenDecodeRequest, credentials=Security(auth_scheme)
):
    """
    - `MASTER_TOKEN` を持つリクエストのみアクセス可能。
    - トークンが期限切れ (`exp` クレームが過去) であってもデコードを実行する。
    - トークンが不正な場合はエラーを返す。
    """
    if credentials.credentials != MASTER_TOKEN:
        raise APIException(
            status_code=403,
            code=ErrorCode.INVALID_MASTER_KEY,
            message="Invalid master token",
            field="authorization",
        )

    try:
        payload = jwt.decode(
            token_request.token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"verify_exp": False},
        )
    except jwt.InvalidTokenError:
        raise APIException(
            status_code=401,
            code=ErrorCode.INVALID_TOKEN,
            message="Invalid token provided",
            field="token",
        )

    return ResponseModel(
        data={
            "sub": payload.get("sub"),
            "exp": (
                datetime.fromtimestamp(payload["exp"]).isoformat()
                if "exp" in payload
                else "N/A"
            ),
            "iat": (
                datetime.fromtimestamp(payload["iat"]).isoformat()
                if "iat" in payload
                else "N/A"
            ),
        }
    )


@router_v1_auth.get("/token/test", summary="Tokenをテストする。")
async def protected(credentials=Security(auth_scheme)):
    verify_token(credentials.credentials)
    return ResponseModel(data={"message": "You have access!"})


app.include_router(router_v1_auth)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
