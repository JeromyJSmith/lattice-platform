"""Resolve the local OpenConstructionERP runtime without assuming localhost:8080."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx

DEFAULT_PORTLESS_PROXY_PORT = 1355
DEFAULT_PORTLESS_ROUTES_PATH = Path.home() / ".portless" / "routes.json"
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
            base_url=f"http://{host}:{_portless_proxy_port()}",
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


def erp_request_kwargs(
    *,
    base_url: str | None = None,
    timeout: float | None = None,
    follow_redirects: bool | None = None,
) -> dict[str, Any]:
    """Return shared httpx request kwargs for the live ERP runtime."""
    kwargs: dict[str, Any] = {"verify": erp_tls_verify(base_url)}
    if timeout is not None:
        kwargs["timeout"] = timeout
    if follow_redirects is not None:
        kwargs["follow_redirects"] = follow_redirects
    return kwargs


def erp_client(*, base_url: str, timeout: float) -> httpx.Client:
    """Build an ERP httpx client with the runtime TLS policy applied."""
    return httpx.Client(base_url=base_url, timeout=timeout, verify=erp_tls_verify(base_url))


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
