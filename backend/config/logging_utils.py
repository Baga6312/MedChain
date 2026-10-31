import json
import logging
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": getattr(record, "service", record.name),
            "environment": getattr(record, "environment", None),
            "message": record.getMessage(),
        }
        if payload["environment"] is None:
            payload.pop("environment")
        for field in ("request_id", "method", "path", "status", "duration_ms", "user_id"):
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=True)


def build_logging_config(level, environment, log_file_path):
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": "config.logging_utils.JsonFormatter",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": "json",
            },
            "file": {
                "class": "logging.handlers.WatchedFileHandler",
                "filename": log_file_path,
                "formatter": "json",
            },
        },
        "loggers": {
            "": {"handlers": ["console", "file"], "level": level},
            "django.request": {"handlers": ["console", "file"], "level": "ERROR", "propagate": False},
            "gunicorn.error": {"handlers": ["console", "file"], "level": "INFO", "propagate": False},
            "gunicorn.access": {"handlers": ["console", "file"], "level": "INFO", "propagate": False},
        },
    }
