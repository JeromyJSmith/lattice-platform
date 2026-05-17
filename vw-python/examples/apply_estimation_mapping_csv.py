"""Apply estimation mappings to Vectorworks classes and objects from CSV.

Run inside Vectorworks 2026 with the target VWX file open.

Supported CSV headers:
- Class Name
- New Class Name / Target Class / Vectorworks Class (optional)
- Unit Cost
- Description
- Unit
- Apply / Enabled / Active (optional yes/no gate)

What it does:
- optionally renames class definitions
- optionally reclasses objects to a target class
- attaches/updates the `Project Cost` record on matching objects
- builds a worksheet summarizing what changed
"""

from __future__ import annotations

import csv
import os
from typing import Any

import vs  # type: ignore


RECORD_NAME = "Project Cost"
WORKSHEET_NAME = "Cost Mapping Update Report"

CONFIG = {
    "csv_path": "/Users/ojeromyo/Desktop/vw_cost_lookup_active_apply.csv",
    "target_layers": [],
    "create_missing_target_classes": True,
    "rename_class_definitions": False,
    "reclass_objects": True,
    "update_records": True,
    "include_subobjects": False,
    "skip_blank_cost_rows": True,
    "measure_rounding": 3,
    "currency_rounding": 2,
}

PRESET = globals().get("PRESET")
if isinstance(PRESET, dict):
    CONFIG.update(PRESET)

FIELD_NUMBER = 1
FIELD_TEXT = 4
AREA_UNITS = {"sf", "sqft", "sq ft"}
LENGTH_UNITS = {"lf", "lnft", "lin ft", "linear ft", "ff"}
COUNT_UNITS = {"ea", "each", "count"}
MANUAL_UNITS = {"cy", "yd", "yd3", "cu yd", "cubic yard", "ton", "tons"}


class MappingRow:
    def __init__(
        self,
        source_class: str,
        target_class: str,
        unit_cost: float,
        description: str,
        unit: str,
        enabled: bool,
    ) -> None:
        self.source_class = source_class
        self.target_class = target_class
        self.unit_cost = unit_cost
        self.description = description
        self.unit = unit
        self.enabled = enabled


def alert(message: str) -> None:
    vs.AlrtDialog(message)


def normalize_header(value: str) -> str:
    return "".join(ch.lower() for ch in (value or "").strip() if ch.isalnum())


def parse_float(value: Any) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = "".join(ch for ch in str(value) if ch in "0123456789.-")
    if cleaned in {"", "-", ".", "-."}:
        return 0.0
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def parse_bool(value: str) -> bool:
    text = (value or "").strip().lower()
    if not text:
        return True
    return text not in {"0", "false", "no", "n", "off"}


def round_measure(value: float) -> float:
    return round(value, int(CONFIG["measure_rounding"]))


def round_currency(value: float) -> float:
    return round(value, int(CONFIG["currency_rounding"]))


def normalize_unit(value: str) -> str:
    return "".join(ch.lower() for ch in (value or "").strip() if ch.isalnum() or ch == " ")


def class_exists(name: str) -> bool:
    return bool(name and vs.GetObject(name))


def ensure_class(name: str) -> None:
    if name and not class_exists(name):
        vs.NameClass(name)


def field_names(record_handle: Any) -> set[str]:
    names: set[str] = set()
    if not record_handle:
        return names
    count = vs.NumFields(record_handle)
    for index in range(1, count + 1):
        names.add(vs.GetFldName(record_handle, index))
    return names


def ensure_record_format() -> None:
    record_handle = vs.GetObject(RECORD_NAME)
    existing = field_names(record_handle)
    desired = [
        ("Unit Cost", "0", FIELD_NUMBER, 0),
        ("Quantity", "0", FIELD_NUMBER, 0),
        ("Total Cost", "0", FIELD_NUMBER, 0),
        ("Description", "", FIELD_TEXT, 0),
        ("Unit", "", FIELD_TEXT, 0),
        ("Measure Basis", "", FIELD_TEXT, 0),
    ]
    for name, default, field_type, flag in desired:
        if name not in existing:
            vs.NewField(RECORD_NAME, name, default, field_type, flag)


