"""Build a Vectorworks cost record and worksheet from an .xlsx cost library.

Usage:
1. Export your Numbers workbook to `.xlsx` if needed.
2. Point CONFIG at a normalized cost-library sheet with these columns:
   `class name`, `unit cost`, `description`, and `unit`.
3. Open the target VWX file in Vectorworks 2026.
4. Run this script from Tools > Plug-ins > Run Script.

The script:
- creates/updates a `Project Cost` record format
- reads a pricing workbook keyed by class name
- attaches the record to matching objects across the document
- writes unit cost, description, unit, measure basis, quantity, and total cost
- builds a `Cost Estimate` worksheet for all objects carrying that record

This script reads `.xlsx` directly with Python. If your source file is still a
`.numbers` workbook, export it to `.xlsx` first.
"""

from __future__ import annotations

import math
import os
import re
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass
from typing import Any

import vs  # type: ignore


RECORD_NAME = "Project Cost"
WORKSHEET_NAME = "Cost Estimate"


CONFIG = {
    "xlsx_path": "/Volumes/PixelTable/GROVE_HARNESS/juniper2026/MARPA_CONSTRUCTION_ESTIMATING 2/2026-04.22_Farber-Haines_SD_Budget1 copy.xlsx",
    "sheet_name": "BUDGET",
    "header_aliases": {
        "class_name": [
            "class name",
            "class",
            "vw class",
            "vectorworks class",
        ],
        "unit_cost": [
            "unit cost",
            "unit price",
            "retail unit price",
            "price",
        ],
        "description": [
            "description",
            "item",
            "scope of work",
        ],
        "unit": [
            "unit",
            "uom",
        ],
    },
    "fallback_columns": {
        "class_name": "A",
        "unit_cost": "B",
        "description": "C",
        "unit": "D",
    },
    "target_classes": [],
    "skip_classes": [
        "None",
        "Dimension",
    ],
    "include_subobjects": False,
    "measure_rounding": 3,
    "currency_rounding": 2,
}


FIELD_NUMBER = 1
FIELD_BOOLEAN = 2
FIELD_TEXT = 4

