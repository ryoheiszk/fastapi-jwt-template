from typing import List, Dict, Any
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    code: str
    detail: str


class BaseResponse(BaseModel):
    data: Dict[str, Any] = {}
    errors: List[ErrorResponse] = []
