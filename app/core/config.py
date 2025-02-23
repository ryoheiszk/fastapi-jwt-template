from pydantic_settings import BaseSettings
from dotenv import load_dotenv


load_dotenv()


class Settings(BaseSettings):
    BASE_URL: str = "/api"

    # Auth
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    MASTER_TOKEN: str

    ACCESS_TOKEN_EXPIRE_HOURS: int = 8760

    # Logging
    CONSOLE_LOG_LEVEL: str = "INFO"
    FILE_LOG_LEVEL: str = "DEBUG"
    LOG_DIR: str = "./logs"
    LOG_FILENAME: str = "app.log"

    class Config:
        case_sensitive = True


settings = Settings()
