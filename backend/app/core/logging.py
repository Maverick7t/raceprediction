import logging
import json
import sys
from datetime import datetime, timezone


class _JSONFormatter(logging.Formatter):
    """
    Emits every log line as a single JSON object.
    Every line carries: timestamp, level, module, message.
    Exceptions are serialised into the same JSON object — never swallowed.
    """

    def format(self, record: logging.LogRecord) -> str:
        payload: dict = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "module": record.module,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "extra"):
            payload.update(record.extra)
        return json.dumps(payload)


def get_logger(name: str) -> logging.Logger:
    """
    Returns a module-level logger configured with JSON output.
    Calling this multiple times with the same name returns the same logger
    without adding duplicate handlers.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(_JSONFormatter())
        logger.addHandler(handler)
        logger.propagate = False

    # Allow LOG_LEVEL override from env without importing config
    # (avoids circular import — config imports nothing from core)
    import os
    level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, level, logging.INFO))

    return logger