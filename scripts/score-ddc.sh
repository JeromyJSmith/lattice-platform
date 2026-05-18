#!/usr/bin/env bash
# score-ddc.sh — capability-path fitness score for the DDC section (0-100).
#
# This scorer is intentionally tied to the Juniper estimation/plugin foundation
# path, not to documentation presence. The goal is to move red/amber capability
# states to green in the order that matters for a real Vectorworks-backed cost
# estimation flow.
#
# Weighted path:
#   cwicr-seed                 10
#   cwicr-qdrant-cost-search   15
#   ifc-cost-enrichment        15
#   boq-sync                   20
#   boq-read                   10
#   boq-export                  5
#   phases-sync                10
#   quantity-takeoff-agent     10
#   ddc-estimation-contract     5
#
# Status weights:
#   green => 1.0
#   amber => 0.5
#   red   => 0.0
#
# Output:
#   default: single integer score
#   --json: detailed JSON payload with per-capability contribution

set -euo pipefail

REPO=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$REPO"

python3 - "$@" <<'PY'
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path.cwd()
MATRIX_PATH = REPO / "ddc" / "capability-matrix.yaml"

TARGETS = [
    ("cwicr-seed", 10),
    ("cwicr-qdrant-cost-search", 15),
    ("ifc-cost-enrichment", 15),
    ("boq-sync", 20),
    ("boq-read", 10),
    ("boq-export", 5),
    ("phases-sync", 10),
    ("quantity-takeoff-agent", 10),
    ("ddc-estimation-contract", 5),
]

STATUS_FACTOR = {
    "green": 1.0,
    "amber": 0.5,
    "red": 0.0,
}


def parse_capabilities(text: str) -> dict[str, dict[str, str]]:
    lines = text.splitlines()
    in_capabilities = False
    current: dict[str, str] | None = None
    rows: dict[str, dict[str, str]] = {}

    for raw_line in lines:
        line = raw_line.rstrip("\n")
        if line.startswith("capabilities:"):
            in_capabilities = True
            continue
        if not in_capabilities:
            continue
        if line.startswith("pipeline:"):
            break
        stripped = line.strip()
        if stripped.startswith("- id:"):
            if current and "id" in current:
                rows[current["id"]] = current
            current = {"id": stripped.split(":", 1)[1].strip()}
            continue
        if current is None:
            continue
        if stripped and ":" in stripped and not stripped.startswith("- "):
            key, value = stripped.split(":", 1)
            value = value.strip()
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            current[key] = value

    if current and "id" in current:
        rows[current["id"]] = current
    return rows


payload = parse_capabilities(MATRIX_PATH.read_text(encoding="utf-8"))
rows = []
score = 0.0
green = 0
amber = 0
red = 0

for capability_id, weight in TARGETS:
    row = payload.get(capability_id, {})
    status = row.get("status", "red").lower()
    factor = STATUS_FACTOR.get(status, 0.0)
    contribution = int(weight * factor)
    score += contribution
    if status == "green":
        green += 1
    elif status == "amber":
        amber += 1
    else:
        red += 1
    rows.append(
        {
            "id": capability_id,
            "status": status,
            "weight": weight,
            "contribution": contribution,
            "current_state": row.get("current_state", row.get("capability", "")),
            "gap": row.get("gap", ""),
            "validation": row.get("validation", ""),
        }
    )

result = {
    "score": int(score),
    "foundation_path": "juniper-estimation-plugin",
    "matrix_path": str(MATRIX_PATH),
    "counts": {
        "green": green,
        "amber": amber,
        "red": red,
        "total": len(TARGETS),
    },
    "targets": rows,
}

if "--json" in sys.argv[1:]:
    print(json.dumps(result, indent=2))
else:
    print(result["score"])
PY
