"""LATTICE sidecar ingest — processes extract_all.py output directory.

Runs OUTSIDE Vectorworks in the LATTICE Python 3.12 sidecar (uv).
Consumes the output directory written by vw-plugin/scripts/extract_all.py
and upserts all data into Pixeltable.

Usage:
    uv run pixeltable/service/ingest/ingest_exports.py <output_dir>

    or from the LATTICE sidecar worker:
    from pixeltable.service.ingest.ingest_exports import ingest_all
    ingest_all(output_dir, project_id)

Architecture:
    VW 2026 (GUI)
      └─ extract_all.py (Python 3.9.2, inside VW)
           └─ writes: layers.json, plants.json, worksheets.csv,
                      ifc/export_ifc4x3.ifc, dxf/*.dxf, manifest.json
    LATTICE sidecar (Python 3.12, this file)
      └─ reads output dir
      └─ IfcOpenShell → parses IFC
      └─ ezdxf → parses DXF
      └─ pixeltable → upserts into lattice/bridge/*
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import pixeltable as pxt


# ---------------------------------------------------------------------------
# Table accessors — all writes go through Pixeltable
# ---------------------------------------------------------------------------

def _get_table(name: str) -> pxt.Table:
    return pxt.get_table(name)


# ---------------------------------------------------------------------------
# Ingest: layers, classes, records, plants, symbols, sheets
# ---------------------------------------------------------------------------

def _ingest_layers(output_dir: Path, project_id: str) -> int:
    data = _load_json(output_dir / "layers.json")
    if not data:
        return 0
    t = _get_table("lattice/bridge/ifc_elements")
    rows = [
        {
            "project_id": project_id,
            "source_element_id": row["layer_id"],
            "ifc_class": "IfcBuildingStorey",
            "bis_class": "SpatialLocation",
            "bis_subclass": "Layer",
            "user_label": row.get("name", ""),
            "property_sets": {
                "VW_Layer": {
                    "scale": row.get("scale"),
                    "visibility": row.get("visibility"),
                    "layer_type": row.get("layer_type"),
                }
            },
        }
        for row in data
    ]
    t.insert(rows)
    return len(rows)


def _ingest_plants(output_dir: Path, project_id: str) -> int:
    data = _load_json(output_dir / "plants.json")
    if not data:
        return 0
    t = _get_table("lattice/bridge/ifc_elements")
    rows = []
    for p in data:
        x = p.get("x", 0.0)
        y = p.get("y", 0.0)
        rows.append({
            "project_id": project_id,
            "source_element_id": p["plant_id"],
            "ifc_class": "IfcPlant",
            "bis_class": "Landscape",
            "bis_subclass": "Landscape:PlantElement",
            "user_label": p.get("common_name") or p.get("latin_name") or "",
            "geometry_wkt": f"POINT({x} {y})",
            "property_sets": {
                "VW_Plant": {
                    k: v for k, v in p.items()
                    if k not in ("plant_id", "project_id", "x", "y", "extracted_at")
                }
            },
        })
    t.insert(rows)
    return len(rows)


def _ingest_ifc(output_dir: Path, project_id: str) -> int:
    ifc_path = output_dir / "ifc" / "export_ifc4x3.ifc"
    if not ifc_path.exists():
        print(f"  IFC: {ifc_path} not found — skipping")
        return 0

    try:
        import ifcopenshell
        import ifcopenshell.util.element
        import ifcopenshell.util.placement
    except ImportError:
        print("  IFC: ifcopenshell not installed — run: uv add ifcopenshell")
        return 0

    model = ifcopenshell.open(str(ifc_path))
    if model.schema not in ("IFC4X3", "IFC4X3_ADD2"):
        print(f"  IFC: unexpected schema {model.schema} (expected IFC4X3)")

    t = _get_table("lattice/bridge/ifc_elements")
    rows = []
    for el in model.by_type("IfcElement"):
        psets = ifcopenshell.util.element.get_psets(el)
        matrix = None
        try:
            matrix = ifcopenshell.util.placement.get_local_placement(
                el.ObjectPlacement
            ).tolist()
        except Exception:
            pass
        rows.append({
            "project_id": project_id,
            "source_element_id": el.GlobalId or "",
            "ifc_class": el.is_a(),
            "bis_class": el.is_a(),
            "bis_subclass": el.is_a(),
            "user_label": el.Name or "",
            "property_sets": psets,
            "ifc_version": model.schema,
        })
        if len(rows) >= 500:
            t.insert(rows)
            rows = []
    if rows:
        t.insert(rows)
    return len(list(model.by_type("IfcElement")))


def _ingest_dxf(output_dir: Path, project_id: str) -> int:
    dxf_dir = output_dir / "dxf"
    if not dxf_dir.exists():
        return 0
    try:
        import ezdxf
    except ImportError:
        print("  DXF: ezdxf not installed — run: uv add ezdxf")
        return 0

    t = _get_table("lattice/bridge/dwg_entities")
    total = 0
    for dxf_file in dxf_dir.glob("*.dxf"):
        try:
            doc = ezdxf.readfile(str(dxf_file))
            msp = doc.modelspace()
            rows = []
            for entity in msp:
                rows.append({
                    "project_id": project_id,
                    "source_file": dxf_file.name,
                    "entity_type": entity.dxftype(),
                    "layer": entity.dxf.layer if hasattr(entity.dxf, "layer") else "",
                    "handle": entity.dxf.handle or "",
                })
            if rows:
                t.insert(rows)
                total += len(rows)
        except Exception as e:
            print(f"  DXF: error reading {dxf_file.name}: {e}")
    return total


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_json(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _load_manifest(output_dir: Path) -> dict[str, Any]:
    p = output_dir / "manifest.json"
    if not p.exists():
        return {}
    with open(p, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def ingest_all(output_dir: str | Path, project_id: str | None = None) -> dict[str, int]:
    output_dir = Path(output_dir)
    manifest = _load_manifest(output_dir)

    pid = project_id or manifest.get("project_id") or "unknown"
    print(f"Ingesting {output_dir} → project_id={pid}")

    counts: dict[str, int] = {}
    counts["layers"] = _ingest_layers(output_dir, pid)
    counts["plants"] = _ingest_plants(output_dir, pid)
    counts["ifc_elements"] = _ingest_ifc(output_dir, pid)
    counts["dxf_entities"] = _ingest_dxf(output_dir, pid)

    print("Ingest complete:", counts)
    return counts


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: uv run {sys.argv[0]} <output_dir> [project_id]")
        sys.exit(1)
    _dir = sys.argv[1]
    _pid = sys.argv[2] if len(sys.argv) > 2 else None
    ingest_all(_dir, _pid)
