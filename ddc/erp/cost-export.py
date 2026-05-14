#!/usr/bin/env python3
"""Export a project's BOQ from OpenConstructionERP as Excel or CSV.

Output goes to public/exports/boq-{project_id}-{timestamp}.{xlsx|csv}
so the operator console can offer a download link via /v1/erp/export.

Tracked in meta/FEATURE_BACKLOG.md § DDC INTEGRATION → "BOQ export".
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import httpx


ERP_BASE = os.environ.get("OPENCONSTRUCTIONERP_URL", "http://localhost:8080")
REPO_ROOT = Path(__file__).resolve().parents[2]
EXPORT_DIR = REPO_ROOT / "public" / "exports"


def export_boq(project_id: str, fmt: str = "xlsx") -> str:
    """Returns the output path on success."""
    normalized_fmt = fmt.lower()
    if normalized_fmt not in {"xlsx", "csv"}:
        raise ValueError("fmt must be xlsx or csv")

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = EXPORT_DIR / f"boq-{project_id}.{normalized_fmt}"
    with httpx.Client(base_url=ERP_BASE, timeout=60.0) as client:
        response = client.get(
            "/api/boq/export",
            params={"project_id": project_id, "format": normalized_fmt},
        )
        response.raise_for_status()
        output_path.write_bytes(response.content)
    return str(output_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: cost-export.py <project_id> [xlsx|csv]", file=sys.stderr)
        raise SystemExit(1)
    fmt = sys.argv[2] if len(sys.argv) > 2 else "xlsx"
    print(export_boq(sys.argv[1], fmt))
