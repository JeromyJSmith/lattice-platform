#!/usr/bin/env -S uv run python
"""Ingest Farber-Haines Vectorworks estimate exports into a project-scoped table."""

from __future__ import annotations

import argparse
import csv
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

from scripts._pxt_env import get_client  # noqa: E402

PROJECT_ID = "farber-haines-2521"
DEFAULT_SUMMARY_CSV = Path("/Users/ojeromyo/Desktop/vw_cost_estimate_summary.csv")
DEFAULT_OBJECT_CSV = Path("/Users/ojeromyo/Desktop/vw_cost_estimate_object_rows.csv")
DEFAULT_MAPPING_CSV = Path("/Users/ojeromyo/Desktop/vw_class_budget_mapping_first_pass.csv")
SUMMARY_TABLE = f"lattice/projects/{PROJECT_ID}/vw_estimate_rows"
OBJECT_TABLE = f"lattice/projects/{PROJECT_ID}/vw_estimate_objects"


def now() -> datetime:
    return datetime.now(timezone.utc)


def parse_float(value: str | None) -> float | None:
    if value is None:
        return None
    cleaned = "".join(ch for ch in str(value) if ch in "0123456789.-")
    if cleaned in {"", "-", ".", "-."}:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def create_dir_if_missing(pxt, path: str) -> None:
    try:
        pxt.create_dir(path)
    except Exception:
        pass


def ensure_table(pxt, path: str, schema: dict[str, object]) -> None:
    try:
        pxt.get_table(path)
        return
    except Exception:
        pass
    pxt.create_table(path, schema)


def read_mapping(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    by_class: dict[str, dict[str, str]] = {}
    for row in rows:
        class_name = (row.get("Class Name") or row.get("class_name") or "").strip()
        if class_name:
            by_class[class_name] = row
    return by_class


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def ensure_project_tables(pxt) -> None:
    create_dir_if_missing(pxt, "lattice/projects")
    create_dir_if_missing(pxt, f"lattice/projects/{PROJECT_ID}")
    ensure_table(pxt, SUMMARY_TABLE, {
        "id": pxt.String,
        "project_id": pxt.String,
        "ingest_run_id": pxt.String,
        "source_csv": pxt.String,
        "class_name": pxt.String,
        "description": pxt.String,
        "unit": pxt.String,
        "measure_basis": pxt.String,
        "quantity": pxt.Float,
        "unit_cost": pxt.Float,
        "total_cost": pxt.Float,
        "objects_counted": pxt.Int,
        "mapping_confidence": pxt.String,
        "budget_description": pxt.String,
        "budget_section": pxt.String,
        "notes": pxt.String,
        "ingested_at": pxt.Timestamp,
    })
    ensure_table(pxt, OBJECT_TABLE, {
        "id": pxt.String,
        "project_id": pxt.String,
        "ingest_run_id": pxt.String,
        "source_csv": pxt.String,
        "object_uuid": pxt.String,
        "class_name": pxt.String,
        "layer_name": pxt.String,
        "object_type": pxt.String,
        "description": pxt.String,
        "unit": pxt.String,
        "measure_basis": pxt.String,
        "quantity": pxt.Float,
        "unit_cost": pxt.Float,
        "total_cost": pxt.Float,
        "ingested_at": pxt.Timestamp,
    })


def replace_rows(table, project_id_column, project_id: str) -> None:
    try:
        table.delete(project_id_column == project_id)
    except Exception:
        pass


def ingest_summary(pxt, summary_csv: Path, mapping_csv: Path) -> int:
    table = pxt.get_table(SUMMARY_TABLE)
    replace_rows(table, table.project_id, PROJECT_ID)
    mapping = read_mapping(mapping_csv)
    rows = load_csv(summary_csv)
    ingest_run_id = f"summary-{now().strftime('%Y%m%dT%H%M%SZ')}"
    ingested_at = now()
    insert_rows: list[dict[str, object]] = []
    for row in rows:
        class_name = (row.get("Class Name") or "").strip()
        mapping_row = mapping.get(class_name, {})
        insert_rows.append({
            "id": uuid.uuid4().hex,
            "project_id": PROJECT_ID,
            "ingest_run_id": ingest_run_id,
            "source_csv": str(summary_csv),
            "class_name": class_name,
            "description": (row.get("Description") or "").strip(),
            "unit": (row.get("Unit") or "").strip(),
            "measure_basis": (row.get("Measure Basis") or "").strip(),
            "quantity": parse_float(row.get("Quantity")),
            "unit_cost": parse_float(row.get("Unit Cost")),
            "total_cost": parse_float(row.get("Total Cost")),
            "objects_counted": int(parse_float(row.get("Objects Counted")) or 0),
            "mapping_confidence": (mapping_row.get("confidence") or "").strip(),
            "budget_description": (mapping_row.get("matched budget description") or mapping_row.get("matched_budget_description") or "").strip(),
            "budget_section": (mapping_row.get("matched budget section") or mapping_row.get("matched_budget_section") or "").strip(),
            "notes": (mapping_row.get("notes") or "").strip(),
            "ingested_at": ingested_at,
        })
    if insert_rows:
        table.insert(insert_rows)
    return len(insert_rows)


def ingest_objects(pxt, object_csv: Path) -> int:
    if not object_csv.exists():
        return 0
    table = pxt.get_table(OBJECT_TABLE)
    replace_rows(table, table.project_id, PROJECT_ID)
    rows = load_csv(object_csv)
    ingest_run_id = f"objects-{now().strftime('%Y%m%dT%H%M%SZ')}"
    ingested_at = now()
    insert_rows: list[dict[str, object]] = []
    for row in rows:
        insert_rows.append({
            "id": uuid.uuid4().hex,
            "project_id": PROJECT_ID,
            "ingest_run_id": ingest_run_id,
            "source_csv": str(object_csv),
            "object_uuid": (row.get("Object UUID") or "").strip(),
            "class_name": (row.get("Class Name") or "").strip(),
            "layer_name": (row.get("Layer Name") or "").strip(),
            "object_type": (row.get("Object Type") or "").strip(),
            "description": (row.get("Description") or "").strip(),
            "unit": (row.get("Unit") or "").strip(),
            "measure_basis": (row.get("Measure Basis") or "").strip(),
            "quantity": parse_float(row.get("Quantity")),
            "unit_cost": parse_float(row.get("Unit Cost")),
            "total_cost": parse_float(row.get("Total Cost")),
            "ingested_at": ingested_at,
        })
    if insert_rows:
        table.insert(insert_rows)
    return len(insert_rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-csv", type=Path, default=DEFAULT_SUMMARY_CSV)
    parser.add_argument("--object-csv", type=Path, default=DEFAULT_OBJECT_CSV)
    parser.add_argument("--mapping-csv", type=Path, default=DEFAULT_MAPPING_CSV)
    args = parser.parse_args()

    if not args.summary_csv.exists():
        raise SystemExit(f"summary csv not found: {args.summary_csv}")

    pxt = get_client()
    ensure_project_tables(pxt)
    summary_count = ingest_summary(pxt, args.summary_csv, args.mapping_csv)
    object_count = ingest_objects(pxt, args.object_csv)
    print(json.dumps({
        "ok": True,
        "project_id": PROJECT_ID,
        "summary_table": SUMMARY_TABLE,
        "summary_rows": summary_count,
        "object_table": OBJECT_TABLE,
        "object_rows": object_count,
    }, default=str, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
