"""Export a class-level estimate summary from attached Project Cost records.

Run inside Vectorworks with the target VWX file open after applying estimation
mapping. Produces:
- worksheet: `Cost Estimate Summary`
- CSV: `~/Desktop/vw_cost_estimate_summary.csv`
"""

from __future__ import annotations

import csv
import os
from collections import defaultdict
from typing import Any

import vs  # type: ignore


RECORD_NAME = "Project Cost"
WORKSHEET_NAME = "Cost Estimate Summary"
CSV_NAME = "vw_cost_estimate_summary.csv"
FIELDS = ["Description", "Unit", "Measure Basis", "Quantity", "Unit Cost", "Total Cost"]
CONFIG = {
    "target_layers": [],
}

PRESET = globals().get("PRESET")
if isinstance(PRESET, dict):
    CONFIG.update(PRESET)


def parse_float(value: str) -> float:
    cleaned = "".join(ch for ch in (value or "") if ch in "0123456789.-")
    if cleaned in {"", "-", ".", "-."}:
        return 0.0
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def safe_field(handle: Any, field: str) -> str:
    try:
        return str(vs.GetRField(handle, RECORD_NAME, field) or "").strip()
    except Exception:
        return ""


def handle_layer_name(handle: Any) -> str:
    try:
        layer_handle = vs.GetLayer(handle)
        if not layer_handle:
            return ""
        return str(vs.GetLName(layer_handle) or "").strip()
    except Exception:
        return ""


def layer_is_allowed(handle: Any) -> bool:
    target_layers = [str(name).strip() for name in CONFIG.get("target_layers", []) if str(name).strip()]
    if not target_layers:
        return True
    return handle_layer_name(handle) in set(target_layers)


def delete_existing_worksheet() -> None:
    worksheet = vs.GetObject(WORKSHEET_NAME)
    if worksheet and vs.GetType(worksheet) == 18:
        try:
            vs.DelObject(worksheet)
        except Exception:
            pass


def set_cell_text(worksheet: Any, row: int, column: int, value: str) -> None:
    vs.SetWSCellFormulaN(worksheet, row, column, row, column, value)


def export_csv(rows: list[dict[str, str]]) -> str:
    path = os.path.join(os.path.expanduser("~/Desktop"), CSV_NAME)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "Class Name",
            "Description",
            "Unit",
            "Measure Basis",
            "Quantity",
            "Unit Cost",
            "Total Cost",
            "Objects Counted",
        ])
        writer.writeheader()
        writer.writerows(rows)
    return path


def build_summary() -> list[dict[str, str]]:
    handles: list[Any] = []
    vs.ForEachObject(lambda h: handles.append(h), f"(R IN ['{RECORD_NAME}'])")

    grouped: dict[tuple[str, str, str, str, str], dict[str, float | int]] = defaultdict(
        lambda: {"quantity": 0.0, "total_cost": 0.0, "count": 0}
    )

    for handle in handles:
        if not layer_is_allowed(handle):
            continue
        try:
            class_name = vs.GetClass(handle) or ""
        except Exception:
            class_name = ""
        if not class_name:
            continue
        description = safe_field(handle, "Description")
        unit = safe_field(handle, "Unit")
        basis = safe_field(handle, "Measure Basis")
        quantity = parse_float(safe_field(handle, "Quantity"))
        unit_cost = safe_field(handle, "Unit Cost")
        total_cost = parse_float(safe_field(handle, "Total Cost"))
        key = (class_name, description, unit, basis, unit_cost)
        grouped[key]["quantity"] += quantity
        grouped[key]["total_cost"] += total_cost
        grouped[key]["count"] += 1

    rows: list[dict[str, str]] = []
    for key in sorted(grouped, key=lambda item: (item[0].lower(), item[1].lower())):
        class_name, description, unit, basis, unit_cost = key
        aggregate = grouped[key]
        rows.append({
            "Class Name": class_name,
            "Description": description,
            "Unit": unit,
            "Measure Basis": basis,
            "Quantity": str(round(float(aggregate["quantity"]), 3)),
            "Unit Cost": unit_cost,
            "Total Cost": str(round(float(aggregate["total_cost"]), 2)),
            "Objects Counted": str(int(aggregate["count"])),
        })
    return rows


def create_worksheet(rows: list[dict[str, str]]) -> None:
    delete_existing_worksheet()
    worksheet = vs.CreateWS(WORKSHEET_NAME, max(len(rows) + 1, 2), 8)
    headers = [
        "Class Name",
        "Description",
        "Unit",
        "Measure Basis",
        "Quantity",
        "Unit Cost",
        "Total Cost",
        "Objects Counted",
    ]
    for idx, header in enumerate(headers, start=1):
        set_cell_text(worksheet, 1, idx, header)
    for row_idx, row in enumerate(rows, start=2):
        for col_idx, header in enumerate(headers, start=1):
            set_cell_text(worksheet, row_idx, col_idx, row[header])
    vs.ShowWS(worksheet, True)


def main() -> None:
    rows = build_summary()
    csv_path = export_csv(rows)
    create_worksheet(rows)
    vs.AlrtDialog(
        f"Exported {len(rows)} summary rows.\n"
        f"Worksheet: {WORKSHEET_NAME}\n"
        f"CSV: {csv_path}"
    )


if __name__ == "__main__":
    main()
