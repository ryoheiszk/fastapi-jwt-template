import traceback
import os
from fastapi import Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.logger import logger
from app.schemas.base import ErrorResponse, BaseResponse

def log_full_traceback(exc):
    """
    例外の完全なスタックトレースをログに記録する

    Args:
        exc: 例外オブジェクト
    """
    tb_lines = traceback.format_exception(type(exc), exc, exc.__traceback__)
    tb_text = ''.join(tb_lines)
    logger.debug(f"Full traceback:\n{tb_text}")

def get_request_info(request):
    """
    リクエスト情報を取得する

    Args:
        request: FastAPIのRequestオブジェクト

    Returns:
        str: リクエスト情報（メソッドとパス）
    """
    return f"{request.method} {request.url.path}"

def get_caller_info(exc, request=None):
    """
    例外のスタックトレースから呼び出し元の情報を取得する

    Args:
        exc: 例外オブジェクト
        request: FastAPIのRequestオブジェクト（オプション）

    Returns:
        str: 呼び出し元の情報
    """
    # 完全なスタックトレースをデバッグログに記録
    log_full_traceback(exc)

    # リクエスト情報を取得
    req_info = get_request_info(request) if request else "unknown request"

    if not exc.__traceback__:
        return f"{req_info} (unknown location)"

    # スタックトレースを取得
    tb_frames = traceback.extract_tb(exc.__traceback__)

    # FastAPIの内部フレームとミドルウェアフレームを除外
    skip_patterns = (
        'exceptions.py',
        'middleware.py',
        '_exception_handler.py',
        'fastapi',
        'starlette',
        'uvicorn'
    )

    # アプリケーションコードのフレームを抽出
    app_frames = []
    for frame in tb_frames:
        if not any(pattern in frame.filename for pattern in skip_patterns):
            app_frames.append(frame)

    # アプリケーションコードのフレームが見つからない場合は、すべてのフレームを使用
    frames_to_check = app_frames if app_frames else tb_frames

    # フレームが見つからない場合
    if not frames_to_check:
        return f"{req_info} (unknown location)"

    # フレーム情報を構築
    frame_infos = []
    for frame in frames_to_check[:3]:  # 最大3つのフレームを表示
        filename = os.path.basename(frame.filename)
        if frame.name:
            frame_infos.append(f"{filename}:{frame.lineno} in {frame.name}()")
        else:
            frame_infos.append(f"{filename}:{frame.lineno}")

    return f"{req_info} at {' -> '.join(frame_infos)}"

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    リクエストバリデーションエラーのハンドラー
    """
    caller_info = get_caller_info(exc, request)
    logger.error(f"Validation error at {caller_info}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=BaseResponse(
            errors=[ErrorResponse(message=str(err["msg"])) for err in exc.errors()]
        ).model_dump(),
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """
    HTTPExceptionのハンドラー
    """
    caller_info = get_caller_info(exc, request)
    logger.error(f"HTTP exception at {caller_info}: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=BaseResponse(
            errors=[ErrorResponse(message=exc.detail)]
        ).model_dump(),
    )

async def general_exception_handler(request: Request, exc: Exception):
    """
    一般的な例外のハンドラー
    """
    caller_info = get_caller_info(exc, request)
    logger.error(f"Unhandled exception at {caller_info}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=BaseResponse(
            errors=[ErrorResponse(message="Internal server error")]
        ).model_dump(),
    )

# カスタム例外クラス
# 注: 標準的なHTTPエラーにはHTTPExceptionを使用することを推奨
class CustomError(Exception):
    """カスタムエラーの基底クラス"""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)

# CustomErrorハンドラー
async def custom_error_handler(request: Request, exc: CustomError):
    """
    カスタムエラーのハンドラー
    """
    caller_info = get_caller_info(exc, request)
    logger.error(f"Custom error at {caller_info}: {exc.status_code} - {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=BaseResponse(
            errors=[ErrorResponse(message=exc.message)]
        ).model_dump(),
    )
