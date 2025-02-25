import os
import sys
import logging
from logging import getLogger, StreamHandler, Formatter, Logger
from logging.handlers import RotatingFileHandler

from app.core.config import settings


class CustomLogger:
    """
    カスタムロガークラス

    コンソールとファイルの両方にログを出力します。
    """
    def __init__(self):
        self.log_dir = settings.LOG_DIR
        self.log_file = settings.LOG_FILENAME
        self.logger = getLogger("global_logger")

        # ログディレクトリが存在しない場合は作成
        os.makedirs(self.log_dir, exist_ok=True)

        # ログレベルを直接指定
        self.console_log_level = logging.INFO
        self.file_log_level = logging.DEBUG

        self._setup_logger()

    def _setup_logger(self) -> None:
        """
        ロガーの設定
        """
        # ログフォーマットの設定
        formatter = Formatter(
            "%(asctime)s | %(levelname)-8s | %(filename)s.%(funcName)s:%(lineno)d | %(message)s"
        )

        # コンソールハンドラーの設定
        console_handler = StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(self.console_log_level)

        # ファイルハンドラーの設定
        file_handler = RotatingFileHandler(
            os.path.join(self.log_dir, self.log_file),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(self.file_log_level)

        # ハンドラーの登録
        self.logger.handlers.clear()
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

        # ロガーのログレベルは最も低いレベルに設定
        self.logger.setLevel(logging.DEBUG)

    def get_logger(self) -> Logger:
        """
        設定済みのロガーインスタンスを取得
        """
        return self.logger


# グローバルなロガーインスタンスを作成
logger = CustomLogger().get_logger()
