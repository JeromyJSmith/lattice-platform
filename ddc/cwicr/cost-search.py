#!/usr/bin/env python3
"""Semantic cost search against the local Qdrant CWICR collection.

Usage:
    python3 cost-search.py "<element description>" [--region US] [--top 5]

Output: JSON array on stdout, one object per match:
    [{ "item_id": "...", "name": "...", "unit": "m2",
       "unit_cost": 47.50, "unit_currency": "USD",
       "unit_cost_region": "US", "score": 0.81 }, ...]

Score interpretation used by the LATTICE ERP route:
    score >= 0.55   reliable candidate for verified automation
    score >= 0.25   review-only candidate, not verified proof
    score < 0.25    weak candidate, not usable proof

This helper returns ranked hits only. API-layer callers should apply
confidence classification before presenting the result as proof.

Tracked in meta/FEATURE_BACKLOG.md § DDC INTEGRATION → "CWICR cost search".

Stub. See INSTALL.md and the acceptance criteria on the matching GitHub issue
("Setup: CWICR Qdrant in OrbStack Ubuntu VM").
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from urllib import error, request

QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333").rstrip("/")
COLLECTION = os.environ.get("CWICR_COLLECTION", "cwicr")
OPENAI_EMBED_MODEL = "text-embedding-3-large"
EMBED_MODEL = os.environ.get("CWICR_EMBED_MODEL", OPENAI_EMBED_MODEL)
DEFAULT_UNIT_CURRENCY = os.environ.get("CWICR_UNIT_CURRENCY", "EUR")
REQUEST_TIMEOUT_SECONDS = 30.0

_MODEL = None


def _get_model():
    global _MODEL
    if _MODEL is None:
        from sentence_transformers import SentenceTransformer

        _MODEL = SentenceTransformer(EMBED_MODEL)
    return _MODEL


def _request_json(method: str, path: str, *, json_body: dict | None = None) -> dict:
    data = None if json_body is None else json.dumps(json_body).encode("utf-8")
    headers = {"Content-Type": "application/json"} if json_body is not None else {}
    req = request.Request(f"{QDRANT_URL}{path}", data=data, headers=headers, method=method)
    try:
        with request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {path} failed with HTTP {exc.code}: {body}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"{method} {path} failed: {exc.reason}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"{method} {path} returned non-object payload")
    return payload


def _fetch_collection_contract() -> dict[str, object]:
    payload = _request_json("GET", f"/collections/{COLLECTION}")
    result = payload.get("result")
    if not isinstance(result, dict):
        raise RuntimeError(f"collection {COLLECTION!r} payload missing result: {payload}")
    config = result.get("config")
    if not isinstance(config, dict):
        raise RuntimeError(f"collection {COLLECTION!r} payload missing config: {payload}")
    params = config.get("params")
    if not isinstance(params, dict):
        raise RuntimeError(f"collection {COLLECTION!r} payload missing params: {payload}")
    vectors = params.get("vectors")
    if not isinstance(vectors, dict):
        raise RuntimeError(f"collection {COLLECTION!r} payload missing vector config: {payload}")
    vector_size = vectors.get("size")
    if not isinstance(vector_size, int):
        raise RuntimeError(f"collection {COLLECTION!r} vector size is not an integer: {payload}")
    return {
        "collection": COLLECTION,
        "vector_size": vector_size,
        "status": result.get("status"),
    }


def _encode_query(description: str, *, expected_dimensions: int) -> list[float]:
    if EMBED_MODEL == OPENAI_EMBED_MODEL:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise NotImplementedError(
                "CWICR cost search blocked: live collection "
                f"{COLLECTION!r} uses OpenAI 3072d embeddings but OPENAI_API_KEY is not configured."
            )
        raise NotImplementedError(
            "CWICR cost search blocked: OpenAI embedding requests are not wired in this runtime yet."
        )

    model = _get_model()
    vector = model.encode(description, normalize_embeddings=True).tolist()
    if len(vector) != expected_dimensions:
        raise NotImplementedError(
            "CWICR cost search blocked: embed model "
            f"{EMBED_MODEL!r} produced {len(vector)} dimensions, but collection "
            f"{COLLECTION!r} requires {expected_dimensions}."
        )
    return vector


def _first_string(*values: object) -> str | None:
    for value in values:
        if isinstance(value, str):
            normalized = value.strip()
            if normalized:
                return normalized
    return None


def _first_number(*values: object) -> float | None:
    for value in values:
        if isinstance(value, bool):
            continue
        if isinstance(value, int | float):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value.strip())
            except ValueError:
                continue
    return None


def _normalize_hit(hit: object, region: str) -> dict:
    payload = getattr(hit, "payload", None)
    if not isinstance(payload, dict):
        payload = {}
    metadata = payload.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}
    payload_full = payload.get("payload_full")
    if not isinstance(payload_full, dict):
        payload_full = {}
    cost_summary = payload_full.get("cost_summary")
    if not isinstance(cost_summary, dict):
        cost_summary = {}
    return {
        "item_id": _first_string(
            payload_full.get("rate_code"),
            metadata.get("doc_id"),
            metadata.get("original_id"),
            metadata.get("point_uuid"),
            getattr(hit, "id", None),
        ),
        "name": _first_string(payload_full.get("rate_name"), metadata.get("names")),
        "unit": _first_string(payload_full.get("rate_unit"), metadata.get("unit")),
        "unit_cost": _first_number(cost_summary.get("total_cost_position")),
        "unit_currency": DEFAULT_UNIT_CURRENCY,
        "unit_cost_region": region,
        "score": getattr(hit, "score", None),
    }


def search(description: str, region: str, top: int) -> list[dict]:
    """Query the live CWICR collection and normalize ranked matches for the ERP route."""
    if not description.strip():
        raise ValueError("description is required")
    if top < 1:
        raise ValueError("top must be >= 1")

    from qdrant_client import QdrantClient
    collection_contract = _fetch_collection_contract()
    vector_size = collection_contract["vector_size"]
    if not isinstance(vector_size, int):
        raise RuntimeError(f"collection {COLLECTION!r} did not report an integer vector size")
    vector = _encode_query(description, expected_dimensions=vector_size)
    client = QdrantClient(url=QDRANT_URL)
    response = client.query_points(
        collection_name=COLLECTION,
        query=vector,
        limit=top,
        with_payload=True,
        with_vectors=False,
    )
    hits = response.points if hasattr(response, "points") else []
    return [_normalize_hit(hit, region) for hit in hits]


def main() -> int:
    """Run the local CWICR search helper as a small CLI."""
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
