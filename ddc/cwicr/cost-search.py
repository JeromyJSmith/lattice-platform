#!/usr/bin/env python3
"""Semantic cost search against the local Qdrant CWICR collection.

Usage:
    python3 cost-search.py "<element description>" [--region US] [--top 5]

Output: JSON array on stdout, one object per match:
    [{ "item_id": "...", "name": "...", "unit": "m2",
       "unit_cost": 47.50, "unit_currency": "USD",
       "unit_cost_region": "US", "score": 0.81 }, ...]

Tracked in meta/FEATURE_BACKLOG.md § DDC INTEGRATION → "CWICR cost search".

Stub. See INSTALL.md and the acceptance criteria on the matching GitHub issue
("Setup: CWICR Qdrant in OrbStack Ubuntu VM").
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from hashlib import sha256
from urllib.error import HTTPError
from urllib.request import Request, urlopen

QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
COLLECTION = os.environ.get("CWICR_COLLECTION", "cwicr")
VECTOR_SIZE = int(os.environ.get("CWICR_VECTOR_SIZE", "64"))


def _embed_text(text: str, size: int = VECTOR_SIZE) -> list[float]:
    """Deterministic local embedding compatible with seed_qdrant.py."""
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


def search(description: str, region: str, top: int) -> list[dict]:
    if not description.strip():
        raise ValueError("description is required")
    if top < 1:
        raise ValueError("top must be >= 1")

    vector = _embed_text(description)
    payload = {
        "vector": vector,
        "limit": top,
        "filter": {
            "must": [
                {"key": "region", "match": {"value": region}},
            ]
        },
        "with_payload": True,
        "with_vector": False,
    }
    req = Request(
        f"{QDRANT_URL}/collections/{COLLECTION}/points/search",
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urlopen(req) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        err = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"qdrant search failed ({exc.code}): {err}") from exc

    hits = body.get("result", []) or []
    return [
        {
            "item_id": (hit.get("payload") or {}).get("item_id"),
            "name": (hit.get("payload") or {}).get("name"),
            "unit": (hit.get("payload") or {}).get("unit"),
            "unit_cost": (hit.get("payload") or {}).get("unit_cost"),
            "unit_currency": (hit.get("payload") or {}).get("unit_currency", "USD"),
            "unit_cost_region": (hit.get("payload") or {}).get("region", region),
            "score": hit.get("score"),
        }
        for hit in hits
    ]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("description", help="Element description, free-form text")
    p.add_argument("--region", default="US", help="Region code (e.g. US, DE, UK, JP)")
    p.add_argument("--top", type=int, default=5, help="How many matches to return")
    args = p.parse_args()
    try:
        out = search(args.description, args.region, args.top)
    except NotImplementedError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2
    json.dump(out, sys.stdout, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
