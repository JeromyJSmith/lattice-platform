"""Export all Vectorworks classes from the active document.

Run inside Vectorworks 2026 with the target file open.

Outputs:
- a worksheet named `All Classes List`
- a CSV on the Desktop named `vw_classes_export.csv`
"""

from __future__ import annotations

import csv
import os

import vs  # type: ignore


WORKSHEET_NAME = "All Classes List"
CSV_NAME = "vw_classes_export.csv"


def get_classes() -> list[str]:
    classes: list[str] = []
    count = vs.ClassNum()
    for index in range(1, count + 1):
        name = vs.ClassList(index)
        if name:
            classes.append(name)
    classes.sort(key=str.lower)
    return classes


def rebuild_worksheet(classes: list[str]) -> None:
    existing = vs.GetObject(WORKSHEET_NAME)
    if existing and vs.GetType(existing) == 18:
        try:
            vs.DelObject(existing)
        except Exception:
            pass

    ws = vs.CreateWS(WORKSHEET_NAME, max(len(classes) + 1, 2), 1)
    vs.SetWSCellFormulaN(ws, 1, 1, 1, 1, "Class Name")
    for row, class_name in enumerate(classes, start=2):
        vs.SetWSCellFormulaN(ws, row, 1, row, 1, class_name)
    vs.ShowWS(ws, True)


def export_csv(classes: list[str]) -> str:
    desktop = os.path.expanduser("~/Desktop")
    path = os.path.join(desktop, CSV_NAME)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Class Name"])
        for class_name in classes:
            writer.writerow([class_name])
    return path


def main() -> None:
    classes = get_classes()
    rebuild_worksheet(classes)
    csv_path = export_csv(classes)
    vs.AlrtDialog(
        f"Exported {len(classes)} classes.\n\n"
        f"Worksheet: {WORKSHEET_NAME}\n"
        f"CSV: {csv_path}"
    )


if __name__ == "__main__":
    main()
