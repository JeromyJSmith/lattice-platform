"""Resolve the local OpenConstructionERP runtime without assuming localhost:8080."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from uuid import UUID

import httpx

DEFAULT_PORTLESS_PROXY_PORT = 1355
DEFAULT_PORTLESS_ROUTES_PATH = Path.home() / ".portless" / "routes.json"
ERP_LOGIN_PATH = "/api/v1/users/auth/login/"
ERP_DEMO_LOGIN_PATH = "/api/v1/users/auth/demo-login/"
ERP_PROJECTS_PATH = "/api/v1/projects/"
DEFAULT_ERP_VERIFIER_PROJECT_NAME = "LATTICE BOQ Verifier Project"
DEFAULT_ERP_VERIFIER_PROJECT_CODE = "LATTICE-BOQ-001"
DEFAULT_ERP_PORTLESS_HOSTS = (
    "openconstructionerp.marpa.localhost",
    "openconstructionerp.localhost",
    "openconstruction-erp.marpa.localhost",
    "openconstruction-erp.localhost",
    "erp.marpa.localhost",
    "erp.localhost",
)


@dataclass(frozen=True)
class ErpRuntimeResolution:
    """Result of resolving the current ERP upstream target."""

    base_url: str | None
    source: str
    blocker: str | None
    portless_host: str | None = None
    routes_path: str | None = None


def _normalize_url(value: str | None) -> str | None:
    normalized = (value or "").strip().rstrip("/")
    return normalized or None


def _candidate_portless_hosts() -> tuple[str, ...]:
    explicit_host = (os.environ.get("OPENCONSTRUCTIONERP_PORTLESS_HOST") or "").strip().lower()
    hosts = [explicit_host] if explicit_host else []
    for host in DEFAULT_ERP_PORTLESS_HOSTS:
        if host not in hosts:
            hosts.append(host)
    return tuple(hosts)


def _portless_proxy_port() -> int:
    raw = (os.environ.get("PORTLESS_PROXY_PORT") or "").strip()
    if not raw:
        return DEFAULT_PORTLESS_PROXY_PORT
    try:
        port = int(raw)
    except ValueError:
        return DEFAULT_PORTLESS_PROXY_PORT
    return port if port > 0 else DEFAULT_PORTLESS_PROXY_PORT


def _load_routes(routes_path: Path) -> list[dict[str, Any]]:
    try:
        payload = json.loads(routes_path.read_text())
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []
    if not isinstance(payload, list):
        return []
    return [row for row in payload if isinstance(row, dict)]


def _parse_env_bool(name: str) -> bool | None:
    raw = (os.environ.get(name) or "").strip().lower()
    if not raw:
        return None
    return raw not in {"0", "false", "no", "off"}


def resolve_erp_runtime() -> ErpRuntimeResolution:
    """Prefer explicit ERP config, then portless aliases, otherwise return a blocked runtime."""

    explicit_url = _normalize_url(os.environ.get("OPENCONSTRUCTIONERP_URL"))
    if explicit_url is not None:
        return ErpRuntimeResolution(base_url=explicit_url, source="env:OPENCONSTRUCTIONERP_URL", blocker=None)

    routes_path = Path(
        _normalize_url(os.environ.get("PORTLESS_ROUTES_PATH")) or DEFAULT_PORTLESS_ROUTES_PATH.as_posix()
    )
    routes = _load_routes(routes_path)
    candidate_hosts = _candidate_portless_hosts()
    routes_by_host = {
        str(row.get("hostname", "")).strip().lower(): row
        for row in routes
        if str(row.get("hostname", "")).strip()
    }
    matched_hosts = [host for host in candidate_hosts if host in routes_by_host]
    if len(matched_hosts) == 1:
        host = matched_hosts[0]
        return ErpRuntimeResolution(
            base_url=f"https://{host}:{_portless_proxy_port()}",
            source=f"portless:{host}",
            blocker=None,
            portless_host=host,
            routes_path=routes_path.as_posix(),
        )
    if len(matched_hosts) > 1:
        return ErpRuntimeResolution(
            base_url=None,
            source="blocked",
            blocker=(
                "OpenConstructionERP runtime blocked: multiple portless ERP routes matched "
                f"{matched_hosts} in {routes_path}; set OPENCONSTRUCTIONERP_URL or "
                "OPENCONSTRUCTIONERP_PORTLESS_HOST explicitly."
            ),
            routes_path=routes_path.as_posix(),
        )

    collision = next(
        (
            row
            for row in routes
            if str(row.get("hostname", "")).strip().lower() == "mlx.marpa.localhost"
            and row.get("port") == 8080
        ),
        None,
    )
    collision_hint = ""
    if collision is not None:
        collision_hint = (
            " Current portless state maps mlx.marpa.localhost -> localhost:8080, "
            "so raw localhost:8080 is not a safe OpenConstructionERP default on this workstation."
        )
    checked_hosts = ", ".join(candidate_hosts)
    return ErpRuntimeResolution(
        base_url=None,
        source="blocked",
        blocker=(
            "OpenConstructionERP runtime blocked: OPENCONSTRUCTIONERP_URL is unset and no ERP portless route "
            f"was found in {routes_path}. Checked hostnames: {checked_hosts}.{collision_hint}"
        ),
        routes_path=routes_path.as_posix(),
    )


def require_erp_runtime() -> ErpRuntimeResolution:
    """Return the resolved ERP runtime or raise with the current blocker message."""

    runtime = resolve_erp_runtime()
    if runtime.base_url is None or runtime.blocker is not None:
        raise RuntimeError(runtime.blocker or "OpenConstructionERP runtime is not configured.")
    return runtime


def erp_tls_verify(base_url: str | None = None) -> bool:
    """Honor explicit TLS config, otherwise trust portless localhost HTTPS as a local dev surface."""

    configured = _parse_env_bool("OPENCONSTRUCTIONERP_VERIFY_TLS")
    if configured is not None:
        return configured

    parsed = urlparse(_normalize_url(base_url) or "")
    host = (parsed.hostname or "").lower()
    if parsed.scheme == "https" and (host == "localhost" or host.endswith(".localhost")):
        return False
    return True


def _normalize_uuid(value: str | None) -> str | None:
    normalized = _normalize_url(value)
    if normalized is None:
        return None
    try:
        return str(UUID(normalized))
    except ValueError:
        return None


def erp_response_detail(response: httpx.Response) -> str:
    """Extract the most useful response detail string for blocker evidence."""
    try:
        payload = response.json()
    except ValueError:
        payload = None
    if isinstance(payload, dict):
        detail = payload.get("detail")
        if isinstance(detail, str) and detail.strip():
            return detail.strip()
    text = response.text.strip()
    if text:
        return text
    return response.reason_phrase or f"HTTP {response.status_code}"


@lru_cache(maxsize=16)
def _resolve_access_token(
    base_url: str,
    verify: bool,
    explicit_token: str | None,
    auth_email: str | None,
    auth_password: str | None,
    demo_email: str | None,
) -> str | None:
    if explicit_token is not None:
        return explicit_token
    request_path: str | None = None
    request_body: dict[str, str] | None = None
    if auth_email is not None and auth_password is not None:
        request_path = ERP_LOGIN_PATH
        request_body = {"email": auth_email, "password": auth_password}
    elif demo_email is not None:
        request_path = ERP_DEMO_LOGIN_PATH
        request_body = {"email": demo_email}
    if request_path is None or request_body is None:
        return None
    url = f"{base_url}{request_path}"
    try:
        response = httpx.post(
            url,
            json=request_body,
            timeout=20.0,
            verify=verify,
            follow_redirects=True,
        )
    except Exception as exc:
        raise RuntimeError(f"OpenConstructionERP auth bootstrap failed for {url}: {exc!s}") from exc
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            "OpenConstructionERP auth bootstrap returned "
            f"{response.status_code} {erp_response_detail(response)} for {url}"
        ) from exc
    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError(f"OpenConstructionERP auth bootstrap returned non-JSON payload for {url}.") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"OpenConstructionERP auth bootstrap returned unsupported JSON payload for {url}.")
    access_token = payload.get("access_token")
    if not isinstance(access_token, str) or not access_token.strip():
        raise RuntimeError(f"OpenConstructionERP auth bootstrap did not return an access_token for {url}.")
    return access_token.strip()


def erp_access_token(base_url: str | None = None) -> str | None:
    """Resolve an ERP bearer token from env or the live auth endpoints."""
    normalized_base_url = _normalize_url(base_url)
    if normalized_base_url is None:
        runtime = resolve_erp_runtime()
        normalized_base_url = runtime.base_url
    if normalized_base_url is None:
        return None
    explicit_token = _normalize_url(os.environ.get("OPENCONSTRUCTIONERP_ACCESS_TOKEN"))
    auth_email = _normalize_url(os.environ.get("OPENCONSTRUCTIONERP_AUTH_EMAIL"))
    auth_password = _normalize_url(os.environ.get("OPENCONSTRUCTIONERP_AUTH_PASSWORD"))
    demo_email = _normalize_url(os.environ.get("OPENCONSTRUCTIONERP_AUTH_DEMO_EMAIL"))
    return _resolve_access_token(
        normalized_base_url,
        erp_tls_verify(normalized_base_url),
        explicit_token,
        auth_email,
        auth_password,
        demo_email,
    )


def erp_auth_headers(base_url: str | None = None) -> dict[str, str]:
    """Return ERP auth headers when a bearer token is configured."""
    access_token = erp_access_token(base_url)
    if access_token is None:
        return {}
    return {"Authorization": f"Bearer {access_token}"}


def erp_request_kwargs(
    *,
    base_url: str | None = None,
    timeout: float | None = None,
    follow_redirects: bool | None = None,
) -> dict[str, Any]:
    """Return shared httpx request kwargs for the live ERP runtime."""
    kwargs: dict[str, Any] = {"verify": erp_tls_verify(base_url)}
    headers = erp_auth_headers(base_url)
    if headers:
        kwargs["headers"] = headers
    if timeout is not None:
        kwargs["timeout"] = timeout
    if follow_redirects is not None:
        kwargs["follow_redirects"] = follow_redirects
    return kwargs


def erp_client(*, base_url: str, timeout: float) -> httpx.Client:
    """Build an ERP httpx client with the runtime TLS policy applied."""
    headers = erp_auth_headers(base_url)
    return httpx.Client(
        base_url=base_url,
        timeout=timeout,
        verify=erp_tls_verify(base_url),
        headers=headers or None,
    )

def ensure_erp_verifier_project_id(
    *,
    env_var_names: tuple[str, ...],
    project_name: str = DEFAULT_ERP_VERIFIER_PROJECT_NAME,
    project_code: str = DEFAULT_ERP_VERIFIER_PROJECT_CODE,
    base_url: str | None = None,
) -> tuple[str, str]:
    """Return a valid ERP project UUID for verifier runs, creating one if needed."""
    for env_var_name in env_var_names:
        project_id = _normalize_uuid(os.environ.get(env_var_name))
        if project_id is not None:
            return project_id, f"env:{env_var_name}"
    runtime = require_erp_runtime() if base_url is None else ErpRuntimeResolution(base_url=base_url, source="arg:base_url", blocker=None)
    with erp_client(base_url=runtime.base_url, timeout=30.0) as client:
        response = client.get(ERP_PROJECTS_PATH, params={"limit": 500})
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list):
            raise RuntimeError(f"OpenConstructionERP project list returned unsupported JSON payload for {ERP_PROJECTS_PATH}.")
        for row in payload:
            if not isinstance(row, dict):
                continue
            project_id = _normalize_uuid(row.get("id"))
            if project_id is None:
                continue
            if row.get("name") == project_name or row.get("project_code") == project_code:
                return project_id, "erp:list-projects"
        create_response = client.post(
            ERP_PROJECTS_PATH,
            json={"name": project_name, "project_code": project_code, "validation_rule_sets": ["boq_quality"]},
        )
        create_response.raise_for_status()
        created_payload = create_response.json()
    if not isinstance(created_payload, dict):
        raise RuntimeError(f"OpenConstructionERP project bootstrap returned unsupported JSON payload for {ERP_PROJECTS_PATH}.")
    project_id = _normalize_uuid(created_payload.get("id"))
    if project_id is None:
        raise RuntimeError(f"OpenConstructionERP project bootstrap did not return a valid UUID for {ERP_PROJECTS_PATH}.")
    return project_id, "erp:create-project"
