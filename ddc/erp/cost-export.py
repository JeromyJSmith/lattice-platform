#!/usr/bin/env python3
"""Export a project's BOQ from OpenConstructionERP as Excel or CSV.

Output goes to public/exports/boq-{project_id}-{timestamp}.{xlsx|csv}
so the operator console can offer a download link via /v1/erp/export.

Tracked in meta/FEATURE_BACKLOG.md § DDC INTEGRATION → "BOQ export".
"""

from __future__ import annotations

import sys


def export_boq(project_id: str, fmt: str = "xlsx") -> str:
    """Returns the output path on success."""
    raise NotImplementedError(
        "cost-export stub. Use OpenConstructionERP's /api/boq/export endpoint "
        "and stream the result to public/exports/."
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: cost-export.py <project_id> [xlsx|csv]", file=sys.stderr)
        raise SystemExit(1)
    fmt = sys.argv[2] if len(sys.argv) > 2 else "xlsx"
    print(export_boq(sys.argv[1], fmt))
