"""VW Universe — Master Extraction Script (Python 3.9.2, VW 2026)

Run this with the target VWX file already open in Vectorworks 2026.
The file must have been opened at least once after migration (dismiss migration
dialogs manually, save once, then run this script).

Execution paths:
  1. vwx-mcp execute_script tool (primary — from LATTICE via TCP :9878)
  2. VW Script Editor: Tools > Plug-Ins > Run Script... > pick this file
  3. VW Python console: paste or import

Pre-flight (one-time per document):
  - Open VW Document Preferences > IFC Settings > set schema to IFC4X3
  - Save the document once after migration dialogs are dismissed
  - (Optional) Configure a Publish Set named "LATTICE Export Set" for PDF sheets

Outputs (written next to the VWX file in extract_output/<timestamp>/):
  manifest.json           — run summary, phase counts, elapsed time
  layers.json             — all design layers (name, type, scale, visibility)
  classes.json            — all classes (name, visibility)
  records.json            — all record format definitions + field schemas
  plants.json             — all plant instances (position + parametric record fields)
  symbols.json            — all symbol definitions (name, has_2d, has_3d)
  worksheets.json         — worksheet inventory (name, row/col counts, db_criteria)
  worksheets_content.csv  — raw cell content (capped: 100 rows x 26 cols per sheet)
  sheets.json             — all sheet layers (name, scale, viewport count)
  ifc_assignments.json    — per-object IFC class + pset names
  ifc/export_ifc4x3.ifc   — IFC 4X3 export (requires IFC scheme set in Doc Prefs)
  dxf/<layer>.dxf         — one DXF per design layer
  sheets/<name>.pdf       — sheet PDFs via Publish Set (if configured)

Architecture note:
  This script runs inside VW's Python 3.9.2 interpreter. After it completes,
  the LATTICE sidecar (Python 3.12, uv) picks up the output directory and
  processes it with IfcOpenShell + ezdxf into Pixeltable.

Research basis: meta/capability-research/census/vw-scripting-extraction-research/SYNTHESIS.md
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import vs  # type: ignore — only resolves inside Vectorworks Python interpreter


# ---------------------------------------------------------------------------
# SYNTHESIS-confirmed: VW 2026 null handle identity
# ---------------------------------------------------------------------------

def is_null(h: Any) -> bool:
    """Return True if h is a VW null handle. NEVER use `is None` for handles."""
    try:
        return h == vs.Handle(0)
    except Exception:
        return True


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

def _output_dir() -> Path:
    """Return the output directory, adjacent to the open document."""
    env = os.environ.get("VW_UNIVERSE_OUTPUT_DIR", "")
    if env:
        return Path(env)
    # SYNTHESIS BQ-01: POSIX since VW 2019 — pathlib.Path() is correct raw
    doc_path = Path(vs.GetFPathName())
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return doc_path.parent / "extract_output" / stamp


PROJECT_ID: str = os.environ.get("LATTICE_PROJECT_ID", "unknown")
MAX_SEC_PER_PHASE: int = int(os.environ.get("VW_EXTRACT_MAX_SEC", "300"))

OUTPUT_DIR: Path = _output_dir()
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

LOG_PATH: Path = OUTPUT_DIR / "extract.log"

VW_EPOCH = datetime(1904, 1, 1)  # VW internal timestamp epoch


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(msg: str) -> None:
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{now_iso()}] {msg}\n")
    except Exception:
        pass
    try:
        vs.AlrtDialog(str(msg)[:500])
    except Exception:
        pass


def safe(fn: Any, *args: Any, default: Any = None) -> Any:
    try:
        return fn(*args)
    except Exception:
        return default


def sha1_id(*parts: str) -> str:
    h = hashlib.sha1()
    for p in parts:
        h.update(f"|{p}".encode("utf-8"))
    d = h.hexdigest()
    return f"{d[:8]}-{d[8:12]}-{d[12:16]}-{d[16:20]}-{d[20:32]}"


def write_json(name: str, data: Any) -> Path:
    path = OUTPUT_DIR / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    return path


def vw_ts(seconds: float) -> str:
    try:
        return (VW_EPOCH + __import__("datetime").timedelta(seconds=float(seconds))).isoformat()
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Phase 1: Design Layers
# SYNTHESIS BQ-01 (POSIX), BQ-08 (Python 3.9.2)
# Bug fixed: FActLayer → FLayer (FActLayer returns only the active layer)
# Bug fixed: while h → while not is_null(h)
# ---------------------------------------------------------------------------

def extract_layers() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    # FLayer() = first layer in document; FActLayer() = currently active layer only
    h = safe(vs.FLayer)
    while h and not is_null(h):
        name = safe(vs.GetLName, h, default="")
        rows.append({
            "layer_id": sha1_id(PROJECT_ID, "layer", name),
            "project_id": PROJECT_ID,
            "name": name,
            "visibility": safe(vs.GetLVisibility, h, default=-1),
            "scale": safe(vs.GetLScale, h, default=None),
            "layer_type": safe(vs.GetObjectVariableInt, h, 154, default=-1),
            "extracted_at": now_iso(),
        })
        h = safe(vs.NextLayer, h)
    return rows


# ---------------------------------------------------------------------------
# Phase 2: Classes
# ---------------------------------------------------------------------------

def extract_classes() -> list[dict[str, Any]]:
    count = safe(vs.ClassNum, default=0) or 0
    rows = []
    for i in range(1, count + 1):
        name = safe(vs.ClassList, i, default="") or ""
        if not name:
            continue
        rows.append({
            "class_id": sha1_id(PROJECT_ID, "class", name),
            "project_id": PROJECT_ID,
            "name": name,
            "visibility": safe(vs.GetClassVisibility, name, default=-1),
            "extracted_at": now_iso(),
        })
    return rows


# ---------------------------------------------------------------------------
# Phase 3: Record Format Inventory
# SYNTHESIS BQ-04: one-call pattern — collect handles, then process outside
# ---------------------------------------------------------------------------

def extract_records() -> list[dict[str, Any]]:
    rec_handles: list[Any] = []
    vs.ForEachObject(lambda h: rec_handles.append(h), "T=RECFMT")

    rows = []
    for rh in rec_handles:
        rec_name = safe(vs.GetName, rh, default="") or ""
        if not rec_name:
            continue
        num_fields = safe(vs.NumFields, rh, default=0) or 0
        fields = []
        for fi in range(1, num_fields + 1):
            fields.append({
                "name": safe(vs.GetFldName, rh, fi, default=""),
                "type": safe(vs.GetFldType, rh, fi, default=-1),
                "default": safe(vs.GetFldDefault, rh, fi, default=""),
            })
        rows.append({
            "record_id": sha1_id(PROJECT_ID, "record", rec_name),
            "project_id": PROJECT_ID,
            "name": rec_name,
            "field_count": num_fields,
            "fields": fields,
            "extracted_at": now_iso(),
        })
    return rows


# ---------------------------------------------------------------------------
# Phase 4: Plant Style Instances
# SYNTHESIS BQ-04: one-call collect, process outside
# SYNTHESIS (Agent C): GetParametricRecord for parametric objects
# Bug fixed: heavy processing inside callback → collect first, process outside
# ---------------------------------------------------------------------------

def extract_plants() -> list[dict[str, Any]]:
    deadline = time.time() + MAX_SEC_PER_PHASE

    # Collect all plugin object handles first (one-call pattern)
    plugin_handles: list[Any] = []
    vs.ForEachObject(lambda h: plugin_handles.append(h), "T=PLUGINOBJECT")

    plants = []
    PLANT_RECORD = "Plant Record"

    for h in plugin_handles:
        if time.time() > deadline:
            log("  Plants: deadline reached, stopping early")
            break

        # Check for Plant Record attachment via parametric record
        rec_h = safe(vs.GetParametricRecord, h)
        if is_null(rec_h):
            # Also check attached records (non-parametric)
            found = False
            num_recs = safe(vs.NumRecords, h, default=0) or 0
            for ri in range(1, num_recs + 1):
                rec = safe(vs.GetRecord, h, ri)
                if not is_null(rec) and safe(vs.GetName, rec, default="") == PLANT_RECORD:
                    found = True
                    break
            if not found:
                continue
            rec_name = PLANT_RECORD
        else:
            rec_name = safe(vs.GetName, rec_h, default="") or ""
            if PLANT_RECORD not in rec_name:
                continue

        x, y = 0.0, 0.0
        try:
            cx, cy = vs.HCenter(h)
            x, y = float(cx or 0), float(cy or 0)
        except Exception:
            pass

        plant: dict[str, Any] = {
            "plant_id": sha1_id(PROJECT_ID, "plant", str(h), str(x), str(y)),
            "project_id": PROJECT_ID,
            "x": x,
            "y": y,
            "layer": safe(vs.GetLName, safe(vs.GetLayer, h), default=""),
            "latin_name":   safe(vs.GetRField, h, PLANT_RECORD, "LatinName", default=""),
            "common_name":  safe(vs.GetRField, h, PLANT_RECORD, "CommonName", default=""),
            "height":       safe(vs.GetRField, h, PLANT_RECORD, "Height", default=""),
            "spread":       safe(vs.GetRField, h, PLANT_RECORD, "Spread", default=""),
            "quantity":     safe(vs.GetRField, h, PLANT_RECORD, "Quantity", default=""),
            "id_tag":       safe(vs.GetRField, h, PLANT_RECORD, "IDTag", default=""),
            "extracted_at": now_iso(),
        }
        plants.append(plant)

    return plants


# ---------------------------------------------------------------------------
# Phase 5: Symbol Definitions
# SYNTHESIS BQ-04: collect first, traverse outside
# SYNTHESIS (Agent C): FIn3D/NextObj for nested traversal
# ---------------------------------------------------------------------------

def extract_symbols() -> list[dict[str, Any]]:
    sym_handles: list[Any] = []
    vs.ForEachObject(lambda h: sym_handles.append(h), "T=SYMDEF")

    syms = []
    for sh in sym_handles:
        name = safe(vs.GetName, sh, default="") or ""
        has_2d, has_3d = False, False
        try:
            child_2d = vs.FIn3D(sh)
            if not is_null(child_2d):
                has_2d = True
                child_3d = vs.NextObj(child_2d)
                if not is_null(child_3d):
                    has_3d = True
        except Exception:
            pass
        syms.append({
            "symbol_id": sha1_id(PROJECT_ID, "symbol", name),
            "project_id": PROJECT_ID,
            "name": name,
            "has_2d": has_2d,
            "has_3d": has_3d,
            "extracted_at": now_iso(),
        })
    return syms


# ---------------------------------------------------------------------------
# Phase 6: Worksheets — Inventory + Cell Content
# SYNTHESIS BQ-09: Type 56 (canvas image) → GetWSFromImage → Type 18 (resource)
# Bug fixed: T=SPRDSHEET → T=WORKSHEET (correct VW criteria)
# Bug fixed: direct GetWSCellValue on image handle → GetWSFromImage first
# Bug fixed: GetWSCellValue → GetWSCellString (correct for string extraction)
# ---------------------------------------------------------------------------

def extract_worksheets() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    deadline = time.time() + MAX_SEC_PER_PHASE

    # Collect canvas worksheet images (Type 56)
    ws_images: list[Any] = []
    vs.ForEachObject(lambda h: ws_images.append(h), "T=WORKSHEET")

    inventory: list[dict[str, Any]] = []
    all_cells: list[dict[str, Any]] = []

    for img in ws_images:
        if time.time() > deadline:
            log("  Worksheets: deadline reached, stopping early")
            break

        # CRITICAL: convert Type 56 (canvas image) → Type 18 (resource)
        hWS = safe(vs.GetWSFromImage, img)
        if is_null(hWS):
            continue

        vs.RefreshWorksheet(hWS)

        name = safe(vs.GetName, img, default="") or ""
        num_rows, num_cols = 0, 0
        try:
            rc = vs.GetWSRowColumnCount(hWS)
            if rc and len(rc) >= 2:
                num_rows = int(rc[0] or 0)
                num_cols = int(rc[1] or 0)
        except Exception:
            pass

        # Probe for database criteria
        criteria = ""
        for row in range(1, min(num_rows, 20) + 1):
            fn = getattr(vs, "GetWSDatabaseCriteria", None)
            if fn is None:
                break
            try:
                r = fn(hWS, row)
                if r and isinstance(r, str) and r.strip():
                    criteria = r.strip()
                    break
                if r and isinstance(r, (list, tuple)) and len(r) >= 2 and r[0]:
                    criteria = str(r[1] or "").strip()
                    if criteria:
                        break
            except Exception:
                pass

        ws_id = sha1_id(PROJECT_ID, "worksheet", name)
        inventory.append({
            "worksheet_id": ws_id,
            "project_id": PROJECT_ID,
            "name": name,
            "row_count": num_rows,
            "col_count": num_cols,
            "db_criteria": criteria,
            "extracted_at": now_iso(),
        })

        # Extract cell content — capped to avoid timeout
        max_rows = min(num_rows, 100)
        max_cols = min(num_cols, 26)
        for row in range(1, max_rows + 1):
            for col in range(1, max_cols + 1):
                try:
                    # GetWSCellString works on Type 18 handle; returns string always
                    val = vs.GetWSCellString(hWS, row, col)
                except Exception:
                    val = ""
                if val:
                    all_cells.append({
                        "worksheet_id": ws_id,
                        "worksheet_name": name,
                        "row": row,
                        "col": col,
                        "value": str(val),
                    })

    return inventory, all_cells


# ---------------------------------------------------------------------------
# Phase 7: Sheet Layers
# Bug fixed: while h → while not is_null(h)
# Bug fixed: FActLayer → FLayer
# ---------------------------------------------------------------------------

def extract_sheets() -> list[dict[str, Any]]:
    sheets = []
    h = safe(vs.FLayer)
    while h and not is_null(h):
        layer_type = safe(vs.GetObjectVariableInt, h, 154, default=-1)
        if layer_type == 1:  # sheet layer
            name = safe(vs.GetLName, h, default="") or ""
            vp_count = 0
            vp_h = safe(vs.FInLayer, h)
            while vp_h and not is_null(vp_h):
                if safe(vs.GetType, vp_h, default=-1) == 122:  # viewport
                    vp_count += 1
                vp_h = safe(vs.NextSObj, vp_h)
            sheets.append({
                "sheet_id": sha1_id(PROJECT_ID, "sheet", name),
                "project_id": PROJECT_ID,
                "name": name,
                "scale": safe(vs.GetLScale, h, default=None),
                "viewport_count": vp_count,
                "extracted_at": now_iso(),
            })
        h = safe(vs.NextLayer, h)
    return sheets


# ---------------------------------------------------------------------------
# Phase 8: IFC Assignments
# SYNTHESIS BQ-04: collect handles first, process outside
# Bug fixed: heavy processing inside callback → collect first
# ---------------------------------------------------------------------------

def extract_ifc_assignments() -> list[dict[str, Any]]:
    deadline = time.time() + MAX_SEC_PER_PHASE

    ifc_entity_fn = getattr(vs, "IFC_GetIFCEntity", None)
    if not ifc_entity_fn:
        return []

    # Collect all object handles first (one-call pattern)
    all_handles: list[Any] = []
    vs.ForEachObject(lambda h: all_handles.append(h), "")

    rows = []
    pset_count_fn = getattr(vs, "IFC_GetNumPsets", None)
    pset_name_fn = getattr(vs, "IFC_GetPsetName", None)

    for h in all_handles:
        if time.time() > deadline:
            log("  IFC assignments: deadline reached")
            break
        ifc_class = safe(ifc_entity_fn, h, default="") or ""
        if not ifc_class:
            continue
        psets: list[str] = []
        if pset_count_fn and pset_name_fn:
            num_psets = safe(pset_count_fn, h, default=0) or 0
            for pi in range(num_psets):
                pn = safe(pset_name_fn, h, pi, default="") or ""
                if pn:
                    psets.append(pn)
        obj_name = safe(vs.GetName, h, default="") or ""
        rows.append({
            "obj_id": sha1_id(PROJECT_ID, "obj", str(h), obj_name),
            "project_id": PROJECT_ID,
            "object_name": obj_name,
            "ifc_class": ifc_class,
            "psets": psets,
            "extracted_at": now_iso(),
        })
    return rows


# ---------------------------------------------------------------------------
# Phase 9A: IFC Export
# SYNTHESIS BQ-10: SaveActiveDocument required before IFC_ExportNoUI
# SYNTHESIS BQ-02: strip preference numbers 8908/8909 — UNVERIFIED
# SYNTHESIS (Agent A): verify IFC_GetIFCScheme() == "IFC4X3" first
# ---------------------------------------------------------------------------

def export_ifc(out_path: str) -> bool:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    # Verify IFC scheme before export
    scheme = safe(vs.IFC_GetIFCScheme, default="") or ""
    if scheme and scheme != "IFC4X3":
        log(f"  IFC export: scheme is '{scheme}', expected IFC4X3. "
            f"Set it in Document Preferences > IFC Settings, then re-run.")
        return False

    # Pre-save required (SYNTHESIS BQ-10)
    vs.SaveActiveDocument()

    fn = getattr(vs, "IFC_ExportNoUI", None)
    if not fn:
        log("  IFC export: IFC_ExportNoUI not available in this VW version")
        return False

    try:
        ok = fn(out_path)
    except Exception as e:
        log(f"  IFC export exception: {e}")
        return False

    exists = os.path.exists(out_path) and os.path.getsize(out_path) > 0
    if not exists:
        log(f"  IFC export: IFC_ExportNoUI returned {ok} but file is missing/empty")
    return exists


# ---------------------------------------------------------------------------
# Phase 9B: DXF Export
# Bug fixed: removed SetSavePref(1001, ...) — unverified preference number
# Uses vs.ExportDXFDWG() directly (confirmed API from VW function reference)
# ---------------------------------------------------------------------------

def export_dxf_all_layers() -> list[str]:
    dxf_dir = OUTPUT_DIR / "dxf"
    dxf_dir.mkdir(parents=True, exist_ok=True)
    exported = []

    fn = getattr(vs, "ExportDXFDWG", None)
    if not fn:
        log("  DXF export: ExportDXFDWG not available")
        return []

    h = safe(vs.FLayer)
    while h and not is_null(h):
        if safe(vs.GetObjectVariableInt, h, 154, default=-1) == 0:  # design layer
            name = safe(vs.GetLName, h, default="") or "unknown"
            safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
            out_path = str(dxf_dir / f"{safe_name}.dxf")
            try:
                vs.SetLayer(h)
                # ExportDXFDWG(path, format, version, export_all_layers)
                # format: 1=DXF, 0=DWG; version: 0=latest AutoCAD
                fn(out_path, 1, 0, False)
                if os.path.exists(out_path):
                    exported.append(out_path)
            except Exception as e:
                log(f"  DXF layer '{name}' failed: {e}")
        h = safe(vs.NextLayer, h)
    return exported


# ---------------------------------------------------------------------------
# Phase 9C: PDF Export via Publish Set
# SYNTHESIS BQ-03: headless PDF impossible — use pre-embedded Publish Set
# Tries three strategies in order; gracefully skips if none work
# ---------------------------------------------------------------------------

def export_pdf_sheets(sheets: list[dict[str, Any]]) -> bool:
    sheets_dir = OUTPUT_DIR / "sheets"
    sheets_dir.mkdir(parents=True, exist_ok=True)

    # Strategy 1: PublishSavedSet (best — requires "LATTICE Export Set" configured in VW)
    fn_publish = getattr(vs, "PublishSavedSet", None)
    if fn_publish:
        try:
            ok = fn_publish("LATTICE Export Set", str(sheets_dir) + "/")
            if ok:
                log("  PDF: PublishSavedSet succeeded")
                return True
        except Exception as e:
            log(f"  PDF: PublishSavedSet failed: {e}")

    # Strategy 2: OpenPDFDocument + ExportPDFPages per sheet
    fn_acquire = getattr(vs, "AcquireExportPDFSettingsAndLocation", None)
    fn_open = getattr(vs, "OpenPDFDocument", None)
    fn_export = getattr(vs, "ExportPDFPages", None)
    fn_close = getattr(vs, "ClosePDFDocument", None)

    if all(f is not None for f in (fn_acquire, fn_open, fn_export, fn_close)):
        try:
            out_pdf = str(sheets_dir / "all_sheets.pdf")
            if fn_acquire(False):
                if fn_open(out_pdf):
                    for sheet in sheets:
                        try:
                            fn_export(sheet["name"])
                        except Exception:
                            pass
                    fn_close()
                    log(f"  PDF: exported {len(sheets)} sheets via OpenPDFDocument")
                    return True
        except Exception as e:
            log(f"  PDF: OpenPDFDocument path failed: {e}")

    # Strategy 3: DoMenuTextByName per sheet — shows dialog, non-silent
    log("  PDF: no silent path available. "
        "Configure 'LATTICE Export Set' in VW Publish for automated PDF export.")
    return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    t0 = time.time()
    log(f"=== VW extraction START  project={PROJECT_ID}  output={OUTPUT_DIR} ===")

    doc_name = safe(vs.GetFName, default="") or ""

    manifest: dict[str, Any] = {
        "project_id": PROJECT_ID,
        "output_dir": str(OUTPUT_DIR),
        "started_at": now_iso(),
        "vw_document": doc_name,
        "python_version": __import__("sys").version,
        "phases": {},
    }

    def run_phase(label: str, fn: Any, *args: Any) -> Any:
        log(f"Phase: {label}")
        t = time.time()
        result = fn(*args)
        elapsed = round(time.time() - t, 2)
        log(f"  {label}: done in {elapsed}s")
        return result

    # --- Data extraction phases ---
    layers = run_phase("Design layers", extract_layers)
    write_json("layers.json", layers)
    manifest["phases"]["layers"] = {"count": len(layers), "path": "layers.json"}

    classes = run_phase("Classes", extract_classes)
    write_json("classes.json", classes)
    manifest["phases"]["classes"] = {"count": len(classes), "path": "classes.json"}

    records = run_phase("Record formats", extract_records)
    write_json("records.json", records)
    manifest["phases"]["records"] = {"count": len(records), "path": "records.json"}

    plants = run_phase("Plant instances", extract_plants)
    write_json("plants.json", plants)
    manifest["phases"]["plants"] = {"count": len(plants), "path": "plants.json"}

    syms = run_phase("Symbol definitions", extract_symbols)
    write_json("symbols.json", syms)
    manifest["phases"]["symbols"] = {"count": len(syms), "path": "symbols.json"}

    ws_inv, ws_cells = run_phase("Worksheets", extract_worksheets)
    write_json("worksheets.json", ws_inv)
    if ws_cells:
        csv_path = OUTPUT_DIR / "worksheets_content.csv"
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(
                f, fieldnames=["worksheet_id", "worksheet_name", "row", "col", "value"]
            )
            w.writeheader()
            w.writerows(ws_cells)
    manifest["phases"]["worksheets"] = {
        "count": len(ws_inv), "path": "worksheets.json",
        "cells": len(ws_cells), "cells_path": "worksheets_content.csv",
    }

    sheets = run_phase("Sheet layers", extract_sheets)
    write_json("sheets.json", sheets)
    manifest["phases"]["sheets"] = {"count": len(sheets), "path": "sheets.json"}

    ifc_assignments = run_phase("IFC assignments", extract_ifc_assignments)
    write_json("ifc_assignments.json", ifc_assignments)
    manifest["phases"]["ifc_assignments"] = {
        "count": len(ifc_assignments), "path": "ifc_assignments.json"
    }

    # --- Format export phases ---
    log("Phase: IFC 4X3 export")
    ifc_path = str(OUTPUT_DIR / "ifc" / "export_ifc4x3.ifc")
    ifc_ok = export_ifc(ifc_path)
    manifest["phases"]["ifc_export"] = {
        "ok": ifc_ok, "path": ifc_path,
        "note": "" if ifc_ok else "Check IFC scheme in Doc Prefs > IFC Settings (must be IFC4X3)",
    }

    log("Phase: DXF export per layer")
    dxf_files = export_dxf_all_layers()
    manifest["phases"]["dxf_export"] = {"count": len(dxf_files), "files": dxf_files}

    log("Phase: PDF sheet export")
    pdf_ok = export_pdf_sheets(sheets)
    manifest["phases"]["pdf_export"] = {
        "ok": pdf_ok,
        "dir": str(OUTPUT_DIR / "sheets"),
        "note": "Configure 'LATTICE Export Set' in VW Publish for automated PDF.",
    }

    # --- Finalize ---
    elapsed = round(time.time() - t0, 2)
    manifest.update({"finished_at": now_iso(), "elapsed_sec": elapsed, "ok": True})
    write_json("manifest.json", manifest)

    summary = (
        f"VW extraction complete in {elapsed}s\n"
        f"  Document: {doc_name}\n"
        f"  Layers: {len(layers)}  Classes: {len(classes)}\n"
        f"  Records: {len(records)}  Plants: {len(plants)}\n"
        f"  Symbols: {len(syms)}  Worksheets: {len(ws_inv)}\n"
        f"  Sheets: {len(sheets)}  IFC objects: {len(ifc_assignments)}\n"
        f"  IFC export: {'OK' if ifc_ok else 'FAILED'}\n"
        f"  DXF files: {len(dxf_files)}\n"
        f"  Output: {OUTPUT_DIR}\n"
        f"\nNext (LATTICE sidecar):\n"
        f"  uv run pixeltable/service/ingest/ingest_exports.py {OUTPUT_DIR}"
    )
    log(summary)
    vs.AlrtDialog(summary)


try:
    main()
except Exception as _exc:
    _msg = f"FATAL: {_exc}"
    try:
        log(_msg)
    except Exception:
        pass
    try:
        vs.AlrtDialog(_msg[:500])
    except Exception:
        pass
    raise
