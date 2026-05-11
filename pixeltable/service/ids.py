"""UUIDv7-style id generator (millisecond-sortable, random tail).

Pure-Python, no extra deps. Sufficient for our row-id needs since the
authoritative dedupe key is `Idempotency-Key`, not `id`.
"""

from __future__ import annotations

import os
import time
import uuid


def uuidv7() -> str:
    ts_ms = int(time.time() * 1000) & ((1 << 48) - 1)
    rand_a = int.from_bytes(os.urandom(2), "big") & 0x0FFF
    rand_b = int.from_bytes(os.urandom(8), "big") & ((1 << 62) - 1)
    raw = (
        (ts_ms << 80)
        | (0x7 << 76)
        | (rand_a << 64)
        | (0x2 << 62)
        | rand_b
    )
    return str(uuid.UUID(int=raw))
