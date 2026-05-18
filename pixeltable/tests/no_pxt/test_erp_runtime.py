"""Pure-Python tests for ERP runtime resolution."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_runtime():
    repo_root = Path(__file__).resolve().parents[3]
    module_path = repo_root / "ddc" / "erp" / "runtime.py"
    spec = importlib.util.spec_from_file_location("ddc_erp_runtime", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_resolve_erp_runtime_prefers_explicit_url(monkeypatch):
    """Explicit OPENCONSTRUCTIONERP_URL should bypass portless discovery."""

    runtime = _load_runtime()
    monkeypatch.setenv("OPENCONSTRUCTIONERP_URL", "https://erp.example.local/")

    resolved = runtime.resolve_erp_runtime()

    assert resolved.base_url == "https://erp.example.local"
    assert resolved.source == "env:OPENCONSTRUCTIONERP_URL"
    assert resolved.blocker is None


def test_resolve_erp_runtime_uses_matching_portless_alias(tmp_path: Path, monkeypatch):
    """A matching ERP alias in portless routes should become the base URL."""

    runtime = _load_runtime()
    routes_path = tmp_path / "routes.json"
    routes_path.write_text(json.dumps([{"hostname": "openconstructionerp.marpa.localhost", "port": 9080, "pid": 1}]))
    monkeypatch.delenv("OPENCONSTRUCTIONERP_URL", raising=False)
    monkeypatch.setenv("PORTLESS_ROUTES_PATH", routes_path.as_posix())

    resolved = runtime.resolve_erp_runtime()

    assert resolved.base_url == "http://openconstructionerp.marpa.localhost:1355"
    assert resolved.source == "portless:openconstructionerp.marpa.localhost"
    assert resolved.blocker is None


def test_resolve_erp_runtime_reports_missing_route_with_collision(tmp_path: Path, monkeypatch):
    """Missing ERP routes should mention the current mlx collision on localhost:8080."""

    runtime = _load_runtime()
    routes_path = tmp_path / "routes.json"
    routes_path.write_text(json.dumps([{"hostname": "mlx.marpa.localhost", "port": 8080, "pid": 1}]))
    monkeypatch.delenv("OPENCONSTRUCTIONERP_URL", raising=False)
    monkeypatch.setenv("PORTLESS_ROUTES_PATH", routes_path.as_posix())

    resolved = runtime.resolve_erp_runtime()

    assert resolved.base_url is None
    assert resolved.source == "blocked"
    assert "mlx.marpa.localhost -> localhost:8080" in (resolved.blocker or "")
