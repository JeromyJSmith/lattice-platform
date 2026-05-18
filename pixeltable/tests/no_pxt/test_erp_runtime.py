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

    assert resolved.base_url == "https://openconstructionerp.marpa.localhost:1355"
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


def test_erp_tls_verify_disables_verification_for_portless_localhost(monkeypatch):
    """Portless localhost HTTPS should be reachable without requiring a trusted local CA."""

    runtime = _load_runtime()
    monkeypatch.delenv("OPENCONSTRUCTIONERP_VERIFY_TLS", raising=False)

    assert runtime.erp_tls_verify("https://openconstructionerp.marpa.localhost:1355") is False
    assert runtime.erp_tls_verify("http://openconstructionerp.marpa.localhost:1355") is True


def test_erp_tls_verify_honors_explicit_override(monkeypatch):
    """An explicit env override should win over the localhost heuristic."""

    runtime = _load_runtime()
    monkeypatch.setenv("OPENCONSTRUCTIONERP_VERIFY_TLS", "1")

    assert runtime.erp_tls_verify("https://openconstructionerp.marpa.localhost:1355") is True


def test_erp_request_kwargs_uses_explicit_access_token(monkeypatch):
    """A pre-issued token should be attached to outbound ERP requests."""

    runtime = _load_runtime()
    runtime._resolve_access_token.cache_clear()
    monkeypatch.setenv("OPENCONSTRUCTIONERP_ACCESS_TOKEN", "token-123")

    kwargs = runtime.erp_request_kwargs(base_url="https://openconstructionerp.marpa.localhost:1355")

    assert kwargs["headers"] == {"Authorization": "Bearer token-123"}


def test_erp_request_kwargs_logs_in_with_credentials(monkeypatch):
    """Email/password auth should bootstrap a bearer token through the ERP login endpoint."""

    runtime = _load_runtime()
    runtime._resolve_access_token.cache_clear()
    monkeypatch.delenv("OPENCONSTRUCTIONERP_ACCESS_TOKEN", raising=False)
    monkeypatch.setenv("OPENCONSTRUCTIONERP_AUTH_EMAIL", "verifier@example.com")
    monkeypatch.setenv("OPENCONSTRUCTIONERP_AUTH_PASSWORD", "DemoPass1234!")

    class _Response:
        status_code = 200

        def raise_for_status(self):
            """Mirror a successful auth response."""
            return None

        def json(self):
            """Return the shaped token payload expected by runtime auth."""
            return {
                "access_token": "jwt-123",
                "refresh_token": "refresh-123",
                "expires_in": 3600,
            }

    seen: list[tuple[str, dict[str, str]]] = []

    def _post(url: str, *, json: dict[str, str], **kwargs):
        seen.append((url, json))
        return _Response()

    monkeypatch.setattr(runtime.httpx, "post", _post)

    kwargs = runtime.erp_request_kwargs(base_url="https://openconstructionerp.marpa.localhost:1355")

    assert kwargs["headers"] == {"Authorization": "Bearer jwt-123"}
    assert seen == [
        (
            "https://openconstructionerp.marpa.localhost:1355/api/v1/users/auth/login/",
            {"email": "verifier@example.com", "password": "DemoPass1234!"},
        )
    ]


