"""Bentley iTwin Platform adapter.

OAuth 2.0 client_credentials -> Bearer token, then call:
    Synchronization API:    GET /synchronization/imodels/{imodel_id}/sourceFiles/{source_id}/storageFile
    Synchronization API:    GET /synchronization/imodels/{imodel_id}/runs/{run_id}
    Changed Elements API:   GET /changedelements/comparisons?iModelId=...&startChangeset=...&endChangeset=...
    iModels API:            GET /imodels/{imodel_id}
    Reality Data API:       GET /realitydata?iTwinId=...

Token cache is in-memory (keyed by client_id), refreshed on 401 or near
expiry. Pagination is handled via the standard `_links.next.href` field
returned by Bentley APIs.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Generator
from urllib.parse import urljoin

import httpx

log = logging.getLogger("vwbridge.itwin")

_TOKEN_CACHE: dict[str, dict[str, Any]] = {}


def _get_token(settings) -> str:
    cid = settings.BENTLEY_CLIENT_ID
    secret = settings.BENTLEY_CLIENT_SECRET
    if not cid or not secret:
        raise RuntimeError("BENTLEY_CLIENT_ID and BENTLEY_CLIENT_SECRET must be set")

    cached = _TOKEN_CACHE.get(cid)
    if cached and cached["expires_at"] - time.time() > 60:
        return cached["access_token"]

    log.info("requesting Bentley OAuth token (client_id=%s)", cid[:8] + "...")
    r = httpx.post(
        settings.BENTLEY_OAUTH_URL,
        data={
            "grant_type":    "client_credentials",
            "client_id":     cid,
            "client_secret": secret,
            "scope":         settings.BENTLEY_SCOPES,
        },
        timeout=30.0,
    )
    r.raise_for_status()
    body = r.json()
    _TOKEN_CACHE[cid] = {
        "access_token": body["access_token"],
        "expires_at":   time.time() + int(body.get("expires_in", 3600)),
    }
    return body["access_token"]


def _request(settings, method: str, path: str, **kw) -> httpx.Response:
    base = settings.BENTLEY_API_BASE
    url = urljoin(base.rstrip("/") + "/", path.lstrip("/"))
    headers = kw.pop("headers", {}) or {}
    headers.setdefault("Authorization", f"Bearer {_get_token(settings)}")
    headers.setdefault("Accept", "application/vnd.bentley.itwin-platform.v1+json")
    timeout = kw.pop("timeout", 30.0)
    r = httpx.request(method, url, headers=headers, timeout=timeout, **kw)
    if r.status_code == 401:
        _TOKEN_CACHE.pop(settings.BENTLEY_CLIENT_ID, None)
        headers["Authorization"] = f"Bearer {_get_token(settings)}"
        r = httpx.request(method, url, headers=headers, timeout=timeout, **kw)
    return r


def fetch_imodel(settings, imodel_id: str) -> dict[str, Any]:
    r = _request(settings, "GET", f"/imodels/{imodel_id}")
    r.raise_for_status()
    return r.json()


def fetch_sync_run(settings, imodel_id: str, sync_run_id: str) -> dict[str, Any]:
    r = _request(
        settings, "GET",
        f"/synchronization/imodels/{imodel_id}/runs/{sync_run_id}",
    )
    r.raise_for_status()
    return r.json()


def fetch_changed_elements_paginated(
    settings,
    *,
    itwin_id: str,
    imodel_id: str,
    since_changeset_id: str | None = None,
    page_size: int = 200,
) -> Generator[dict[str, Any], None, None]:
    """Yield normalized {imodel_id, page, page_size, changeset_id, changed_elements:[...]} per page."""
    params = {
        "iTwinId":        itwin_id,
        "iModelId":       imodel_id,
        "$top":           page_size,
    }
    if since_changeset_id:
        params["startChangeset"] = since_changeset_id

    next_url: str | None = "/changedelements/comparisons"
    page = 0

    while next_url:
        log.info("fetching changed-elements page=%d url=%s", page, next_url)
        if next_url.startswith("http"):
            r = httpx.get(
                next_url,
                headers={"Authorization": f"Bearer {_get_token(settings)}",
                         "Accept": "application/vnd.bentley.itwin-platform.v1+json"},
                timeout=30.0,
            )
        else:
            r = _request(settings, "GET", next_url, params=params if page == 0 else None)
        if r.status_code == 429:
            retry_after = float(r.headers.get("retry-after", "5"))
            log.warning("429 from changed-elements; sleeping %.1fs", retry_after)
            time.sleep(retry_after)
            continue
        r.raise_for_status()
        body = r.json()

        comparisons = body.get("comparisons") or body.get("changedElements") or []
        normalized = []
        for c in comparisons:
            normalized.append({
                "changeset_id":      c.get("endChangeset") or c.get("changesetId", ""),
                "source_element_id": c.get("sourceId") or c.get("sourceElementId", ""),
                "change_kind":       c.get("opCode") or c.get("change_kind", ""),
                "bis_class":         c.get("bisClass", ""),
                "bis_subcategory":   c.get("bisSubcategory", ""),
                "before_hash":       c.get("beforeHash", ""),
                "after_hash":        c.get("afterHash", ""),
            })

        yield {
            "itwin_id":         itwin_id,
            "imodel_id":        imodel_id,
            "page":             page,
            "page_size":        page_size,
            "changeset_id":     since_changeset_id or "",
            "changed_elements": normalized,
        }

        page += 1
        next_url = (body.get("_links") or {}).get("next", {}).get("href")
        if not next_url:
            break