def object_geometry_measure(handle: Any) -> tuple[float, float]:
    area = 0.0
    length = 0.0
    try:
        area = float(vs.ObjArea(handle) or 0.0)
    except Exception:
        area = 0.0
    try:
        length = float(vs.HLength(handle) or 0.0)
    except Exception:
        length = 0.0
    return area, length


def object_measure(handle: Any, unit: str) -> tuple[str, float]:
    area, length_inches = object_geometry_measure(handle)
    unit_key = normalize_unit(unit)
    if unit_key in AREA_UNITS:
        return "Area", round_measure(area)
    if unit_key in LENGTH_UNITS:
        return "Length", round_measure(length_inches / 12.0)
    if unit_key in COUNT_UNITS:
        return "Count", 1.0
    # Volume and mass-based budget rows need explicit project conversion rules.
    if unit_key in MANUAL_UNITS:
        return "Manual Review", 0.0
    if area > 0:
        return "Area", round_measure(area)
    if length_inches > 0:
        return "Length", round_measure(length_inches / 12.0)
    return "Count", 1.0


def load_mappings(path: str) -> list[MappingRow]:
    if not os.path.exists(path):
        raise RuntimeError(f"CSV not found: {path}")

    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise RuntimeError("CSV has no headers.")

        columns = {normalize_header(name): name for name in reader.fieldnames}

        def col(*names: str) -> str | None:
            for name in names:
                hit = columns.get(normalize_header(name))
                if hit:
                    return hit
            return None

        source_col = col("Class Name", "Class", "Source Class")
        target_col = col("New Class Name", "Target Class", "Vectorworks Class")
        cost_col = col("Unit Cost", "UnitPrice", "Price")
        desc_col = col("Description", "Budget Description", "Item")
        unit_col = col("Unit", "UOM")
        enabled_col = col("Apply", "Enabled", "Active")

        if not source_col:
            raise RuntimeError("CSV must include 'Class Name'.")

        rows: list[MappingRow] = []
        for raw in reader:
            source_class = (raw.get(source_col, "") or "").strip()
            if not source_class:
                continue

            target_class = source_class
            if target_col:
                target_class = (raw.get(target_col, "") or "").strip() or source_class

            unit_cost = parse_float(raw.get(cost_col, "")) if cost_col else 0.0
            description = (raw.get(desc_col, "") or "").strip() if desc_col else ""
            unit = (raw.get(unit_col, "") or "").strip() if unit_col else ""
            enabled = parse_bool(raw.get(enabled_col, "")) if enabled_col else True

            if CONFIG["skip_blank_cost_rows"] and not description and not unit and unit_cost == 0:
                enabled = False

            rows.append(MappingRow(
                source_class=source_class,
                target_class=target_class,
                unit_cost=unit_cost,
                description=description,
                unit=unit,
                enabled=enabled,
            ))

    if not rows:
        raise RuntimeError("No usable rows found in CSV.")
    return rows


def safe_parent_type(handle: Any) -> int | None:
    try:
        parent = vs.GetParent(handle)
        if not parent:
            return None
        return vs.GetType(parent)
    except Exception:
        return None


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


def should_skip_subobject(handle: Any) -> bool:
    if CONFIG["include_subobjects"]:
        return False
    return safe_parent_type(handle) in {11, 15, 86, 122}


def delete_existing_worksheet() -> None:
    worksheet = vs.GetObject(WORKSHEET_NAME)
    if worksheet and vs.GetType(worksheet) == 18:
        try:
            vs.DelObject(worksheet)
        except Exception:
            pass


def set_cell_text(worksheet: Any, row: int, column: int, value: str) -> None:
    vs.SetWSCellFormulaN(worksheet, row, column, row, column, value)


