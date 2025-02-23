import os
import sys
import logging
from logging import getLogger, StreamHandler, Formatter, Logger
from logging.handlers import RotatingFileHandler


class CustomLogger:
    def __init__(self):
        self.log_dir = "./logs"
        self.log_file = "app.log"
        self.logger = getLogger("global_logger")

        os.makedirs(self.log_dir, exist_ok=True)

        self.console_log_level = logging.INFO
        self.file_log_level = logging.DEBUG

        self._setup_logger()

    def _setup_logger(self) -> None:
        formatter = Formatter(
            "%(asctime)s | %(levelname)-8s | %(filename)s.%(funcName)s:%(lineno)d | %(message)s"
        )

        console_handler = StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(self.console_log_level)

        file_handler = RotatingFileHandler(
            os.path.join(self.log_dir, self.log_file),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(self.file_log_level)

        self.logger.handlers.clear()
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

        self.logger.setLevel("DEBUG")

    def get_logger(self) -> Logger:
        return self.logger


# グローバルなロガーインスタンスを作成
logger = CustomLogger().get_logger()
