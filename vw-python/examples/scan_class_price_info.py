"""Scan the active Vectorworks document for cost/price-like data by class.

Run inside Vectorworks 2026 with the target VWX file open.

Outputs:
- worksheet: `Class Price Scan`
- CSV: `~/Desktop/vw_class_price_scan.csv`

The scan checks attached record fields on objects for field names containing:
cost, price, retail, vendor, total, unitcost, unit cost, amount, budget
"""

from __future__ import annotations

import csv
import os
from typing import Any

import vs  # type: ignore


WORKSHEET_NAME = "Class Price Scan"
CSV_NAME = "vw_class_price_scan.csv"
KEYWORDS = ("cost", "price", "retail", "vendor", "total", "amount", "budget")


def field_names(record_handle: Any) -> list[str]:
    names: list[str] = []
    if not record_handle:
        return names
    try:
        count = vs.NumFields(record_handle)
    except Exception:
        return names
    for index in range(1, count + 1):
        try:
            name = vs.GetFldName(record_handle, index)
        except Exception:
            name = ""
        if name:
            names.append(name)
    return names


def looks_like_price_field(name: str) -> bool:
    lowered = (name or "").strip().lower()
    return any(keyword in lowered for keyword in KEYWORDS)


def rebuild_worksheet(rows: list[dict[str, str]]) -> None:
    existing = vs.GetObject(WORKSHEET_NAME)
    if existing and vs.GetType(existing) == 18:
        try:
            vs.DelObject(existing)
        except Exception:
            pass

    ws = vs.CreateWS(WORKSHEET_NAME, max(len(rows) + 1, 2), 6)
    headers = ["Class Name", "Object Count", "Record Name", "Field Name", "Sample Value", "Handle"]
    for col, header in enumerate(headers, start=1):
        vs.SetWSCellFormulaN(ws, 1, col, 1, col, header)
    for row_idx, row in enumerate(rows, start=2):
        vs.SetWSCellFormulaN(ws, row_idx, 1, row_idx, 1, row["class_name"])
        vs.SetWSCellFormulaN(ws, row_idx, 2, row_idx, 2, row["object_count"])
        vs.SetWSCellFormulaN(ws, row_idx, 3, row_idx, 3, row["record_name"])
        vs.SetWSCellFormulaN(ws, row_idx, 4, row_idx, 4, row["field_name"])
        vs.SetWSCellFormulaN(ws, row_idx, 5, row_idx, 5, row["sample_value"])
        vs.SetWSCellFormulaN(ws, row_idx, 6, row_idx, 6, row["handle"])
    vs.ShowWS(ws, True)


def export_csv(rows: list[dict[str, str]]) -> str:
    path = os.path.join(os.path.expanduser("~/Desktop"), CSV_NAME)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["class_name", "object_count", "record_name", "field_name", "sample_value", "handle"])
        writer.writeheader()
        writer.writerows(rows)
    return path


def main() -> None:
    all_handles: list[Any] = []
    vs.ForEachObject(lambda h: all_handles.append(h), "(ALL)")

    object_counts: dict[str, int] = {}
    findings: list[dict[str, str]] = []

    for handle in all_handles:
        try:
            class_name = vs.GetClass(handle) or ""
        except Exception:
            continue
        if not class_name:
            continue
        object_counts[class_name] = object_counts.get(class_name, 0) + 1

        try:
            record_count = vs.NumRecords(handle)
        except Exception:
            record_count = 0
        if not record_count:
            continue

        for record_index in range(1, record_count + 1):
            try:
                record_handle = vs.GetRecord(handle, record_index)
            except Exception:
                record_handle = None
            if not record_handle:
                continue
            try:
                record_name = vs.GetName(record_handle) or ""
            except Exception:
                record_name = ""
            for field_name in field_names(record_handle):
                if not looks_like_price_field(field_name):
                    continue
                try:
                    value = vs.GetRField(handle, record_name, field_name) or ""
                except Exception:
                    value = ""
                if not value:
                    continue
                findings.append({
                    "class_name": class_name,
                    "object_count": "0",
                    "record_name": record_name,
                    "field_name": field_name,
                    "sample_value": str(value),
                    "handle": str(handle),
                })

    deduped: list[dict[str, str]] = []
    seen: set[tuple[str, str, str, str]] = set()
    for row in findings:
        key = (row["class_name"], row["record_name"], row["field_name"], row["sample_value"])
        if key in seen:
            continue
        seen.add(key)
        row["object_count"] = str(object_counts.get(row["class_name"], 0))
        deduped.append(row)

    deduped.sort(key=lambda row: (row["class_name"].lower(), row["record_name"].lower(), row["field_name"].lower()))
    csv_path = export_csv(deduped)
    rebuild_worksheet(deduped)

    vs.AlrtDialog(
        f"Scanned {len(all_handles)} objects.\n"
        f"Classes with cost-like data rows: {len({row['class_name'] for row in deduped})}\n"
        f"Finding rows: {len(deduped)}\n\n"
        f"Worksheet: {WORKSHEET_NAME}\n"
        f"CSV: {csv_path}"
    )


if __name__ == "__main__":
    main()
