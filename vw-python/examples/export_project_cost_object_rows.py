"""Export per-object estimate rows from attached Project Cost records.

Run inside Vectorworks with the target VWX file open after applying estimation
mapping. Produces:
- worksheet: `Cost Estimate Object Rows`
- CSV: `~/Desktop/vw_cost_estimate_object_rows.csv`
"""

from __future__ import annotations

import csv
import os
from typing import Any

import vs  # type: ignore


RECORD_NAME = "Project Cost"
WORKSHEET_NAME = "Cost Estimate Object Rows"
CSV_NAME = "vw_cost_estimate_object_rows.csv"
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


def collect_rows() -> list[dict[str, str]]:
    handles: list[Any] = []
    vs.ForEachObject(lambda h: handles.append(h), f"(R IN ['{RECORD_NAME}'])")

    rows: list[dict[str, str]] = []
    for handle in handles:
        if not layer_is_allowed(handle):
            continue
        object_uuid = ""
        class_name = ""
        layer_name = handle_layer_name(handle)
        object_type = ""
        try:
            object_uuid = str(vs.GetObjectUuid(handle) or "").strip()
        except Exception:
            pass
        try:
            class_name = str(vs.GetClass(handle) or "").strip()
        except Exception:
            pass
        try:
            object_type = str(vs.GetTypeN(handle))
        except Exception:
            pass

        quantity = safe_field(handle, "Quantity")
        unit_cost = safe_field(handle, "Unit Cost")
        total_cost = safe_field(handle, "Total Cost")

        rows.append({
            "Object UUID": object_uuid,
            "Class Name": class_name,
            "Layer Name": layer_name,
            "Object Type": object_type,
            "Description": safe_field(handle, "Description"),
            "Unit": safe_field(handle, "Unit"),
            "Measure Basis": safe_field(handle, "Measure Basis"),
            "Quantity": str(round(parse_float(quantity), 3)),
            "Unit Cost": unit_cost,
            "Total Cost": str(round(parse_float(total_cost), 2)),
        })

    rows.sort(key=lambda row: (
        row["Class Name"].lower(),
        row["Description"].lower(),
        row["Object UUID"].lower(),
    ))
    return rows


def export_csv(rows: list[dict[str, str]]) -> str:
    path = os.path.join(os.path.expanduser("~/Desktop"), CSV_NAME)
    headers = [
        "Object UUID",
        "Class Name",
        "Layer Name",
        "Object Type",
        "Description",
        "Unit",
        "Measure Basis",
        "Quantity",
        "Unit Cost",
        "Total Cost",
    ]
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    return path


def create_worksheet(rows: list[dict[str, str]]) -> None:
    delete_existing_worksheet()
    headers = [
        "Object UUID",
        "Class Name",
        "Layer Name",
        "Object Type",
        "Description",
        "Unit",
        "Measure Basis",
        "Quantity",
        "Unit Cost",
        "Total Cost",
    ]
    worksheet = vs.CreateWS(WORKSHEET_NAME, max(len(rows) + 1, 2), len(headers))
    for idx, header in enumerate(headers, start=1):
        set_cell_text(worksheet, 1, idx, header)
    for row_idx, row in enumerate(rows, start=2):
        for col_idx, header in enumerate(headers, start=1):
            set_cell_text(worksheet, row_idx, col_idx, row[header])
    vs.ShowWS(worksheet, True)


def main() -> None:
    rows = collect_rows()
    csv_path = export_csv(rows)
    create_worksheet(rows)
    vs.AlrtDialog(
        f"Exported {len(rows)} object rows.\n"
        f"Worksheet: {WORKSHEET_NAME}\n"
        f"CSV: {csv_path}"
    )


if __name__ == "__main__":
    main()