def create_report_worksheet(rows: list[dict[str, str]]) -> None:
    delete_existing_worksheet()
    worksheet = vs.CreateWS(WORKSHEET_NAME, max(len(rows) + 1, 2), 7)
    headers = [
        "Source Class",
        "Target Class",
        "Objects Updated",
        "Class Renamed",
        "Record Updated",
        "Unit Cost",
        "Description",
    ]
    for idx, header in enumerate(headers, start=1):
        set_cell_text(worksheet, 1, idx, header)
    for row_idx, row in enumerate(rows, start=2):
        set_cell_text(worksheet, row_idx, 1, row["source_class"])
        set_cell_text(worksheet, row_idx, 2, row["target_class"])
        set_cell_text(worksheet, row_idx, 3, row["objects_updated"])
        set_cell_text(worksheet, row_idx, 4, row["class_renamed"])
        set_cell_text(worksheet, row_idx, 5, row["record_updated"])
        set_cell_text(worksheet, row_idx, 6, row["unit_cost"])
        set_cell_text(worksheet, row_idx, 7, row["description"])
    vs.ShowWS(worksheet, True)


def main() -> None:
    ensure_record_format()
    mappings = load_mappings(CONFIG["csv_path"])

    by_source = {row.source_class: row for row in mappings if row.enabled}

    if CONFIG["create_missing_target_classes"]:
        for mapping in by_source.values():
            ensure_class(mapping.target_class)

    rename_results: dict[str, bool] = {}
    if CONFIG["rename_class_definitions"]:
        for mapping in by_source.values():
            if mapping.source_class != mapping.target_class and class_exists(mapping.source_class):
                try:
                    vs.RenameClass(mapping.source_class, mapping.target_class)
                    rename_results[mapping.source_class] = True
                except Exception:
                    rename_results[mapping.source_class] = False

    all_handles: list[Any] = []
    vs.ForEachObject(lambda h: all_handles.append(h), "(ALL)")

    per_class_counts: dict[str, int] = {key: 0 for key in by_source}
    per_class_record: dict[str, bool] = {key: False for key in by_source}

    for handle in all_handles:
        if should_skip_subobject(handle):
            continue
        if not layer_is_allowed(handle):
            continue
        try:
            current_class = vs.GetClass(handle)
        except Exception:
            continue
        mapping = by_source.get(current_class)
        if not mapping:
            continue

        if CONFIG["reclass_objects"] and mapping.target_class and mapping.target_class != current_class:
            try:
                vs.SetClass(handle, mapping.target_class)
            except Exception:
                pass

        if CONFIG["update_records"]:
            basis, quantity = object_measure(handle, mapping.unit)
            total_cost = round_currency(mapping.unit_cost * quantity)
            vs.SetRecord(handle, RECORD_NAME)
            vs.SetRField(handle, RECORD_NAME, "Unit Cost", str(round_currency(mapping.unit_cost)))
            vs.SetRField(handle, RECORD_NAME, "Quantity", str(quantity))
            vs.SetRField(handle, RECORD_NAME, "Total Cost", str(total_cost))
            vs.SetRField(handle, RECORD_NAME, "Description", mapping.description)
            vs.SetRField(handle, RECORD_NAME, "Unit", mapping.unit)
            vs.SetRField(handle, RECORD_NAME, "Measure Basis", basis)
            per_class_record[current_class] = True

        per_class_counts[current_class] = per_class_counts.get(current_class, 0) + 1

    report_rows: list[dict[str, str]] = []
    for source_class, mapping in by_source.items():
        report_rows.append({
            "source_class": source_class,
            "target_class": mapping.target_class,
            "objects_updated": str(per_class_counts.get(source_class, 0)),
            "class_renamed": "yes" if rename_results.get(source_class) else "",
            "record_updated": "yes" if per_class_record.get(source_class) else "",
            "unit_cost": str(round_currency(mapping.unit_cost)) if mapping.unit_cost else "",
            "description": mapping.description,
        })

    create_report_worksheet(report_rows)

    touched = sum(per_class_counts.values())
    active = len(by_source)
    renamed = sum(1 for value in rename_results.values() if value)
    alert(
        "Estimation mapping applied.\n\n"
        f"Active mapping rows: {active}\n"
        f"Objects updated: {touched}\n"
        f"Classes renamed: {renamed}\n"
        f"Worksheet: {WORKSHEET_NAME}"
    )


if __name__ == "__main__":
    main()
