import json
import logging.config
from utils.settings import settings
from typing import Optional, Dict, Any


class CustomFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "time": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "props": getattr(record, "props", ""),
            "thread": record.threadName,
            "process": record.process,
        })


# Define the logging schema
logging_schema: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": CustomFormatter
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "json",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "concurrent_log_handler.ConcurrentRotatingFileHandler",
            "filename": settings.log_file,
            "backupCount": 5,
            "maxBytes": 500_000_000,
            "use_gzip": False,
            "formatter": "json",
        },
    },
    "loggers": {
        "fastapi": {
            "handlers": settings.log_handlers,
            "level": logging.INFO,
            "propagate": True,
        }
    },
}


def changeLogFile(log_file: Optional[str] = None) -> None:
    if log_file:
        logging_schema["handlers"]["file"]["filename"] = log_file

