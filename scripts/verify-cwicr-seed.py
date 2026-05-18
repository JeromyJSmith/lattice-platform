#!/usr/bin/env python3
"""Verify the live CWICR seed contract against release metadata and local Qdrant."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any

import httpx

QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333").rstrip("/")
COLLECTION = os.environ.get("CWICR_COLLECTION", "cwicr")
EXPECTED_POINT_COUNT = int(os.environ.get("CWICR_EXPECTED_POINT_COUNT", "55719"))
EXPECTED_VECTOR_SIZE = int(os.environ.get("CWICR_EXPECTED_VECTOR_SIZE", "3072"))
RELEASE_API_URL = os.environ.get(
    "CWICR_RELEASE_API_URL",
    "https://api.github.com/repos/datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR/releases/latest",
)
REQUEST_TIMEOUT_SECONDS = 20.0
SNAPSHOT_DIMENSION_RE = re.compile(r"(?:EMBEDDINGS_|embeddings_)(\d+)")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--collection", default=COLLECTION)
    return parser.parse_args()


def _fetch_json(url: str, *, method: str = "GET", json_body: dict[str, Any] | None = None) -> dict[str, Any]:
    response = httpx.request(
        method,
        url,
        json=json_body,
        timeout=REQUEST_TIMEOUT_SECONDS,
        headers={"Accept": "application/vnd.github+json"},
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError(f"expected JSON object from {url}")
    return payload


def _fetch_text(url: str) -> str:
    response = httpx.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.text


def _fetch_release_metadata() -> dict[str, Any]:
    payload = _fetch_json(RELEASE_API_URL)
    assets = payload.get("assets")
    if not isinstance(assets, list):
        raise RuntimeError("latest CWICR release payload is missing assets")
    snapshot_assets = [
        asset
        for asset in assets
        if isinstance(asset, dict) and str(asset.get("name", "")).endswith(".snapshot")
    ]
    if not snapshot_assets:
        raise RuntimeError("latest CWICR release does not expose any snapshot assets")

    dimensions = sorted(
        {
            int(match.group(1))
            for asset in snapshot_assets
            for match in [SNAPSHOT_DIMENSION_RE.search(str(asset.get("name", "")))]
            if match is not None
        }
    )
    return {
        "tag_name": payload.get("tag_name"),
        "name": payload.get("name"),
        "asset_count": len(assets),
        "snapshot_asset_count": len(snapshot_assets),
        "snapshot_assets": [
            {
                "name": asset.get("name"),
                "size": asset.get("size"),
                "browser_download_url": asset.get("browser_download_url"),
            }
            for asset in snapshot_assets[:5]
        ],
        "snapshot_dimensions": dimensions,
    }


def _probe_health() -> dict[str, Any]:
    root = _fetch_json(f"{QDRANT_URL}/")
    health_404 = False
    try:
        health = _fetch_json(f"{QDRANT_URL}/health")
        endpoint = "/health"
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code != 404:
            raise RuntimeError(f"Qdrant /health probe failed: {exc!s}") from exc
        health_404 = True
        health_text = _fetch_text(f"{QDRANT_URL}/healthz").strip()
        endpoint = "/healthz"
        health = {"status": "ok" if "passed" in health_text.lower() else health_text, "raw": health_text}
    return {
        "root": root,
        "health": health,
        "health_endpoint": endpoint,
        "health_404_fallback": health_404,
    }


def _extract_vector_size(collection_payload: dict[str, Any]) -> int | None:
    result = collection_payload.get("result")
    if not isinstance(result, dict):
        return None
    config = result.get("config")
    if not isinstance(config, dict):
        return None
    params = config.get("params")
    if not isinstance(params, dict):
        return None
    vectors = params.get("vectors")
    if isinstance(vectors, dict):
        size = vectors.get("size")
        return size if isinstance(size, int) else None
    return None


def _probe_collection(collection: str) -> dict[str, Any]:
    collection_payload = _fetch_json(f"{QDRANT_URL}/collections/{collection}")
    count_payload = _fetch_json(
        f"{QDRANT_URL}/collections/{collection}/points/count",
        method="POST",
        json_body={"exact": True},
    )
    result = collection_payload.get("result")
    count_result = count_payload.get("result")
    if not isinstance(result, dict):
        raise RuntimeError(f"Qdrant collection payload missing result for {collection}: {collection_payload}")
    if not isinstance(count_result, dict):
        raise RuntimeError(f"Qdrant count payload missing result for {collection}: {count_payload}")
    count = count_result.get("count")
    if not isinstance(count, int):
        raise RuntimeError(f"Qdrant count payload missing integer count for {collection}: {count_payload}")
    return {
        "collection": collection,
        "points_count": count,
        "indexed_vectors_count": result.get("indexed_vectors_count"),
        "vector_size": _extract_vector_size(collection_payload),
        "status": result.get("status"),
        "raw": {
            "collection": collection_payload,
            "count": count_payload,
        },
    }


def _evaluate_seed_contract(release: dict[str, Any], collection_state: dict[str, Any]) -> tuple[bool, list[str]]:
    blockers: list[str] = []

    snapshot_dimensions = release.get("snapshot_dimensions")
    if not isinstance(snapshot_dimensions, list) or not snapshot_dimensions:
        blockers.append("latest CWICR release does not expose a parseable snapshot vector dimension")
    elif EXPECTED_VECTOR_SIZE not in snapshot_dimensions:
        blockers.append(
            "latest CWICR release snapshot dimensions "
            f"{snapshot_dimensions} do not include the expected {EXPECTED_VECTOR_SIZE}-d contract"
        )

    observed_count = collection_state.get("points_count")
    if observed_count != EXPECTED_POINT_COUNT:
        blockers.append(
            f"collection {collection_state['collection']!r} has {observed_count} points; "
            f"expected {EXPECTED_POINT_COUNT}"
        )

    observed_vector_size = collection_state.get("vector_size")
    if observed_vector_size != EXPECTED_VECTOR_SIZE:
        blockers.append(
            f"collection {collection_state['collection']!r} uses vector size {observed_vector_size}; "
            f"expected {EXPECTED_VECTOR_SIZE}"
        )

    return not blockers, blockers


def _build_success_payload(release: dict[str, Any], qdrant: dict[str, Any], collection_state: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "passed",
        "collection": collection_state["collection"],
        "expected": {
            "points_count": EXPECTED_POINT_COUNT,
            "vector_size": EXPECTED_VECTOR_SIZE,
        },
        "release": release,
        "qdrant": qdrant,
        "collection_state": collection_state,
    }


def _build_failure_payload(
    release: dict[str, Any],
    qdrant: dict[str, Any],
    collection_state: dict[str, Any],
    blockers: list[str],
) -> dict[str, Any]:
    return {
        "status": "blocked",
        "collection": collection_state["collection"],
        "expected": {
            "points_count": EXPECTED_POINT_COUNT,
            "vector_size": EXPECTED_VECTOR_SIZE,
        },
        "release": release,
        "qdrant": qdrant,
        "collection_state": collection_state,
        "blockers": blockers,
        "resolution_hint": (
            "Restore a real 3072-d CWICR snapshot into the target collection or reseed it to "
            f"{EXPECTED_POINT_COUNT} points, then rerun this verifier."
        ),
    }


def main() -> int:
    """Execute the live CWICR seed verifier and exit non-zero when proof fails."""
    args = _parse_args()
    try:
        release = _fetch_release_metadata()
        qdrant = _probe_health()
        collection_state = _probe_collection(args.collection)
        ok, blockers = _evaluate_seed_contract(release, collection_state)
    except Exception as exc:
        print(
            json.dumps(
                {
                    "status": "blocked",
                    "collection": args.collection,
                    "blockers": [str(exc)],
                },
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1

    if not ok:
        print(
            json.dumps(
                _build_failure_payload(release, qdrant, collection_state, blockers),
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1

    print(
        json.dumps(
            _build_success_payload(release, qdrant, collection_state),
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
