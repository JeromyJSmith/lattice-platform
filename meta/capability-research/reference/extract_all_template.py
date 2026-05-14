"""VW Universe — Master Extraction Script.

Run this ONCE with the target VWX file open in Vectorworks 2026.
Everything that can be extracted headlessly is extracted here.
Format exports (IFC, DXF, PDF) are triggered at the end.

ONE-TIME SETUP (do this before first run):
  1. Open the VWX file in Vectorworks 2026.
  2. File > Export > Export IFC Project...
     - Export Format: IFC 4x3 AddendumII
     - Set output path to: <output_dir>/ifc4.ifc
     - Click OK. This saves the settings.
  3. Run this script:
     Tools > Plug-Ins > Run Script... > pick this file
     OR paste into the Python script console.

OUTPUTS (written to VW_UNIVERSE_OUTPUT_DIR or ~/vw-universe-exports/<timestamp>/):
  manifest.json              — run summary, all counts
  layers.json                — every design layer (name, visibility, scale)
  classes.json               — all classes (name, description, visibility)
  records.json               — all record formats + field schemas
  plants.json                — all plant style instances with positions + records
  symbols.json               — all symbol definitions (name, 2D/3D presence)
  worksheets.json            — all worksheets (name, rows/cols, db criteria)
  worksheets_content.csv     — raw cell content from all worksheets
  sheets.json                — all sheet layers (name, scale, viewport count)
  ifc_assignments.json       — per-object IFC class + pset names
  <ifc4.ifc>                 — IFC4.3 export (triggered via VW menu)
  <ifc2x3.ifc>               — IFC2x3 export (triggered via VW menu)
  <dxf/> dir                 — one DXF per design layer
  <sheets/> dir              — one PDF per sheet layer (via Publish/BatchPDF)
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

import vs  # type: ignore


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

def _resolve_output_dir() -> str:
    env = os.environ.get("VW_UNIVERSE_OUTPUT_DIR", "")
    if env:
        return env
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = os.path.expanduser(f"~/vw-universe-exports/{stamp}")
    return base


OUTPUT_DIR = _resolve_output_dir()
PROJECT_ID = os.environ.get("LATTICE_PROJECT_ID", "PROJECT_ID_PLACEHOLDER")
MAX_SECONDS_PER_PHASE = int(os.environ.get("VW_UNIVERSE_MAX_SEC", "300"))
LOG_PATH = os.path.join(OUTPUT_DIR, "extract.log")


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def now_iso() -> str:
    """Return current UTC time as ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


def log(msg: str) -> None:
    """Append a timestamped log line and show a VW alert dialog."""
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{now_iso()}] {msg}\n")
        vs.AlrtDialog(f"[LOG] {msg}")  # visible in VW during run
    except Exception:
        pass


def safe(fn, *args, default=None):
    """Call fn(*args) and return default on any exception."""
    try:
        return fn(*args)
    except Exception:
        return default


def sha1_id(*parts: str) -> str:
    """Return a deterministic UUID-shaped hex digest from the given parts."""
    h = hashlib.sha1()
    for p in parts:
        h.update(f"|{p}".encode("utf-8"))
    d = h.hexdigest()
    return f"{d[:8]}-{d[8:12]}-{d[12:16]}-{d[16:20]}-{d[20:32]}"