def test_erp_request_kwargs_falls_back_to_local_demo_login(monkeypatch):
    """Local Portless ERP should auto-bootstrap through the seeded demo account when no auth env is set."""

    runtime = _load_runtime()
    runtime._resolve_access_token.cache_clear()
    monkeypatch.delenv("OPENCONSTRUCTIONERP_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("OPENCONSTRUCTIONERP_AUTH_EMAIL", raising=False)
    monkeypatch.delenv("OPENCONSTRUCTIONERP_AUTH_PASSWORD", raising=False)
    monkeypatch.delenv("OPENCONSTRUCTIONERP_AUTH_DEMO_EMAIL", raising=False)

    class _Response:
        status_code = 200

        def raise_for_status(self):
            """Mirror a successful demo auth response."""
            return None

        def json(self):
            """Return the mocked demo token payload."""
            return {
                "access_token": "demo-jwt-123",
                "refresh_token": "refresh-123",
                "expires_in": 3600,
            }

    seen: list[tuple[str, dict[str, str]]] = []

    def _post(url: str, *, json: dict[str, str], **kwargs):
        seen.append((url, json))
        return _Response()

    monkeypatch.setattr(runtime.httpx, "post", _post)

    kwargs = runtime.erp_request_kwargs(base_url="https://openconstructionerp.marpa.localhost:1355")

    assert kwargs["headers"] == {"Authorization": "Bearer demo-jwt-123"}
    assert seen == [
        (
            "https://openconstructionerp.marpa.localhost:1355/api/v1/users/auth/demo-login/",
            {"email": "demo@openestimator.io"},
        )
    ]


def test_erp_request_kwargs_does_not_try_demo_login_for_non_local_runtime(monkeypatch):
    """Automatic demo auth should stay limited to local localhost ERP targets."""

    runtime = _load_runtime()
    runtime._resolve_access_token.cache_clear()
    monkeypatch.delenv("OPENCONSTRUCTIONERP_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("OPENCONSTRUCTIONERP_AUTH_EMAIL", raising=False)
    monkeypatch.delenv("OPENCONSTRUCTIONERP_AUTH_PASSWORD", raising=False)
    monkeypatch.delenv("OPENCONSTRUCTIONERP_AUTH_DEMO_EMAIL", raising=False)

    def _post(*args, **kwargs):
        raise AssertionError("demo login should not be attempted for non-local ERP targets")

    monkeypatch.setattr(runtime.httpx, "post", _post)

    kwargs = runtime.erp_request_kwargs(base_url="https://erp.example.com")

    assert "headers" not in kwargs


def test_ensure_erp_verifier_project_id_creates_project_when_missing(monkeypatch):
    """Verifier project bootstrap should create a UUID-backed project when env config is absent."""

    runtime = _load_runtime()
    runtime._resolve_access_token.cache_clear()
    monkeypatch.delenv("ERP_BOQ_PROJECT_ID", raising=False)

    class _Response:
        def __init__(self, payload):
            self._payload = payload

        def raise_for_status(self):
            """Mirror a successful project list/create response."""
            return None

        def json(self):
            """Return the mocked ERP project payload."""
            return self._payload

    class _Client:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def get(self, path: str, params=None):
            """Return an empty project list so bootstrap creates one."""
            assert path == runtime.ERP_PROJECTS_PATH
            assert params == {"limit": 500}
            return _Response([])

        def post(self, path: str, json=None):
            """Return the created verifier project payload."""
            assert path == runtime.ERP_PROJECTS_PATH
            assert json == {
                "name": runtime.DEFAULT_ERP_VERIFIER_PROJECT_NAME,
                "project_code": runtime.DEFAULT_ERP_VERIFIER_PROJECT_CODE,
                "validation_rule_sets": ["boq_quality"],
            }
            return _Response({"id": "e7d28c24-c7f9-4a8e-a219-da2d52b82a73"})

    monkeypatch.setattr(runtime, "erp_client", lambda **kwargs: _Client())
    monkeypatch.setattr(
        runtime,
        "require_erp_runtime",
        lambda: runtime.ErpRuntimeResolution(
            base_url="https://openconstructionerp.marpa.localhost:1355",
            source="env:OPENCONSTRUCTIONERP_URL",
            blocker=None,
        ),
    )

    project_id, project_source = runtime.ensure_erp_verifier_project_id(env_var_names=("ERP_BOQ_PROJECT_ID",))

    assert project_id == "e7d28c24-c7f9-4a8e-a219-da2d52b82a73"
    assert project_source == "erp:create-project"
