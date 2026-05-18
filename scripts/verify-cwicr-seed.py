#!/usr/bin/env python3
"""Verify the live CWICR seed contract against release metadata and local Qdrant."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any
from urllib import error, request

QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333").rstrip("/")
COLLECTION = os.environ.get("CWICR_COLLECTION", "cwicr")
EXPECTED_POINT_COUNT = int(os.environ.get("CWICR_EXPECTED_POINT_COUNT", "49600"))
EXPECTED_VECTOR_SIZE = int(os.environ.get("CWICR_EXPECTED_VECTOR_SIZE", "3072"))
SNAPSHOT_ASSET_NAME = os.environ.get(
    "CWICR_SNAPSHOT_ASSET_NAME",
    "HI_MUMBAI_workitems_costs_resources_EMBEDDINGS_3072_DDC_CWICR.snapshot",
)
RELEASE_API_URL = os.environ.get(
    "CWICR_RELEASE_API_URL",
    "https://api.github.com/repos/datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR/releases/latest",
)
REQUEST_TIMEOUT_SECONDS = 20.0
SNAPSHOT_RESTORE_TIMEOUT_SECONDS = 60.0 * 60.0
SNAPSHOT_DIMENSION_RE = re.compile(r"(?:EMBEDDINGS_|embeddings_)(\d+)")


class HTTPRequestError(RuntimeError):
    """Surface HTTP status codes without taking a runtime dependency on httpx."""

    def __init__(self, *, method: str, url: str, status_code: int, body: str) -> None:
        super().__init__(f"{method} {url} failed with HTTP {status_code}")
        self.status_code = status_code
        self.body = body


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--collection", default=COLLECTION)
    parser.add_argument(
        "--restore-if-needed",
        action="store_true",
        help="Attempt a real snapshot restore when the local collection does not match the expected contract.",
    )
    return parser.parse_args()


def _request_text(
    url: str,
    *,
    method: str = "GET",
    json_body: dict[str, Any] | None = None,
    timeout: float = REQUEST_TIMEOUT_SECONDS,
) -> str:
    headers = {"Accept": "application/vnd.github+json"}
    data = None
    if json_body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(json_body).encode("utf-8")
    req = request.Request(url, data=data, headers=headers, method=method)
    try:
        with request.urlopen(req, timeout=timeout) as response:
            return response.read().decode("utf-8")
    except error.HTTPError as exc:
        raise HTTPRequestError(
            method=method,
            url=url,
            status_code=exc.code,
            body=exc.read().decode("utf-8", errors="replace"),
        ) from exc
    except error.URLError as exc:
        raise RuntimeError(f"{method} {url} failed: {exc.reason}") from exc


def _fetch_json(
    url: str,
    *,
    method: str = "GET",
    json_body: dict[str, Any] | None = None,
    timeout: float = REQUEST_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    payload = json.loads(_request_text(url, method=method, json_body=json_body, timeout=timeout))
    if not isinstance(payload, dict):
        raise RuntimeError(f"expected JSON object from {url}")
    return payload


def _fetch_text(url: str) -> str:
    return _request_text(url)


def _fetch_release_metadata() -> dict[str, Any]:
    payload = _fetch_json(RELEASE_API_URL)
    assets = payload.get("assets")
    if not isinstance(assets, list):
        raise RuntimeError("latest CWICR release payload is missing assets")
    snapshot_assets = []
    for asset in assets:
        if not isinstance(asset, dict) or not str(asset.get("name", "")).endswith(".snapshot"):
            continue
        match = SNAPSHOT_DIMENSION_RE.search(str(asset.get("name", "")))
        snapshot_assets.append(
            {
                "name": asset.get("name"),
                "size": asset.get("size"),
                "browser_download_url": asset.get("browser_download_url"),
                "vector_size": int(match.group(1)) if match is not None else None,
            }
        )
    if not snapshot_assets:
        raise RuntimeError("latest CWICR release does not expose any snapshot assets")

    dimensions = sorted(
        {
            asset["vector_size"]
            for asset in snapshot_assets
            if isinstance(asset.get("vector_size"), int)
        }
    )
    selected_snapshot_asset = next(
        (asset for asset in snapshot_assets if asset.get("name") == SNAPSHOT_ASSET_NAME),
        None,
    )
    return {
        "tag_name": payload.get("tag_name"),
        "name": payload.get("name"),
        "asset_count": len(assets),
        "snapshot_asset_count": len(snapshot_assets),
        "snapshot_assets": snapshot_assets,
        "snapshot_dimensions": dimensions,
        "selected_snapshot_asset": selected_snapshot_asset,
    }


def _probe_health() -> dict[str, Any]:
    root = _fetch_json(f"{QDRANT_URL}/")
    health_404 = False
    try:
        health = _fetch_json(f"{QDRANT_URL}/health")
        endpoint = "/health"
    except HTTPRequestError as exc:
        if exc.status_code != 404:
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


def _probe_collection(collection: str, *, allow_missing: bool = False) -> dict[str, Any] | None:
    try:
        collection_payload = _fetch_json(f"{QDRANT_URL}/collections/{collection}")
        count_payload = _fetch_json(
            f"{QDRANT_URL}/collections/{collection}/points/count",
            method="POST",
            json_body={"exact": True},
        )
    except HTTPRequestError as exc:
        if allow_missing and exc.status_code == 404:
            return None
        raise
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


def _delete_collection(collection: str) -> bool:
    try:
        _request_text(
            f"{QDRANT_URL}/collections/{collection}",
            method="DELETE",
        )
    except HTTPRequestError as exc:
        if exc.status_code == 404:
            return False
        raise
    return True


def _recover_snapshot(collection: str, snapshot_asset: dict[str, Any]) -> dict[str, Any]:
    snapshot_url = snapshot_asset.get("browser_download_url")
    if not isinstance(snapshot_url, str) or not snapshot_url:
        raise RuntimeError(f"snapshot asset {snapshot_asset.get('name')!r} is missing a download URL")
    payload = _fetch_json(
        f"{QDRANT_URL}/collections/{collection}/snapshots/recover",
        method="PUT",
        json_body={
            "location": snapshot_url,
            "priority": "snapshot",
        },
        timeout=SNAPSHOT_RESTORE_TIMEOUT_SECONDS,
    )
    return payload


def _evaluate_seed_contract(
    release: dict[str, Any],
    collection_state: dict[str, Any] | None,
    *,
    collection_name: str = COLLECTION,
) -> tuple[bool, list[str]]:
    blockers: list[str] = []

    snapshot_dimensions = release.get("snapshot_dimensions")
    if not isinstance(snapshot_dimensions, list) or not snapshot_dimensions:
        blockers.append("latest CWICR release does not expose a parseable snapshot vector dimension")
    elif EXPECTED_VECTOR_SIZE not in snapshot_dimensions:
        blockers.append(
            "latest CWICR release snapshot dimensions "
            f"{snapshot_dimensions} do not include the expected {EXPECTED_VECTOR_SIZE}-d contract"
        )

    selected_snapshot_asset = release.get("selected_snapshot_asset")
    if not isinstance(selected_snapshot_asset, dict):
        blockers.append(f"latest CWICR release does not expose snapshot asset {SNAPSHOT_ASSET_NAME!r}")
    else:
        observed_snapshot_vector_size = selected_snapshot_asset.get("vector_size")
        if observed_snapshot_vector_size != EXPECTED_VECTOR_SIZE:
            blockers.append(
                f"release snapshot {selected_snapshot_asset.get('name')!r} uses vector size "
                f"{observed_snapshot_vector_size}; expected {EXPECTED_VECTOR_SIZE}"
            )

    if collection_state is None:
        blockers.append(f"collection {collection_name!r} is missing")
        return not blockers, blockers

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


def _build_success_payload(
    release: dict[str, Any],
    qdrant: dict[str, Any],
    collection_state: dict[str, Any],
    restore: dict[str, Any],
) -> dict[str, Any]:
    return {
        "status": "passed",
        "collection": collection_state["collection"],
        "expected": {
            "points_count": EXPECTED_POINT_COUNT,
            "vector_size": EXPECTED_VECTOR_SIZE,
            "snapshot_asset_name": SNAPSHOT_ASSET_NAME,
        },
        "release": release,
        "qdrant": qdrant,
        "collection_state": collection_state,
        "restore": restore,
    }


def _build_failure_payload(
    release: dict[str, Any],
    qdrant: dict[str, Any],
    collection_state: dict[str, Any] | None,
    blockers: list[str],
    restore: dict[str, Any],
    *,
    collection_name: str = COLLECTION,
) -> dict[str, Any]:
    return {
        "status": "blocked",
        "collection": collection_name if collection_state is None else collection_state["collection"],
        "expected": {
            "points_count": EXPECTED_POINT_COUNT,
            "vector_size": EXPECTED_VECTOR_SIZE,
            "snapshot_asset_name": SNAPSHOT_ASSET_NAME,
        },
        "release": release,
        "qdrant": qdrant,
        "collection_state": collection_state,
        "blockers": blockers,
        "restore": restore,
        "resolution_hint": (
            f"Restore release snapshot {SNAPSHOT_ASSET_NAME!r} into the target collection or reseed it to "
            f"{EXPECTED_POINT_COUNT} points, then rerun this verifier."
        ),
    }


def main() -> int:
    """Execute the live CWICR seed verifier and exit non-zero when proof fails."""
    args = _parse_args()
    restore: dict[str, Any] = {
        "attempted": False,
        "snapshot_asset_name": SNAPSHOT_ASSET_NAME,
    }
    try:
        release = _fetch_release_metadata()
        qdrant = _probe_health()
        collection_state = _probe_collection(args.collection, allow_missing=True)
        ok, blockers = _evaluate_seed_contract(release, collection_state, collection_name=args.collection)
        if not ok and args.restore_if_needed:
            snapshot_asset = release.get("selected_snapshot_asset")
            if not isinstance(snapshot_asset, dict):
                raise RuntimeError(f"cannot restore because release asset {SNAPSHOT_ASSET_NAME!r} is unavailable")
            restore = {
                "attempted": True,
                "snapshot_asset_name": SNAPSHOT_ASSET_NAME,
                "deleted_existing_collection": _delete_collection(args.collection),
                "recover_response": _recover_snapshot(args.collection, snapshot_asset),
            }
            collection_state = _probe_collection(args.collection)
            ok, blockers = _evaluate_seed_contract(release, collection_state, collection_name=args.collection)
    except Exception as exc:
        print(
            json.dumps(
                {
                    "status": "blocked",
                    "collection": args.collection,
                    "blockers": [str(exc)],
                    "restore": restore,
                },
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1

    if not ok:
        print(
            json.dumps(
                _build_failure_payload(
                    release,
                    qdrant,
                    collection_state,
                    blockers,
                    restore,
                    collection_name=args.collection,
                ),
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1

    print(
        json.dumps(
            _build_success_payload(release, qdrant, collection_state, restore),
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
