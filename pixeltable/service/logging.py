"""Structured logging helpers."""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from typing import Any

LOG_LEVEL = os.environ.get("PXT_BRIDGE_LOG_LEVEL", "INFO").upper()


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts":      time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(record.created)),
            "level":   record.levelname,
            "logger":  record.name,
            "message": record.getMessage(),
        }
        for k in ("request_id", "idempotency_key", "route", "vw_export_hash", "harness_run_id"):
            v = getattr(record, k, None)
            if v is not None:
                payload[k] = v
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure() -> None:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(LOG_LEVEL)
