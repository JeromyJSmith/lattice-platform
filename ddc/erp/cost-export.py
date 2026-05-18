#!/usr/bin/env python3
"""Export a project's BOQ from OpenConstructionERP as Excel or CSV.

Output goes to public/exports/boq-{project_id}-{timestamp}.{xlsx|csv}
so the operator console can offer a download link via /v1/erp/export.

Tracked in meta/FEATURE_BACKLOG.md § DDC INTEGRATION → "BOQ export".
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import httpx

REPO_ROOT = Path(__file__).resolve().parents[2]
if REPO_ROOT.as_posix() not in sys.path:
    sys.path.insert(0, REPO_ROOT.as_posix())

from ddc.erp.runtime import require_erp_runtime, resolve_erp_runtime


ERP_BOQ_LIST_PATH = "/api/v1/boq/boqs/"
ERP_BOQ_EXPORT_PATHS = {
    "xlsx": "/api/v1/boq/boqs/{boq_id}/export/excel",
    "csv": "/api/v1/boq/boqs/{boq_id}/export/csv",
}
EXPORT_DIR = REPO_ROOT / "public" / "exports"
ERP_RUNTIME = resolve_erp_runtime()
ERP_BASE = ERP_RUNTIME.base_url


def _normalize_project_id(project_id: str) -> str:
    normalized_project_id = project_id.strip()
    if not normalized_project_id:
        raise ValueError("project_id required")
    return normalized_project_id


def _filename_project_id_fragment(project_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", project_id).strip("-") or "project"


def _normalize_boq_list_payload(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, list) or not all(isinstance(row, dict) for row in payload):
        raise RuntimeError("OpenConstructionERP BOQ list response must be a JSON array of objects")
    return payload


def _resolve_boq_id(client: httpx.Client, project_id: str) -> str:
    response = client.get(ERP_BOQ_LIST_PATH, params={"project_id": project_id}, follow_redirects=True)
    response.raise_for_status()
    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError("OpenConstructionERP BOQ list response was not valid JSON") from exc
    rows = _normalize_boq_list_payload(payload)
    if not rows:
        raise RuntimeError(
            "OpenConstructionERP export requires an existing BOQ at "
            f"{ERP_BOQ_LIST_PATH}?project_id={project_id}"
        )
    boq_id = rows[0].get("id")
    if not isinstance(boq_id, str) or not boq_id.strip():
        raise RuntimeError("OpenConstructionERP BOQ list response did not expose a usable BOQ id")
    return boq_id.strip()


def export_boq(project_id: str, fmt: str = "xlsx") -> str:
    """Returns the output path on success."""
    normalized_project_id = _normalize_project_id(project_id)
    normalized_fmt = fmt.lower()
    if normalized_fmt not in {"xlsx", "csv"}:
        raise ValueError("fmt must be xlsx or csv")

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = EXPORT_DIR / f"boq-{_filename_project_id_fragment(normalized_project_id)}.{normalized_fmt}"
    erp_runtime = require_erp_runtime()
    with httpx.Client(base_url=erp_runtime.base_url, timeout=60.0) as client:
        boq_id = _resolve_boq_id(client, normalized_project_id)
        response = client.get(
            ERP_BOQ_EXPORT_PATHS[normalized_fmt].format(boq_id=boq_id),
            follow_redirects=True,
        )
        response.raise_for_status()
        if not response.content:
            raise RuntimeError(
                f"OpenConstructionERP export returned an empty artifact for project_id={normalized_project_id}"
            )
        output_path.write_bytes(response.content)
    return str(output_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: cost-export.py <project_id> [xlsx|csv]", file=sys.stderr)
        raise SystemExit(1)
    fmt = sys.argv[2] if len(sys.argv) > 2 else "xlsx"
    print(export_boq(sys.argv[1], fmt))
