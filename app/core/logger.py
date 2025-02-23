import os
import sys
from logging import getLogger, StreamHandler, Formatter, Logger
from logging.handlers import RotatingFileHandler
from typing import Optional

from app.core.config import settings


class CustomLogger:
    """カスタムロガークラス

    環境変数で設定可能なロギング機能を提供します。
    コンソールとファイルの両方にログを出力し、ファイルは自動的にローテーションします。
    """

    def __init__(
        self,
        name: Optional[str] = None,
    ):
        """
        Args:
            name: ロガー名。Noneの場合はルートロガーを使用
        """
        self.log_dir = settings.LOG_DIR
        self.log_file = settings.LOG_FILENAME
        self.logger = getLogger(name or settings.PROJECT_NAME.lower().replace(" ", "-"))

        # ログディレクトリが存在しない場合は作成
        os.makedirs(self.log_dir, exist_ok=True)

        # 環境変数からログレベルを取得
        self.console_log_level = settings.CONSOLE_LOG_LEVEL
        self.file_log_level = settings.FILE_LOG_LEVEL

        self._setup_logger()

    def _setup_logger(self) -> None:
        """ロガーの設定を行います"""
        # フォーマッターの作成
        formatter = Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s.%(funcName)s:%(lineno)d | %(message)s"
        )

        # コンソールハンドラの設定
        console_handler = StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(self.console_log_level)

        # ファイルハンドラの設定
        file_handler = RotatingFileHandler(
            os.path.join(self.log_dir, self.log_file),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(self.file_log_level)

        # 既存のハンドラをクリア
        self.logger.handlers.clear()

        # 新しいハンドラを追加
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

        # ロガーの基本レベルをDEBUGに設定（全てのログをキャプチャ）
        self.logger.setLevel("DEBUG")

    def get_logger(self) -> Logger:
        """設定済みのロガーを返します

        Returns:
            Logger: 設定済みのロガーインスタンス
        """
        return self.logger


# グローバルなロガーインスタンスを作成
logger = CustomLogger().get_logger()
