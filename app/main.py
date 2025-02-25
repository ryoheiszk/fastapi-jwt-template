from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.exceptions import (
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler,
    CustomError,
    custom_error_handler
)
from app.api.v1.router import router as api_v1_router

app = FastAPI(
    title="FastAPI JWT Sample",
    description="FastAPI sample with JWT authentication",
    version="0.1.0",
    docs_url=f"{settings.BASE_URL}/docs",
    redoc_url=f"{settings.BASE_URL}/redoc",
    openapi_url=f"{settings.BASE_URL}/openapi.json",
)

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# グローバルな例外ハンドラーの登録
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(CustomError, custom_error_handler)
app.add_exception_handler(Exception, general_exception_handler)

# ルーターの登録
app.include_router(api_v1_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
