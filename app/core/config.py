from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Sample"
    PROJECT_DESCRIPTION: str = "FastAPI sample with JWT authentication"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    BASE_URL: str = "/api"

    # Security
    SECRET_KEY: str = "mysecretkey"  # 本番環境では環境変数から取得すべき
    ALGORITHM: str = "HS256"
    MASTER_TOKEN: str = "master_token"  # 本番環境では環境変数から取得すべき
    ACCESS_TOKEN_EXPIRE_HOURS: int = 8760  # デフォルト1年

    class Config:
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
