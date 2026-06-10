import json
import logging
from datetime import datetime, timezone
from typing import Any


class StructuredLogger:
    def __init__(self, name: str = "app", level: int = logging.INFO, log_file: str = "app.txt"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False
        self.logger.handlers.clear()

        formatter = logging.Formatter("%(message)s")

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)

        self.logger.addHandler(stream_handler)
        self.logger.addHandler(file_handler)

    def _log(self, level: int, message: str, **kwargs: Any) -> None:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": logging.getLevelName(level),
            "message": message,
            **kwargs,
        }
        self.logger.log(level, json.dumps(payload, ensure_ascii=False))

    def debug(self, message: str, **kwargs: Any) -> None:
        self._log(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        self._log(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        self._log(logging.ERROR, message, **kwargs)

    def exception(self, message: str, **kwargs: Any) -> None:
        kwargs["exception"] = True
        self._log(logging.ERROR, message, **kwargs)


logger = StructuredLogger("centauro_scraper", log_file="./app/temp/centauro_scraper.txt")

