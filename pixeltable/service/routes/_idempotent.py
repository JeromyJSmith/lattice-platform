"""Helper to wrap a write-handler in idempotency replay logic."""

from __future__ import annotations

from typing import Any, Callable

from fastapi import Response

from service.idempotency import IdempotencyStore


def with_idempotency(
    store: IdempotencyStore,
    key: str,
    handler: Callable[[], dict[str, Any]],
) -> dict[str, Any]:
    cached = store.get(key)
    if cached:
        body = cached.get("body") or {}
        body = {**body, "idempotent_replay": True}
        return body
    out = handler()
    store.put(key, 200, out)
    return out
