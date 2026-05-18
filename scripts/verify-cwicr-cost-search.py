#!/usr/bin/env python3
"""Run the live /v1/erp/cost-search proof contract against local CWICR Qdrant."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[1]
PIXELTABLE_ROOT = REPO_ROOT / "pixeltable"
if PIXELTABLE_ROOT.as_posix() not in sys.path:
    sys.path.insert(0, PIXELTABLE_ROOT.as_posix())

from service.routes import erp  # noqa: E402

QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333").rstrip("/")
COLLECTION = os.environ.get("CWICR_COLLECTION", "cwicr")
DEFAULT_DESCRIPTION = os.environ.get("CWICR_VERIFY_DESCRIPTION", "TOLI_KATO_KAKATO_KANE")
DEFAULT_REGION = os.environ.get("CWICR_VERIFY_REGION", "US")
DEFAULT_TOP = int(os.environ.get("CWICR_VERIFY_TOP", "3"))
REQUEST_TIMEOUT_SECONDS = 10.0


class HTTPRequestError(RuntimeError):
    """Preserve HTTP status context for Qdrant health probe fallback."""

    def __init__(self, *, method: str, path: str, status_code: int, body: str) -> None:
        super().__init__(f"{method} {path} failed with HTTP {status_code}")
        self.status_code = status_code
        self.body = body


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--description", default=DEFAULT_DESCRIPTION)
    parser.add_argument("--region", default=DEFAULT_REGION)
    parser.add_argument("--top", type=int, default=DEFAULT_TOP)
    return parser.parse_args()


def _fetch_json(method: str, path: str, *, json_body: dict[str, Any] | None = None) -> dict[str, Any]:
    response = httpx.request(
        method,
        f"{QDRANT_URL}{path}",
        json=json_body,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    if response.status_code >= 400:
        raise HTTPRequestError(
            method=method,
            path=path,
            status_code=response.status_code,
            body=response.text,
        )
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError(f"Qdrant returned non-object payload for {path}")
    return payload


def _fetch_text(method: str, path: str) -> str:
    response = httpx.request(method, f"{QDRANT_URL}{path}", timeout=REQUEST_TIMEOUT_SECONDS)
    if response.status_code >= 400:
        raise HTTPRequestError(
            method=method,
            path=path,
            status_code=response.status_code,
            body=response.text,
        )
    return response.text


def _verify_qdrant_ready() -> dict[str, Any]:
    try:
        root = _fetch_json("GET", "/")
    except Exception as exc:
        raise RuntimeError(f"Qdrant root probe failed: {exc!s}") from exc

    health_404_fallback = False
    try:
        health = _fetch_json("GET", "/health")
        health_endpoint = "/health"
    except HTTPRequestError as exc:
        if exc.status_code != 404:
            raise RuntimeError(f"Qdrant health probe failed: {exc!s}") from exc
        health_404_fallback = True
        health_text = _fetch_text("GET", "/healthz").strip()
        health_endpoint = "/healthz"
        health = {"status": "ok" if "passed" in health_text.lower() else health_text, "raw": health_text}

    if health.get("status") != "ok":
        raise RuntimeError(f"Qdrant health is not ok: {health}")

    try:
        collection_payload = _fetch_json("GET", f"/collections/{COLLECTION}")
        count_payload = _fetch_json("POST", f"/collections/{COLLECTION}/points/count", json_body={"exact": True})
    except Exception as exc:
        raise RuntimeError(f"CWICR collection probe failed: {exc!s}") from exc

    collection_result = collection_payload.get("result")
    if not isinstance(collection_result, dict):
        raise RuntimeError(f"CWICR collection payload missing result: {collection_payload}")
    result = count_payload.get("result")
    if not isinstance(result, dict):
        raise RuntimeError(f"CWICR collection count payload missing result: {count_payload}")
    count = result.get("count")
    if not isinstance(count, int) or count < 1:
        raise RuntimeError(f"CWICR collection {COLLECTION!r} is empty or unavailable: {count_payload}")

    config = collection_result.get("config")
    params = config.get("params") if isinstance(config, dict) else None
    vectors = params.get("vectors") if isinstance(params, dict) else None
    vector_size = vectors.get("size") if isinstance(vectors, dict) else None

    return {
        "root": root,
        "health": health,
        "health_endpoint": health_endpoint,
        "health_404_fallback": health_404_fallback,
        "collection": COLLECTION,
        "count": count,
        "vector_size": vector_size,
        "status": collection_result.get("status"),
    }


def _build_app() -> FastAPI:
    app = FastAPI()
    app.include_router(erp.router, prefix="/v1/erp")
    return app


def _verify_route(description: str, region: str, top: int) -> dict[str, Any]:
    client = TestClient(_build_app())
    response = client.post(
        "/v1/erp/cost-search",
        json={"description": description, "region": region, "top": top},
    )
    body = response.json()
    if response.status_code == 501:
        detail = body.get("detail") if isinstance(body, dict) else None
        return {
            "status": "blocked",
            "status_code": response.status_code,
            "detail": detail or body,
            "body": body,
        }
    if response.status_code != 200:
        raise RuntimeError(f"/v1/erp/cost-search returned {response.status_code}: {body}")
    verification_status = body.get("verification", {}).get("status")
    trust_status = body.get("trust_contract", {}).get("status")
    if verification_status != "passed" or trust_status != "passed":
        return {
            "status": "blocked",
            "status_code": response.status_code,
            "detail": "verification did not pass",
            "body": body,
        }
    rows = body.get("rows")
    if not isinstance(rows, list) or not rows:
        raise RuntimeError(f"cost-search returned no rows: {body}")
    confidence = body.get("confidence")
    if not isinstance(confidence, dict) or not isinstance(confidence.get("top_score"), (int, float)):
        raise RuntimeError(f"cost-search returned non-numeric top_score: {body}")
    return {
        "status": "passed",
        "proof": {
            "description": body.get("description"),
            "region": body.get("region"),
            "top": body.get("top"),
            "top_item_id": rows[0].get("item_id"),
            "top_score": confidence["top_score"],
            "retrieval": body.get("retrieval"),
            "verification": body.get("verification"),
            "trust_contract": body.get("trust_contract"),
            "row_count": len(rows),
        },
    }


def main() -> int:
    """Execute the live CWICR verifier and exit non-zero when the proof fails."""
    args = _parse_args()
    try:
        qdrant = _verify_qdrant_ready()
        route = _verify_route(args.description, args.region, args.top)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if route["status"] != "passed":
        print(
            json.dumps(
                {
                    "status": "blocked",
                    "collection": COLLECTION,
                    "qdrant": qdrant,
                    "request": {
                        "description": args.description,
                        "region": args.region,
                        "top": args.top,
                    },
                    "route": route,
                },
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1

    print(
        json.dumps(
            {
                "status": "passed",
                "collection": COLLECTION,
                "qdrant": qdrant,
                "proof": route["proof"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
