from typing import List
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    message: str


class BaseResponse(BaseModel):
    data: dict = {}
    errors: List[ErrorResponse] = []