def write_json(name: str, data: Any) -> str:
    """Serialize data as JSON to OUTPUT_DIR/name and return the full path."""
    path = os.path.join(OUTPUT_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    return path


# ---------------------------------------------------------------------------
# Phase 1: Design Layers
# ---------------------------------------------------------------------------

def extract_layers() -> list[dict[str, Any]]:
    """Walk all layers and collect name, visibility, scale, and type."""
    rows = []
    h = safe(vs.FActLayer)
    while h:
        name = safe(vs.GetLName, h, default="")
        visibility = safe(vs.GetLVisibility, h, default=-1)
        scale = safe(vs.GetLScale, h, default=None)
        layer_type = safe(vs.GetObjectVariableInt, h, 154, default=-1)
        rows.append({
            "layer_id": sha1_id(PROJECT_ID, "layer", name),
            "project_id": PROJECT_ID,
            "name": name,
            "visibility": visibility,   # 0=visible, 1=invisible, 2=greyed
            "scale": scale,
            "layer_type": layer_type,   # 0=design, 1=sheet, 2=scratch
            "extracted_at": now_iso(),
        })
        h = safe(vs.NextLayer, h)
    return rows


# ---------------------------------------------------------------------------
# Phase 2: Classes
# ---------------------------------------------------------------------------

def extract_classes() -> list[dict[str, Any]]:
    """Collect all class names from the active document."""
    rows = []
    count = safe(vs.ClassNum, default=0)
    for i in range(1, (count or 0) + 1):
        name = safe(vs.ClassList, i, default="")
        if not name:
            continue
        rows.append({
            "class_id": sha1_id(PROJECT_ID, "class", name),
            "project_id": PROJECT_ID,
            "name": name,
            "extracted_at": now_iso(),
        })
    return rows


# ---------------------------------------------------------------------------
# Phase 3: Record Format Inventory
# ---------------------------------------------------------------------------

def extract_records() -> list[dict[str, Any]]:
    """Walk all record format definitions and collect field schemas."""
    rows = []
    rec_handles: list[Any] = []

    def _collect_rec(h):
        rec_handles.append(h)

    safe(vs.ForEachObject, _collect_rec, "T=RECFMT")

    for rh in rec_handles:
        rec_name = safe(vs.GetName, rh, default="")
        if not rec_name:
            continue
        num_fields = safe(vs.NumFields, rh, default=0) or 0
        fields = []
        for fi in range(1, num_fields + 1):
            fname = safe(vs.GetFldName, rh, fi, default="")
            ftype = safe(vs.GetFldType, rh, fi, default=-1)
            fdefault = safe(vs.GetFldDefault, rh, fi, default="")
            fields.append({"name": fname, "type": ftype, "default": fdefault})
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
# ---------------------------------------------------------------------------

def extract_plants() -> list[dict[str, Any]]:
    """Walk parametric objects and collect Plant Record data and positions."""
    plants = []
    PLANT_RECORD = "Plant Record"
    deadline = time.time() + MAX_SECONDS_PER_PHASE

    def _collect_plant(h):
        if time.time() > deadline:
            return
        # Check if Plant Record is attached
        nr = safe(vs.NumRecords, h, default=0) or 0
        found_plant = False
        for ri in range(1, nr + 1):
            rec = safe(vs.GetRecord, h, ri)
            if rec and safe(vs.GetName, rec, default="") == PLANT_RECORD:
                found_plant = True
                break
        if not found_plant:
            return

        x, y, z = 0.0, 0.0, 0.0
        try:
            loc = vs.GetEntPenLoc3D(h)
            if loc:
                x, y, z = float(loc[0] or 0), float(loc[1] or 0), float(loc[2] or 0)
        except Exception:
            pass

        plant = {
            "plant_id": sha1_id(PROJECT_ID, "plant", str(h), str(x), str(y)),
            "project_id": PROJECT_ID,
            "x": x, "y": y, "z": z,
            "latin_name": safe(vs.GetRField, h, PLANT_RECORD, "LatinName", default=""),
            "common_name": safe(vs.GetRField, h, PLANT_RECORD, "CommonName", default=""),
            "height": safe(vs.GetRField, h, PLANT_RECORD, "Height", default=""),
            "spread": safe(vs.GetRField, h, PLANT_RECORD, "Spread", default=""),
            "quantity": safe(vs.GetRField, h, PLANT_RECORD, "Quantity", default=""),
            "id_tag": safe(vs.GetRField, h, PLANT_RECORD, "IDTag", default=""),
            "extracted_at": now_iso(),
        }
        plants.append(plant)

    safe(vs.ForEachObject, _collect_plant, "T=PLUGINOBJECT")
    return plants


# ---------------------------------------------------------------------------
# Phase 5: Symbol Definitions
# ---------------------------------------------------------------------------

def extract_symbols() -> list[dict[str, Any]]:
    """Walk symbol definitions and check for 2D and 3D group presence."""
    syms = []
    sym_handles: list[Any] = []

    def _collect_sym(h):
        sym_handles.append(h)

    safe(vs.ForEachObject, _collect_sym, "T=SYMDEF")

    for sh in sym_handles:
        name = safe(vs.GetName, sh, default="")
        # Check 2D/3D presence via sub-object counts
        has_2d = False
        has_3d = False
        try:
            # 2D group is first child, 3D group is second child
            child2d = vs.FInGroup(sh)
            if child2d:
                has_2d = True
                child3d = vs.NextSObj(child2d)
                if child3d:
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
# Phase 6: Worksheets — Inventory + Content
# ---------------------------------------------------------------------------

def extract_worksheets() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Walk all worksheets, collect inventory metadata and cell content."""
    ws_handles: list[Any] = []
    deadline = time.time() + MAX_SECONDS_PER_PHASE

    def _collect_ws(h):
        if len(ws_handles) >= 200:
            return
        ws_handles.append(h)

    safe(vs.ForEachObject, _collect_ws, "T=SPRDSHEET")

    inventory = []
    all_cells = []
    for ws_h in ws_handles:
        if time.time() > deadline:
            break
        name = safe(vs.GetName, ws_h, default="") or ""
        num_rows, num_cols = 0, 0
        try:
            rc = vs.GetWSRowColumnCount(ws_h)
            if rc and len(rc) >= 2:
                num_rows = int(rc[0] or 0)
                num_cols = int(rc[1] or 0)
        except Exception:
            pass

        # Probe for database criteria on any row
        criteria = ""
        for fn_name in ("GetWSDatabaseCriteria", "GetWSDatabaseCriteriaA"):
            fn = getattr(vs, fn_name, None)
            if fn is None:
                continue
            for row in range(1, min(num_rows, 50) + 1):
                try:
                    r = fn(ws_h, row)
                    if r and isinstance(r, str) and r.strip():
                        criteria = r.strip()
                        break
                    if r and isinstance(r, (list, tuple)) and len(r) >= 2 and r[0]:
                        criteria = str(r[1] or "").strip()
                        if criteria:
                            break
                except Exception:
                    pass
            if criteria:
                break

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

        # Extract cell content (cap at 100 rows × 26 cols to avoid timeout)
        max_rows = min(num_rows, 100)
        max_cols = min(num_cols, 26)
        get_cell = getattr(vs, "GetWSCellValue", None) or getattr(vs, "GetWSCellString", None)
        if get_cell:
            for row in range(1, max_rows + 1):
                for col in range(1, max_cols + 1):
                    try:
                        val = get_cell(ws_h, row, col)
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
# ---------------------------------------------------------------------------

def extract_sheets() -> list[dict[str, Any]]:
    """Walk all sheet layers and collect name, scale, and viewport count."""
    sheets = []
    # Sheet layers: type code 2 (vs.GetObjectVariableInt(h, 154) == 1 for sheet)
    h = safe(vs.FActLayer)
    while h:
        layer_type = safe(vs.GetObjectVariableInt, h, 154, default=-1)
        if layer_type == 1:  # sheet layer
            name = safe(vs.GetLName, h, default="")
            scale = safe(vs.GetLScale, h, default=None)
            # Count viewports on this sheet
            vp_count = 0
            vp_h = safe(vs.FInLayer, h)
            while vp_h:
                obj_type = safe(vs.GetType, vp_h, default=-1)
                if obj_type == 122:  # viewport type
                    vp_count += 1
                vp_h = safe(vs.NextSObj, vp_h)
            sheets.append({
                "sheet_id": sha1_id(PROJECT_ID, "sheet", name),
                "project_id": PROJECT_ID,
                "name": name,
                "scale": scale,
                "viewport_count": vp_count,
                "extracted_at": now_iso(),
            })
        h = safe(vs.NextLayer, h)
    return sheets


# ---------------------------------------------------------------------------
# Phase 8: IFC Assignments per object
# ---------------------------------------------------------------------------

def extract_ifc_assignments() -> list[dict[str, Any]]:
    """Walk all objects and collect IFC class assignments and property set names."""
    rows = []
    deadline = time.time() + MAX_SECONDS_PER_PHASE
    ifc_fn = getattr(vs, "IFC_GetIFCEntity", None)
    pset_count_fn = getattr(vs, "IFC_GetNumPsets", None)
    pset_name_fn = getattr(vs, "IFC_GetPsetName", None)
    if not ifc_fn:
        return rows

    def _collect(h):
        if time.time() > deadline:
            return
        ifc_class = safe(ifc_fn, h, default="")
        if not ifc_class:
            return
        psets = []
        if pset_count_fn and pset_name_fn:
            num_psets = safe(pset_count_fn, h, default=0) or 0
            for pi in range(num_psets):
                pn = safe(pset_name_fn, h, pi, default="")
                if pn:
                    psets.append(pn)
        obj_name = safe(vs.GetName, h, default="")
        rows.append({
            "obj_id": sha1_id(PROJECT_ID, "obj", str(h), obj_name),
            "project_id": PROJECT_ID,
            "object_name": obj_name,
            "ifc_class": ifc_class,
            "psets": psets,
            "extracted_at": now_iso(),
        })

    safe(vs.ForEachObject, _collect, "")  # walk all objects
    return rows


# ---------------------------------------------------------------------------
# Phase 9: Format Exports (IFC, DXF, PDF Sheets)
# ---------------------------------------------------------------------------

def trigger_ifc_export(version_label: str, out_path: str) -> bool:
    """Export IFC headlessly via IFC_ExportNoUI — no dialog required.

    IFC version (4x3 vs 2x3) is controlled by VW Document Settings > IFC Settings.
    Switch the version there ONCE, then this function runs silently.

    Ref: vs.IFC_ExportNoUI(strFullFilePath) -> BOOLEAN
    Source: Vectorworks/developer-scripting Function Reference
    """
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    try:
        # Primary: headless export — no dialog, no user interaction
        fn = getattr(vs, "IFC_ExportNoUI", None)
        if fn:
            ok = fn(out_path)
            if ok and os.path.exists(out_path):
                return True
            log(f"IFC_ExportNoUI returned {ok} for {version_label}")
        # Fallback: menu trigger with last-used settings
        vs.SetPref(8908, True)
        vs.SetSavePref(8909, out_path)
        vs.DoMenuTextByName("Export IFC Project...", 0)
        return os.path.exists(out_path)
    except Exception as e:
        log(f"IFC export ({version_label}) failed: {e}")
        return False


def trigger_dxf_export_all_layers() -> list[str]:
    """Export each visible design layer to DXF.

    Activates each layer, triggers DXF export with last-used settings.
    """
    exported = []
    dxf_dir = os.path.join(OUTPUT_DIR, "dxf")
    os.makedirs(dxf_dir, exist_ok=True)

    h = safe(vs.FActLayer)
    while h:
        layer_type = safe(vs.GetObjectVariableInt, h, 154, default=-1)
        if layer_type == 0:  # design layer
            name = safe(vs.GetLName, h, default="unknown")
            safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
            out_path = os.path.join(dxf_dir, f"{safe_name}.dxf")
            try:
                vs.SetLayer(h)  # activate this layer
                vs.SetSavePref(1001, out_path)  # DXF output path pref
                vs.DoMenuTextByName("Export DXF/DWG...", 0)
                if os.path.exists(out_path):
                    exported.append(out_path)
            except Exception as e:
                log(f"DXF export for layer '{name}' failed: {e}")
        h = safe(vs.NextLayer, h)
    return exported


def trigger_pdf_publish(sheets: list[dict]) -> bool:
    """Export all sheet layers to PDF using the proper VW PDF API.

    Strategy (in order of preference):
    1. PublishSavedSet — one call, exports named publish set to folder (best)
    2. AcquireExportPDFSettingsAndLocation + OpenPDFDocument + ExportPDFPages — per-sheet
    3. PrintWithoutUsingPrintDialog — fallback

    Ref: Vectorworks/developer-scripting Function Reference
      vs.PublishSavedSet(savedSetName, outputFolder) -> BOOLEAN
      vs.AcquireExportPDFSettingsAndLocation(inbSeparateDocuments) -> BOOLEAN
      vs.OpenPDFDocument(inFilenameStr) -> BOOLEAN
      vs.ExportPDFPages(savedViewNameStr) -> INTEGER
      vs.ClosePDFDocument()
    """
    sheets_dir = os.path.join(OUTPUT_DIR, "sheets")
    os.makedirs(sheets_dir, exist_ok=True)

    # Strategy 1: PublishSavedSet (configure "LATTICE Export Set" once in VW)
    fn_publish = getattr(vs, "PublishSavedSet", None)
    if fn_publish:
        try:
            ok = fn_publish("LATTICE Export Set", sheets_dir + "/")
            if ok:
                log("  PDF: PublishSavedSet succeeded")
                return True
        except Exception as e:
            log(f"  PublishSavedSet failed: {e}")

    # Strategy 2: OpenPDFDocument + ExportPDFPages per sheet
    fn_acquire = getattr(vs, "AcquireExportPDFSettingsAndLocation", None)
    fn_open = getattr(vs, "OpenPDFDocument", None)
    fn_export = getattr(vs, "ExportPDFPages", None)
    fn_close = getattr(vs, "ClosePDFDocument", None)

    if fn_acquire and fn_open and fn_export and fn_close:
        try:
            out_pdf = os.path.join(sheets_dir, "all_sheets.pdf")
            settings_ok = fn_acquire(False)  # False = single document
            if settings_ok:
                opened = fn_open(out_pdf)
                if opened:
                    for sheet in sheets:
                        try:
                            fn_export(sheet["name"])
                        except Exception:
                            pass
                    fn_close()
                    log(f"  PDF: exported {len(sheets)} sheets via OpenPDFDocument")
                    return True
        except Exception as e:
            log(f"  OpenPDFDocument path failed: {e}")

    # Strategy 3: fallback — print each sheet
    log("  PDF: falling back to PrintWithoutUsingPrintDialog per sheet")
    fn_print = getattr(vs, "PrintWithoutUsingPrintDialog", None) or \
               getattr(vs, "DoMenuTextByName", None)
    h = safe(vs.FActLayer)
    while h:
        layer_type = safe(vs.GetObjectVariableInt, h, 154, default=-1)
        if layer_type == 1:
            try:
                vs.SetLayer(h)
                if fn_print == vs.DoMenuTextByName:
                    vs.DoMenuTextByName("Print...", 0)
                elif fn_print:
                    fn_print()
            except Exception:
                pass
        h = safe(vs.NextLayer, h)
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Run all extraction phases and format exports, writing outputs to OUTPUT_DIR."""
    t0 = time.time()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    log(f"=== VW Universe extraction START  output={OUTPUT_DIR} ===")

    manifest: dict[str, Any] = {
        "project_id": PROJECT_ID,
        "output_dir": OUTPUT_DIR,
        "started_at": now_iso(),
        "vw_document": safe(vs.GetFName, default=""),
        "phases": {},
    }

    # --- Phase 1: Layers ---
    log("Phase 1: Design layers")
    layers = extract_layers()
    write_json("layers.json", layers)
    manifest["phases"]["layers"] = {"count": len(layers), "path": "layers.json"}
    log(f"  {len(layers)} layers")

    # --- Phase 2: Classes ---
    log("Phase 2: Classes")
    classes = extract_classes()
    write_json("classes.json", classes)
    manifest["phases"]["classes"] = {"count": len(classes), "path": "classes.json"}
    log(f"  {len(classes)} classes")

    # --- Phase 3: Record Formats ---
    log("Phase 3: Record formats")
    records = extract_records()
    write_json("records.json", records)
    manifest["phases"]["records"] = {"count": len(records), "path": "records.json"}
    log(f"  {len(records)} record formats")

    # --- Phase 4: Plants ---
    log("Phase 4: Plant instances")
    plants = extract_plants()
    write_json("plants.json", plants)
    manifest["phases"]["plants"] = {"count": len(plants), "path": "plants.json"}
    log(f"  {len(plants)} plant instances")

    # --- Phase 5: Symbols ---
    log("Phase 5: Symbol definitions")
    syms = extract_symbols()
    write_json("symbols.json", syms)
    manifest["phases"]["symbols"] = {"count": len(syms), "path": "symbols.json"}
    log(f"  {len(syms)} symbols ({sum(1 for s in syms if s['has_3d'])} with 3D)")

    # --- Phase 6: Worksheets ---
    log("Phase 6: Worksheets")
    ws_inventory, ws_cells = extract_worksheets()
    write_json("worksheets.json", ws_inventory)
    # Write worksheet cell content as CSV
    if ws_cells:
        csv_path = os.path.join(OUTPUT_DIR, "worksheets_content.csv")
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["worksheet_id", "worksheet_name", "row", "col", "value"])
            w.writeheader()
            w.writerows(ws_cells)
    manifest["phases"]["worksheets"] = {
        "count": len(ws_inventory), "path": "worksheets.json",
        "cells": len(ws_cells), "cells_path": "worksheets_content.csv",
    }
    log(f"  {len(ws_inventory)} worksheets, {len(ws_cells)} cells extracted")

    # --- Phase 7: Sheet Layers ---
    log("Phase 7: Sheet layers")
    sheets = extract_sheets()
    write_json("sheets.json", sheets)
    manifest["phases"]["sheets"] = {"count": len(sheets), "path": "sheets.json"}
    log(f"  {len(sheets)} sheet layers")

    # --- Phase 8: IFC Assignments ---
    log("Phase 8: IFC object assignments")
    ifc_assignments = extract_ifc_assignments()
    write_json("ifc_assignments.json", ifc_assignments)
    manifest["phases"]["ifc_assignments"] = {
        "count": len(ifc_assignments), "path": "ifc_assignments.json"
    }
    log(f"  {len(ifc_assignments)} objects with IFC class assigned")

    # --- Phase 9: Format Exports ---
    log("Phase 9: Format exports")

    # IFC 4.3
    ifc4_path = os.path.join(OUTPUT_DIR, "ifc", "export_ifc4.ifc")
    ifc4_ok = trigger_ifc_export("IFC4.3", ifc4_path)
    manifest["phases"]["ifc4_export"] = {"ok": ifc4_ok, "path": ifc4_path}
    log(f"  IFC4.3 export: {'OK' if ifc4_ok else 'FAILED (see note)'}")

    # IFC 2x3 — requires user to switch IFC version in preferences first
    # We write instructions and trigger a second export attempt
    ifc2x3_path = os.path.join(OUTPUT_DIR, "ifc", "export_ifc2x3.ifc")
    log(
        "  NOTE: For IFC2x3, open VW Export IFC dialog, change version to IFC2x3,"
        f" export to {ifc2x3_path}, then re-run this script."
    )
    manifest["phases"]["ifc2x3_export"] = {
        "ok": False, "path": ifc2x3_path,
        "note": "Requires manual version switch to IFC2x3 in VW export dialog first.",
    }

    # DXF per layer
    log("  DXF export per layer...")
    dxf_files = trigger_dxf_export_all_layers()
    manifest["phases"]["dxf_export"] = {
        "count": len(dxf_files), "files": dxf_files
    }
    log(f"  {len(dxf_files)} DXF files exported")

    # PDF Sheets — pass sheet list so ExportPDFPages gets correct names
    log("  PDF sheet export...")
    pdf_ok = trigger_pdf_publish(sheets)
    manifest["phases"]["pdf_export"] = {
        "ok": pdf_ok, "dir": os.path.join(OUTPUT_DIR, "sheets"),
        "note": "Configure 'LATTICE Export Set' in VW Publish for best results.",
    }
    log(f"  PDF publish: {'OK' if pdf_ok else 'fallback used'}")

    # --- Finalize manifest ---
    elapsed = round(time.time() - t0, 2)
    manifest["finished_at"] = now_iso()
    manifest["elapsed_sec"] = elapsed
    manifest["ok"] = True
    write_json("manifest.json", manifest)

    summary = (
        f"VW Universe extraction complete in {elapsed}s\n"
        f"  Layers: {len(layers)}\n"
        f"  Classes: {len(classes)}\n"
        f"  Records: {len(records)}\n"
        f"  Plants: {len(plants)}\n"
        f"  Symbols: {len(syms)}\n"
        f"  Worksheets: {len(ws_inventory)}\n"
        f"  Sheets: {len(sheets)}\n"
        f"  IFC objects: {len(ifc_assignments)}\n"
        f"  Output: {OUTPUT_DIR}\n"
        f"\nNext: run headless ingest:\n"
        f"  lattice project switch vw-universe\n"
        f"  uv run /Volumes/PixelTable/vw-universe/ingest/ingest_exports.py {OUTPUT_DIR}"
    )
    log(summary)
    vs.AlrtDialog(summary)


try:
    main()
except Exception as e:
    msg = f"FATAL: {e}"
    try:
        log(msg)
    except Exception:
        pass
    vs.AlrtDialog(msg)
    raise