NS_MAIN = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
NS_REL = {"r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}


@dataclass
class CostRow:
    class_name: str
    unit_cost: float
    description: str
    unit: str


def alert(message: str) -> None:
    vs.AlrtDialog(message)


def message(message_text: str) -> None:
    try:
        vs.Message(message_text)
    except Exception:
        pass


def normalize_label(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (value or "").strip().lower()).strip()


def normalize_class(value: str) -> str:
    return (value or "").strip()


def col_letter_to_index(value: str) -> int:
    result = 0
    for ch in value.strip().upper():
        if "A" <= ch <= "Z":
            result = result * 26 + (ord(ch) - ord("A") + 1)
    return max(result - 1, 0)


def parse_float(value: Any) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = re.sub(r"[^0-9.\-]", "", str(value))
    if cleaned in {"", "-", ".", "-."}:
        return 0.0
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def read_shared_strings(book: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in book.namelist():
        return []
    root = ET.fromstring(book.read("xl/sharedStrings.xml"))
    strings: list[str] = []
    for si in root.findall("a:si", NS_MAIN):
        strings.append("".join((t.text or "") for t in si.iterfind(".//a:t", NS_MAIN)))
    return strings


def workbook_sheets(book: zipfile.ZipFile) -> list[tuple[str, str]]:
    workbook = ET.fromstring(book.read("xl/workbook.xml"))
    rels = ET.fromstring(book.read("xl/_rels/workbook.xml.rels"))
    rel_map = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels}
    sheets: list[tuple[str, str]] = []
    for sheet in workbook.findall("a:sheets/a:sheet", NS_MAIN):
        name = sheet.attrib.get("name", "")
        rel_id = sheet.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id", "")
        target = rel_map.get(rel_id, "")
        if target:
            sheets.append((name, f"xl/{target}"))
    return sheets


def parse_sheet_rows(book: zipfile.ZipFile, sheet_target: str, shared_strings: list[str]) -> list[list[str]]:
    root = ET.fromstring(book.read(sheet_target))
    rows: list[list[str]] = []
    for row in root.findall(".//a:sheetData/a:row", NS_MAIN):
        row_values: list[str] = []
        cells = row.findall("a:c", NS_MAIN)
        max_idx = -1
        for cell in cells:
            ref = cell.attrib.get("r", "")
            letters = "".join(ch for ch in ref if ch.isalpha())
            idx = col_letter_to_index(letters) if letters else len(row_values)
            while len(row_values) < idx:
                row_values.append("")
            cell_type = cell.attrib.get("t")
            formula = cell.find("a:f", NS_MAIN)
            value = cell.find("a:v", NS_MAIN)
            text = ""
            if value is not None and value.text is not None:
                text = value.text
                if cell_type == "s":
                    try:
                        text = shared_strings[int(text)]
                    except Exception:
                        pass
                elif cell_type == "b":
                    text = "TRUE" if text == "1" else "FALSE"
            elif formula is not None and formula.text is not None:
                text = formula.text
            if idx < len(row_values):
                row_values[idx] = text
            else:
                row_values.append(text)
            max_idx = max(max_idx, idx)
        if max_idx >= 0:
            while len(row_values) <= max_idx:
                row_values.append("")
        rows.append(row_values)
    return rows


def find_source_sheet(book: zipfile.ZipFile, sheet_name: str | None) -> tuple[str, str]:
    sheets = workbook_sheets(book)
    if not sheets:
        raise RuntimeError("No worksheets found in workbook.")
    if sheet_name:
        wanted = normalize_label(sheet_name)
        for name, target in sheets:
            if normalize_label(name) == wanted:
                return name, target
        available = ", ".join(name for name, _ in sheets)
        raise RuntimeError(f"Sheet '{sheet_name}' not found. Available sheets: {available}")
    return sheets[0]


def detect_header_row(rows: list[list[str]]) -> tuple[int, dict[str, int]]:
    aliases = {
        key: {normalize_label(v) for v in values}
        for key, values in CONFIG["header_aliases"].items()
    }
    for row_idx, row in enumerate(rows[:20]):
        normalized = [normalize_label(cell) for cell in row]
        found: dict[str, int] = {}
        for key, allowed in aliases.items():
            for idx, label in enumerate(normalized):
                if label in allowed:
                    found[key] = idx
                    break
        if len(found) >= 3 and "class_name" in found and "unit_cost" in found:
            return row_idx, found

    fallback = {
        key: col_letter_to_index(value)
        for key, value in CONFIG["fallback_columns"].items()
    }
    return 0, fallback


def load_cost_rows(path: str, sheet_name: str | None) -> dict[str, CostRow]:
    if not os.path.exists(path):
        raise RuntimeError(f"Workbook not found: {path}")
    if not path.lower().endswith(".xlsx"):
        raise RuntimeError("This script reads .xlsx files. Export Numbers to .xlsx first.")

    with zipfile.ZipFile(path) as book:
        shared_strings = read_shared_strings(book)
        selected_sheet_name, selected_target = find_source_sheet(book, sheet_name)
        rows = parse_sheet_rows(book, selected_target, shared_strings)

    header_row_idx, columns = detect_header_row(rows)
    result: dict[str, CostRow] = {}
    for row in rows[header_row_idx + 1:]:
        class_name = normalize_class(row[columns["class_name"]]) if columns["class_name"] < len(row) else ""
        unit_cost_raw = row[columns["unit_cost"]] if columns["unit_cost"] < len(row) else ""
        description = row[columns["description"]] if columns["description"] < len(row) else ""
        unit = row[columns["unit"]] if columns["unit"] < len(row) else ""

        if not class_name:
            continue

        unit_cost = parse_float(unit_cost_raw)
        result[class_name] = CostRow(
            class_name=class_name,
            unit_cost=unit_cost,
            description=description.strip(),
            unit=unit.strip(),
        )

    if not result:
        raise RuntimeError(f"No usable rows found in sheet '{selected_sheet_name}'.")
    return result


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


def round_measure(value: float) -> float:
    return round(value, int(CONFIG["measure_rounding"]))


def round_currency(value: float) -> float:
    return round(value, int(CONFIG["currency_rounding"]))


def object_measure(handle: Any) -> tuple[str, float]:
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

    if area > 0:
        return "Area", round_measure(area)
    if length > 0:
        return "Length", round_measure(length)
    return "Count", 1.0


def should_process_class(class_name: str, cost_map: dict[str, CostRow]) -> bool:
    if class_name in CONFIG["skip_classes"]:
        return False
    target_classes = CONFIG["target_classes"]
    if target_classes:
        return class_name in target_classes
    return class_name in cost_map


def attach_cost_records(cost_map: dict[str, CostRow]) -> tuple[int, list[str]]:
    touched = 0
    missing_classes: set[str] = set()
    include_subobjects = bool(CONFIG["include_subobjects"])

    all_handles: list[Any] = []
    vs.ForEachObject(lambda h: all_handles.append(h), "")

    for handle in all_handles:
        try:
            class_name = vs.GetClass(handle)
        except Exception:
            continue
        if not class_name or not should_process_class(class_name, cost_map):
            continue
        cost = cost_map.get(class_name)
        if cost is None:
            missing_classes.add(class_name)
            continue

        parent = None
        try:
            parent = vs.GetParent(handle)
        except Exception:
            parent = None
        if not include_subobjects and parent and vs.GetType(parent) in {11, 15, 86, 122}:
            continue

        basis, quantity = object_measure(handle)
        total_cost = round_currency(cost.unit_cost * quantity)

        vs.SetRecord(handle, RECORD_NAME)
        vs.SetRField(handle, RECORD_NAME, "Unit Cost", str(round_currency(cost.unit_cost)))
        vs.SetRField(handle, RECORD_NAME, "Quantity", str(quantity))
        vs.SetRField(handle, RECORD_NAME, "Total Cost", str(total_cost))
        vs.SetRField(handle, RECORD_NAME, "Description", cost.description)
        vs.SetRField(handle, RECORD_NAME, "Unit", cost.unit)
        vs.SetRField(handle, RECORD_NAME, "Measure Basis", basis)
        touched += 1

    return touched, sorted(missing_classes)


def delete_existing_worksheet() -> None:
    worksheet = vs.GetObject(WORKSHEET_NAME)
    if worksheet and vs.GetType(worksheet) == 18:
        try:
            vs.DelObject(worksheet)
        except Exception:
            pass


def set_cell_text(worksheet: Any, row: int, column: int, value: str) -> None:
    vs.SetWSCellFormulaN(worksheet, row, column, row, column, value)


def create_cost_worksheet() -> None:
    delete_existing_worksheet()
    worksheet = vs.CreateWS(WORKSHEET_NAME, 2, 10)

    headers = [
        "Class",
        "Description",
        "Unit",
        "Measure Basis",
        "Quantity",
        "Area",
        "Length",
        "Count",
        "Unit Cost",
        "Total Cost",
    ]

    for idx, header in enumerate(headers, start=1):
        set_cell_text(worksheet, 1, idx, header)

    set_cell_text(worksheet, 2, 0, f"=DATABASE((R IN ['{RECORD_NAME}']))")
    set_cell_text(worksheet, 2, 1, "=C")
    set_cell_text(worksheet, 2, 2, f"='{RECORD_NAME}'.'Description'")
    set_cell_text(worksheet, 2, 3, f"='{RECORD_NAME}'.'Unit'")
    set_cell_text(worksheet, 2, 4, f"='{RECORD_NAME}'.'Measure Basis'")
    set_cell_text(worksheet, 2, 5, f"='{RECORD_NAME}'.'Quantity'")
    set_cell_text(worksheet, 2, 6, "=AREA")
    set_cell_text(worksheet, 2, 7, "=LENGTH")
    set_cell_text(worksheet, 2, 8, "=COUNT")
    set_cell_text(worksheet, 2, 9, f"='{RECORD_NAME}'.'Unit Cost'")
    set_cell_text(worksheet, 2, 10, f"='{RECORD_NAME}'.'Total Cost'")

    try:
        vs.SetWSCellNumberFormat(worksheet, 2, 5, 2, 8, 1, 3, "", "")
        vs.SetWSCellNumberFormat(worksheet, 2, 9, 2, 10, 2, 2, "$", "")
    except Exception:
        pass

    vs.RecalculateWS(worksheet)
    vs.ShowWS(worksheet, True)


def main() -> None:
    try:
        ensure_record_format()
        cost_map = load_cost_rows(CONFIG["xlsx_path"], CONFIG["sheet_name"])
        touched, missing_classes = attach_cost_records(cost_map)
        create_cost_worksheet()

        summary = [
            f"Loaded {len(cost_map)} cost rows.",
            f"Attached/updated {touched} objects with '{RECORD_NAME}'.",
            f"Created worksheet '{WORKSHEET_NAME}'.",
        ]
        if missing_classes:
            summary.append("Classes with no workbook match: " + ", ".join(missing_classes[:15]))
        alert("\n".join(summary))
    except Exception as exc:
        alert(f"Cost estimate build failed:\n{exc}")


if __name__ == "__main__":
    main()
