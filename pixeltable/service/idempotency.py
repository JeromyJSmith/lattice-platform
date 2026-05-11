"""In-memory + on-disk idempotency cache.

We cache `Idempotency-Key -> {status_code, body_sha256, timestamp}` for 24h.
On hit, return the previously recorded status. On disk, we sweep entries
older than 24h on each startup.
"""

from __future__ import annotations

import hashlib
import json
import threading
import time
from pathlib import Path
from typing import Any

_TTL_S = 24 * 60 * 60
_LOCK = threading.Lock()


class IdempotencyStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._mem: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        cutoff = time.time() - _TTL_S
        try:
            raw = json.loads(self.path.read_text())
        except Exception:
            return
        self._mem = {k: v for k, v in raw.items() if v.get("ts", 0) >= cutoff}
        self._flush()

    def _flush(self) -> None:
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self._mem, default=str))
        tmp.replace(self.path)

    def get(self, key: str) -> dict[str, Any] | None:
        with _LOCK:
            entry = self._mem.get(key)
            if not entry:
                return None
            if time.time() - entry.get("ts", 0) > _TTL_S:
                self._mem.pop(key, None)
                self._flush()
                return None
            return entry

    def put(self, key: str, status_code: int, body: dict[str, Any]) -> None:
        with _LOCK:
            self._mem[key] = {
                "status_code": status_code,
                "body_sha256": hashlib.sha256(
                    json.dumps(body, sort_keys=True, default=str).encode()
                ).hexdigest(),
                "body":        body,
                "ts":          time.time(),
            }
            self._flush()
