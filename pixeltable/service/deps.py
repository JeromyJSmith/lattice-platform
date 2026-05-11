"""FastAPI dependency providers."""

from __future__ import annotations

import logging
import os
from importlib import import_module
from pathlib import Path
from typing import Any

try:
    _fastapi = import_module("fastapi")
except ModuleNotFoundError as exc:  # pragma: no cover - environment wiring guard
    raise RuntimeError(
        "fastapi is required for pixeltable/service deps; run `uv sync` in `pixeltable/`."
    ) from exc

Header = _fastapi.Header
HTTPException = _fastapi.HTTPException
Request = _fastapi.Request

from service.idempotency import IdempotencyStore

log = logging.getLogger("vwbridge.deps")


def get_pxt(request: Request):
    return request.app.state.pxt


def get_settings(request: Request):
    return request.app.state.settings


def get_idem_store(request: Request) -> IdempotencyStore:
    return request.app.state.idem


def require_idempotency_key(idempotency_key: str | None = Header(default=None)) -> str:
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Idempotency-Key header required")
    if len(idempotency_key) > 256 or len(idempotency_key) < 8:
        raise HTTPException(status_code=400, detail="Idempotency-Key must be 8..256 chars")
    return idempotency_key


def require_local_socket_or_token(request: Request) -> None:
    """Cheap auth: when bound to UNIX socket on localhost, allow. When bound
    to TCP, require X-Bridge-Token == $PXT_BRIDGE_TOKEN.
    """
    socket = os.environ.get("PXT_BRIDGE_SOCKET")
    if socket:
        return
    token = os.environ.get("PXT_BRIDGE_TOKEN")
    if not token:
        return
    sent = request.headers.get("x-bridge-token", "")
    if sent != token:
        raise HTTPException(status_code=401, detail="bad bridge token")
