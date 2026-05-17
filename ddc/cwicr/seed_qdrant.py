#!/usr/bin/env python3
"""Seed a lightweight CWICR sample collection into local Qdrant.

This is intentionally small and idempotent so Wave-1 capability verification
can run in local/dev environments without external downloads.
"""

from __future__ import annotations

import math
import json
from hashlib import sha256
from urllib.error import HTTPError
from urllib.request import Request, urlopen

QDRANT_URL = "http://localhost:6333"
COLLECTION = "cwicr"
VECTOR_SIZE = 64

SAMPLE_ROWS = [
    {
        "item_id": "cwicr-concrete-slab-us",
        "name": "Concrete slab, reinforced",
        "unit": "m2",
        "unit_cost": 145.0,
        "unit_currency": "USD",
        "region": "US",
        "description": "reinforced concrete slab with labor and formwork",
    },
    {
        "item_id": "cwicr-asphalt-path-us",
        "name": "Asphalt pathway paving",
        "unit": "m2",
        "unit_cost": 52.0,
        "unit_currency": "USD",
        "region": "US",
        "description": "asphalt pathway with compaction and base layer",
    },
    {
        "item_id": "cwicr-topsoil-us",
        "name": "Topsoil placement and grading",
        "unit": "m3",
        "unit_cost": 38.0,
        "unit_currency": "USD",
        "region": "US",
        "description": "topsoil placement grading and finish preparation",
    },
    {
        "item_id": "cwicr-drainage-pipe-us",
        "name": "Perforated drainage pipe installation",
        "unit": "m",
        "unit_cost": 34.5,
        "unit_currency": "USD",
        "region": "US",
        "description": "perforated drainage pipe trench bedding and backfill",
    },
    {
        "item_id": "cwicr-steel-railing-us",
        "name": "Galvanized steel guard railing",
        "unit": "m",
        "unit_cost": 118.0,
        "unit_currency": "USD",
        "region": "US",
        "description": "galvanized steel guard railing posts and anchor bolts",
    },
]


def embed_text(text: str, size: int = VECTOR_SIZE) -> list[float]:
    """Small deterministic text embedding for local capability checks."""
    vec = [0.0] * size
    for token in text.lower().split():
        digest = sha256(token.encode("utf-8")).digest()
        idx = digest[0] % size
        sign = -1.0 if digest[1] % 2 else 1.0
        magnitude = 0.2 + (digest[2] / 255.0)
        vec[idx] += sign * magnitude
    norm = math.sqrt(sum(v * v for v in vec))
    if norm == 0:
        return vec
    return [v / norm for v in vec]


def _http(method: str, path: str, payload: dict | None = None) -> dict:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    req = Request(
        f"{QDRANT_URL}{path}",
        data=body,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urlopen(req) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except HTTPError as exc:
        msg = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Qdrant HTTP {exc.code}: {msg}") from exc


def _ensure_collection_http() -> None:
    data = _http("GET", "/collections")
    names = {c["name"] for c in data.get("result", {}).get("collections", [])}
    if COLLECTION in names:
        return
    _http(
        "PUT",
        f"/collections/{COLLECTION}",
        {"vectors": {"size": VECTOR_SIZE, "distance": "Cosine"}},
    )


def main() -> int:
    points = [
        {
            "id": idx + 1,
            "vector": embed_text(
                f"{row['name']} {row['description']} {row['region']} {row['unit']}"
            ),
            "payload": row,
        }
        for idx, row in enumerate(SAMPLE_ROWS)
    ]
    _ensure_collection_http()
    _http("PUT", f"/collections/{COLLECTION}/points", {"points": points})
    count_data = _http(
        "POST",
        f"/collections/{COLLECTION}/points/count",
        {"exact": True},
    )
    count = count_data.get("result", {}).get("count", 0)
    print(f"seeded {len(points)} points, collection_count={count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

