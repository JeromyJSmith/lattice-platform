"""Pure-Python tests for the live CWICR cost-search verifier."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


def _load_verifier():
    repo_root = Path(__file__).resolve().parents[3]
    script_path = repo_root / "scripts" / "verify-cwicr-cost-search.py"
    spec = importlib.util.spec_from_file_location("verify_cwicr_cost_search", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_verify_qdrant_ready_falls_back_to_healthz(monkeypatch) -> None:
    """Accept the live Qdrant healthz-only contract and keep the collection dimensions."""
    verifier = _load_verifier()

    def fake_fetch_json(method: str, path: str, *, json_body=None):
        """Return deterministic Qdrant probe payloads for the verifier."""
        if (method, path) == ("GET", "/"):
            return {"title": "qdrant"}
        if (method, path) == ("GET", "/health"):
            raise verifier.HTTPRequestError(method=method, path=path, status_code=404, body="")
        if (method, path) == ("GET", "/collections/cwicr"):
            return {
                "result": {
                    "status": "green",
                    "config": {
                        "params": {
                            "vectors": {
                                "size": 3072,
                            }
                        }
                    },
                }
            }
        if (method, path) == ("POST", "/collections/cwicr/points/count"):
            return {"result": {"count": 49600}}
        raise AssertionError((method, path, json_body))

    monkeypatch.setattr(verifier, "_fetch_json", fake_fetch_json)
    monkeypatch.setattr(verifier, "_fetch_text", lambda method, path: "healthz check passed")

    payload = verifier._verify_qdrant_ready()

    assert payload["health_endpoint"] == "/healthz"
    assert payload["health_404_fallback"] is True
    assert payload["count"] == 49600
    assert payload["vector_size"] == 3072


def test_main_reports_structured_route_blocker(monkeypatch, capsys) -> None:
    """Emit machine-readable blocker evidence when the route is still blocked."""
    verifier = _load_verifier()
    monkeypatch.setattr(
        verifier,
        "_parse_args",
        lambda: verifier.argparse.Namespace(
            description="concrete slab 10cm reinforced",
            region="US",
            top=3,
        ),
    )
    monkeypatch.setattr(
        verifier,
        "_verify_qdrant_ready",
        lambda: {
            "collection": "cwicr",
            "count": 49600,
            "vector_size": 3072,
            "health_endpoint": "/healthz",
        },
    )
    monkeypatch.setattr(
        verifier,
        "_verify_route",
        lambda *_args, **_kwargs: {
            "status": "blocked",
            "status_code": 501,
            "detail": "CWICR cost search blocked: live collection 'cwicr' uses OpenAI 3072d embeddings but OPENAI_API_KEY is not configured.",
        },
    )

    assert verifier.main() == 1
    payload = json.loads(capsys.readouterr().err)
    assert payload["status"] == "blocked"
    assert payload["qdrant"]["count"] == 49600
    assert payload["qdrant"]["vector_size"] == 3072
    assert payload["route"]["status_code"] == 501


def test_main_passes_when_route_proof_passes(monkeypatch, capsys) -> None:
    """Return a passing proof payload only when the route contract passes."""
    verifier = _load_verifier()
    monkeypatch.setattr(
        verifier,
        "_parse_args",
        lambda: verifier.argparse.Namespace(
            description="concrete slab 10cm reinforced",
            region="US",
            top=3,
        ),
    )
    monkeypatch.setattr(
        verifier,
        "_verify_qdrant_ready",
        lambda: {
            "collection": "cwicr",
            "count": 49600,
            "vector_size": 3072,
            "health_endpoint": "/healthz",
        },
    )
    monkeypatch.setattr(
        verifier,
        "_verify_route",
        lambda *_args, **_kwargs: {
            "status": "passed",
            "proof": {
                "top_item_id": "RATE-1",
                "top_score": 0.81,
                "row_count": 3,
            },
        },
    )

    assert verifier.main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "passed"
    assert payload["qdrant"]["count"] == 49600
    assert payload["proof"]["top_item_id"] == "RATE-1"
