"""service.idempotency.IdempotencyStore semantics."""

from __future__ import annotations

import time
from pathlib import Path

from service.idempotency import IdempotencyStore


def test_set_then_get_returns_value(tmp_path: Path):
    store = IdempotencyStore(path=tmp_path / "idem.json")
    store.put("k1", 200, {"ok": True})
    got = store.get("k1")
    assert got is not None
    assert got["status_code"] == 200
    assert got["body"] == {"ok": True}


def test_get_unknown_returns_none(tmp_path: Path):
    store = IdempotencyStore(path=tmp_path / "idem.json")
    assert store.get("nope") is None


def test_persists_across_instances(tmp_path: Path):
    disk = tmp_path / "idem.json"
    s1 = IdempotencyStore(path=disk)
    s1.put("persistent", 201, {"id": "abc"})

    s2 = IdempotencyStore(path=disk)
    got = s2.get("persistent")
    assert got is not None
    assert got["body"] == {"id": "abc"}


def test_body_sha_is_stable(tmp_path: Path):
    s1 = IdempotencyStore(path=tmp_path / "a.json")
    s2 = IdempotencyStore(path=tmp_path / "b.json")
    s1.put("k", 200, {"a": 1, "b": 2})
    s2.put("k", 200, {"b": 2, "a": 1})  # key order differs
    e1 = s1.get("k")
    e2 = s2.get("k")
    assert e1 is not None
    assert e2 is not None
    assert e1["body_sha256"] == e2["body_sha256"]
