from datetime import datetime
from pydantic import BaseModel, Field

from app.schemas.base import BaseResponse


class TokenRequest(BaseModel):
    expire_hours: int = Field(..., example=8760)
    username: str = Field(..., example="user")


class TokenDecodeRequest(BaseModel):
    token: str


class TokenPayload(BaseModel):
    sub: str
    exp: datetime
    iat: datetime


class TokenResponse(BaseResponse):
    data: dict = {"token": ""}
