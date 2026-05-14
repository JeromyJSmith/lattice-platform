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
import os
import sys

QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
COLLECTION = os.environ.get("CWICR_COLLECTION", "cwicr")
EMBED_MODEL = os.environ.get("CWICR_EMBED_MODEL", "sentence-transformers/all-mpnet-base-v2")

_MODEL = None


def _get_model():
    global _MODEL
    if _MODEL is None:
        from sentence_transformers import SentenceTransformer

        _MODEL = SentenceTransformer(EMBED_MODEL)
    return _MODEL


def search(description: str, region: str, top: int) -> list[dict]:
    if not description.strip():
        raise ValueError("description is required")
    if top < 1:
        raise ValueError("top must be >= 1")

    from qdrant_client import QdrantClient
    from qdrant_client.http.models import FieldCondition, Filter, MatchValue

    model = _get_model()
    client = QdrantClient(url=QDRANT_URL)
    vector = model.encode(description, normalize_embeddings=True).tolist()
    hits = client.search(
        collection_name=COLLECTION,
        query_vector=vector,
        limit=top,
        query_filter=Filter(
            must=[FieldCondition(key="region", match=MatchValue(value=region))]
        ),
    )
    return [
        {
            "item_id": hit.payload.get("item_id"),
            "name": hit.payload.get("name"),
            "unit": hit.payload.get("unit"),
            "unit_cost": hit.payload.get("unit_cost"),
            "unit_currency": hit.payload.get("unit_currency", "USD"),
            "unit_cost_region": hit.payload.get("region", region),
            "score": hit.score,
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
