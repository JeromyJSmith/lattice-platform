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
import sys


QDRANT_URL = "http://localhost:6333"
COLLECTION = "cwicr"
EMBED_MODEL = "sentence-transformers/all-mpnet-base-v2"


def search(description: str, region: str, top: int) -> list[dict]:
    """Embed description and query Qdrant for top-k matches.

    NOT YET IMPLEMENTED. Sketch (uncomment when seed-qdrant.sh has run):

    from sentence_transformers import SentenceTransformer
    from qdrant_client import QdrantClient
    from qdrant_client.http.models import Filter, FieldCondition, MatchValue

    model = SentenceTransformer(EMBED_MODEL)
    client = QdrantClient(url=QDRANT_URL)
    vec = model.encode(description).tolist()
    flt = Filter(must=[FieldCondition(key="region", match=MatchValue(value=region))])
    hits = client.search(
        collection_name=COLLECTION, query_vector=vec,
        limit=top, query_filter=flt,
    )
    return [
        {"item_id": h.payload["item_id"], "name": h.payload["name"],
         "unit": h.payload["unit"], "unit_cost": h.payload["unit_cost"],
         "unit_currency": h.payload["unit_currency"],
         "unit_cost_region": h.payload["region"], "score": h.score}
        for h in hits
    ]
    """
    raise NotImplementedError(
        "cost-search stub. Run ddc/cwicr/INSTALL.md steps first, then "
        "implement search() per the docstring sketch."
    )


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
