"""
app/core/logging.py

Production-grade structured JSON logging with optional Better Stack shipping.

Features:
- Structured JSON logs to stdout
- Optional Better Stack (Logtail) shipping
- Exception serialization with stack traces
- Request correlation support via `extra=`
- Safe/idempotent logger initialization
- Container/cloud-native friendly
"""

from __future__ import annotations

import json
import logging
import os
import socket
import sys
from datetime import datetime, timezone
from typing import Any

# Standard LogRecord attributes
# Used to separate custom `extra=` fields from built-in logging fields.

STANDARD_LOG_RECORD_ATTRS = {
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
    "message",
    "asctime",
    "taskName",
}


# JSON Formatter

class JSONFormatter(logging.Formatter):
    """
    Emits every log line as a structured JSON object.

    Example:
    {
        "timestamp": "...",
        "level": "INFO",
        "service": "f1-backend",
        "environment": "prod",
        "module": "prediction_service",
        "message": "Prediction completed",
        "request_id": "...",
        "latency_ms": 143
    }
    """

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created,
                tz=timezone.utc,
            ).isoformat(),
            "level": record.levelname,
            "service": os.getenv("SERVICE_NAME", "f1-backend"),
            "environment": os.getenv("ENVIRONMENT", "dev"),
            "hostname": socket.gethostname(),
            "module": record.module,
            "logger": record.name,
            "message": record.getMessage(),
        }

        STANDARD_ATTRS = {
            "name", "msg", "args", "levelname", "levelno",
            "pathname", "filename", "module", "exc_info",
            "exc_text", "stack_info", "lineno", "funcName",
            "created", "msecs", "relativeCreated", "thread",
            "threadName", "processName", "process", "message",
        }
        extra_fields = {k: v for k, v in record.__dict__.items() if k not in STANDARD_ATTRS}
        payload.update(extra_fields)

        # Attach serialized exception if present

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


# Better Stack / Logtail Handler

_BETTERSTACK_HANDLER: logging.Handler | None = None


def _get_betterstack_token() -> str | None:
    # Primary env var used by this repo
    token = os.environ.get("BETTERSTACK_TOKEN")
    if token:
        return token
    # Common alternative name used in Better Stack / Logtail docs
    return os.environ.get("LOGTAIL_SOURCE_TOKEN")


def _create_betterstack_handler() -> logging.Handler | None:
    """
    Creates Better Stack Logtail handler if configured.

    Returns:
        logging.Handler | None
    """

    token = _get_betterstack_token()

    if not token:
        return None

    try:
        from logtail import LogtailHandler  # type: ignore

        handler = LogtailHandler(source_token=token)

        handler.setLevel(logging.INFO)
        handler.setFormatter(JSONFormatter())

        return handler

    except ImportError:
        logging.getLogger(__name__).warning(
            "logtail-python not installed. "
            "Better Stack log shipping disabled."
        )
        return None

    except Exception:
        logging.getLogger(__name__).exception(
            "Failed to initialize Better Stack handler."
        )
        return None


def _get_or_create_betterstack_handler() -> logging.Handler | None:
    """Lazily creates Better Stack handler after env/.env is loaded."""
    global _BETTERSTACK_HANDLER
    if _BETTERSTACK_HANDLER is not None:
        return _BETTERSTACK_HANDLER
    _BETTERSTACK_HANDLER = _create_betterstack_handler()
    return _BETTERSTACK_HANDLER


# Logger Factory

def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured structured logger.

    Safe to call repeatedly:
    - No duplicate handlers
    - No duplicate logs

    Usage:
        logger = get_logger(__name__)

        logger.info(
            "Prediction completed",
            extra={
                "request_id": request_id,
                "driver_id": driver_id,
                "latency_ms": latency_ms,
            },
        )

        try:
            ...
        except Exception:
            logger.exception("Prediction failed")
    """

    logger = logging.getLogger(name)

    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()

    logger.setLevel(getattr(logging, log_level, logging.INFO))

    # Stdout JSON handler

    if not any(
        isinstance(h, logging.StreamHandler) and getattr(h, "stream", None) is sys.stdout
        for h in logger.handlers
    ):
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.DEBUG)
        stdout_handler.setFormatter(JSONFormatter())
        logger.addHandler(stdout_handler)

    # Optional Better Stack shipping
     

    betterstack_handler = _get_or_create_betterstack_handler()
    if betterstack_handler is not None and betterstack_handler not in logger.handlers:
        logger.addHandler(betterstack_handler)

    # Prevent propagation to root logger
    # Avoid duplicate logs under uvicorn/gunicorn-

    logger.propagate = False

    return logger