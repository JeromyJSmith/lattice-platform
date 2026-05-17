"""Apply a conservative IFC entity map in the active Vectorworks file.

Run inside Vectorworks 2026 with the target VWX file open.

This script distinguishes between:

- direct-attach classes that accept scripted IFC assignment today
- alternate-path classes that require Data Manager or object-type-specific
  handling and should be reported, not blindly retried
"""

from __future__ import annotations

import os
from typing import Any

import vs  # type: ignore


WORKSHEET_NAME = "IFC Entity Update Report"
CSV_NAME = "farber_haines_ifc_entity_update_report.csv"

CONFIG = {
    "apply_changes": False,
    "report_csv_dir": os.path.expanduser("~/Desktop"),
}

CLASS_RULES = {
    "L-Boulder": {
        "entity": "IfcGeographicElement",
        "strategy": "alternate",
        "notes": "Direct IFC setters return false on sampled boulder objects; use Data Manager or object-type-specific assignment.",
    },
    "L-Tree-Proposed": {
        "entity": "IfcGeographicElement",
        "strategy": "alternate",
        "notes": "Plant PIOs reject direct IFC setters in this file; solve through Data Manager or plant-style workflow.",
    },
    "L-Plant-Proposed": {
        "entity": "IfcGeographicElement",
        "strategy": "alternate",
        "notes": "Plant PIOs reject direct IFC setters in this file; solve through Data Manager or plant-style workflow.",
    },
    "L-Tree-Existing": {
        "entity": "IfcGeographicElement",
        "strategy": "alternate",
        "notes": "Existing Tree PIOs reject direct IFC setters in this file; solve through Data Manager or existing-tree workflow.",
    },
    "L-Tree-Removed": {
        "entity": "IfcGeographicElement",
        "strategy": "alternate",
        "notes": "Existing Tree PIOs reject direct IFC setters in this file; solve through Data Manager or existing-tree workflow.",
    },
    "L-Floor-Concrete-Sand Finish": {
        "entity": "IfcSlab",
        "strategy": "direct",
        "notes": "Verified direct scripted attach.",
    },
    "L-Floor-Concrete-Driveway Broom Finish": {
        "entity": "IfcSlab",
        "strategy": "direct",
        "notes": "Verified direct scripted attach.",
    },
    "L-Floor-Concrete Standard": {
        "entity": "IfcSlab",
        "strategy": "direct",
        "notes": "Verified direct scripted attach.",
    },
    "L-Floor-Concrete Patios": {
        "entity": "IfcSlab",
        "strategy": "direct",
        "notes": "Verified direct scripted attach.",
    },
    "L-Detail Material-Concrete": {
        "entity": "IfcSlab",
        "strategy": "direct",
        "notes": "Verified direct scripted attach.",
    },
    "3D-hardscape": {
        "entity": "IfcSlab",
        "strategy": "direct",
        "notes": "Verified direct scripted attach.",
    },
    "L-Gravel": {
        "entity": "IfcSlab",
        "strategy": "direct",
        "notes": "Verified direct scripted attach.",
    },
    "L-Detail Material-Gravel": {
        "entity": "IfcSlab",
        "strategy": "direct",
        "notes": "Verified direct scripted attach.",
    },
    "L-Lawn": {
        "entity": "IfcSlab",
        "strategy": "direct",
        "notes": "Verified direct scripted attach for this landscape area geometry.",
    },
    "L-Edge-Roll Top Metal": {
        "entity": "IfcKerb",
        "strategy": "alternate",
        "notes": "Direct IFC setters return false on sampled edging objects; use Data Manager or object-type-specific assignment.",
    },
}


def safe_get_ifc_entity(handle: Any) -> str:
    try:
        ok, name = vs.IFC_GetIFCEntity(handle)
        if ok and name:
            return str(name).strip()
    except Exception:
        return ""
    return ""


def safe_set_ifc_entity(handle: Any, entity: str) -> bool:
    try:
        return bool(vs.IFC_SetIFCEntity2(handle, entity))
    except Exception:
        return False


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
    import csv

    path = os.path.join(CONFIG["report_csv_dir"], CSV_NAME)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "Class Name",
            "Recommended IFC Entity",
            "Apply Strategy",
            "Objects Seen",
            "Objects Already Correct",
            "Objects Updated",
            "Dry Run Pending",
            "Notes",
        ])
        writer.writeheader()
        writer.writerows(rows)
    return path


def create_worksheet(rows: list[dict[str, str]]) -> None:
    delete_existing_worksheet()
    worksheet = vs.CreateWS(WORKSHEET_NAME, max(len(rows) + 1, 2), 8)
    headers = [
        "Class Name",
        "Recommended IFC Entity",
        "Apply Strategy",
        "Objects Seen",
        "Objects Already Correct",
        "Objects Updated",
        "Dry Run Pending",
        "Notes",
    ]
    for idx, header in enumerate(headers, start=1):
        set_cell_text(worksheet, 1, idx, header)
    for row_idx, row in enumerate(rows, start=2):
        for col_idx, header in enumerate(headers, start=1):
            set_cell_text(worksheet, row_idx, col_idx, row[header])
    vs.ShowWS(worksheet, True)


def main() -> None:
    handles: list[Any] = []
    vs.ForEachObject(lambda h: handles.append(h), "(ALL)")

    summary: dict[str, dict[str, int | str]] = {}
    for class_name, rule in CLASS_RULES.items():
        summary[class_name] = {
            "entity": rule["entity"],
            "strategy": rule["strategy"],
            "notes": rule["notes"],
            "seen": 0,
            "already": 0,
            "updated": 0,
            "pending": 0,
        }

    for handle in handles:
        try:
            class_name = vs.GetClass(handle) or ""
        except Exception:
            continue
        rule = CLASS_RULES.get(class_name)
        if not rule:
            continue

        summary[class_name]["seen"] += 1
        entity = str(rule["entity"])
        current = safe_get_ifc_entity(handle)
        if current == entity:
            summary[class_name]["already"] += 1
            continue

        if rule["strategy"] != "direct":
            summary[class_name]["pending"] += 1
            continue

        if CONFIG["apply_changes"]:
            if safe_set_ifc_entity(handle, entity):
                summary[class_name]["updated"] += 1
        else:
            summary[class_name]["pending"] += 1

    rows: list[dict[str, str]] = []
    for class_name in sorted(CLASS_RULES):
        item = summary[class_name]
        if int(item["seen"]) == 0:
            continue
        rows.append({
            "Class Name": class_name,
            "Recommended IFC Entity": str(item["entity"]),
            "Apply Strategy": str(item["strategy"]),
            "Objects Seen": str(item["seen"]),
            "Objects Already Correct": str(item["already"]),
            "Objects Updated": str(item["updated"]),
            "Dry Run Pending": str(item["pending"]),
            "Notes": str(item["notes"]),
        })

    csv_path = export_csv(rows)
    create_worksheet(rows)
    mode = "apply" if CONFIG["apply_changes"] else "dry run"
    vs.AlrtDialog(
        f"IFC entity recommendation {mode} complete.\n\n"
        f"Classes touched: {len(rows)}\n"
        f"CSV: {csv_path}\n"
        f"Worksheet: {WORKSHEET_NAME}"
    )


if __name__ == "__main__":
    main()
