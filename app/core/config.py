import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv


# .envファイルを読み込む
load_dotenv()


class Settings(BaseSettings):
    """
    アプリケーション設定クラス
    """
    # API設定
    BASE_URL: str = "/api"
    PORT: int = int(os.getenv("PORT"))

    # 認証設定
    JWT_SECRET: str = os.getenv("JWT_SECRET")
    ALGORITHM: str = "HS256"
    MASTER_KEY: str = os.getenv("MASTER_KEY")
    ACCESS_TOKEN_EXPIRE_HOURS: int = 8760

    # ロギング設定
    LOG_DIR: str = "./logs"
    LOG_FILENAME: str = "app.log"

    class Config:
        case_sensitive = True
        env_file = ".env"


# 設定インスタンスを作成
settings = Settings()
