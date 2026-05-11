"""Server-side IFC normalization using ifcopenshell>=0.8.5.

Reads an .ifc file, walks all geometric elements, extracts canonical
attributes + property sets, and returns enriched payload.elements suitable
for upsert.upsert_vw_sidecar.

This is intentionally conservative: we extract well-known IFC entity
attributes plus *all* IfcPropertySet / IfcQuantitySet rows, then mark
property sets as `is_marpa_seed` based on `grammars/marpa_seed_psets.yaml`.
"""

from __future__ import annotations

import logging
import os
from importlib import import_module
from pathlib import Path
from typing import Any

import yaml

log = logging.getLogger("vwbridge.ifc")

_HERE = Path(__file__).resolve().parent.parent
SEED_CONFIG_PATH = _HERE / "grammars" / "marpa_seed_psets.yaml"

_LANDSCAPE_CLASSES: tuple[str, ...] = (
    "IfcGeographicElement",
    "IfcCivilElement",
    "IfcSite",
    "IfcSpace",
    "IfcDistributionElement",
    "IfcBuildingElementProxy",
    "IfcSlab",  # hardscape
)


def _load_seed_config() -> dict[str, Any]:
    """Load and normalize the MARPA seed pset config.

    The on-disk YAML uses a flat list under `seed_psets:` (one entry per
    pset), which is the most readable form for humans editing the grammar.
    Internally, `_classify_pset` expects a nested `seeds: {record_kind: [...]}`
    map for O(1) lookup by record_kind. We accept either shape on disk and
    always return the canonical nested form so callers don't need to care.
    """
    if not SEED_CONFIG_PATH.exists():
        return {"seeds": {}, "default_record_kind": "other"}
    raw = yaml.safe_load(SEED_CONFIG_PATH.read_text()) or {}
    if not isinstance(raw, dict):
        raw = {}

    seeds: dict[str, list[dict[str, Any]]] = {}
    nested = raw.get("seeds")
    if isinstance(nested, dict):
        for kind, group in nested.items():
            seeds[str(kind)] = list(group or [])

    flat = raw.get("seed_psets")
    if isinstance(flat, list):
        for entry in flat:
            if not isinstance(entry, dict):
                continue
            kind = str(entry.get("record_kind") or "other")
            seeds.setdefault(kind, []).append(entry)

    return {
        "seeds": seeds,
        "default_record_kind": raw.get("default_record_kind", "other"),
    }


def _safe_get(obj, attr: str, default=None):
    try:
        v = getattr(obj, attr, default)
        return v if v is not None else default
    except Exception:
        return default


def _bbox_from_placement(elt) -> tuple[list[float] | None, list[float] | None, list[float] | None]:
    try:
        geom = import_module("ifcopenshell.geom")
    except Exception:
        return None, None, None
    settings = geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)
    try:
        shape = geom.create_shape(settings, elt)
        # ifcopenshell.geom.create_shape() may return different wrapper types
        # depending on backend/build; not all expose `.geometry`.
        geometry = getattr(shape, "geometry", None)
        verts = getattr(geometry, "verts", None)
        if not verts:
            return None, None, None
        xs = verts[0::3]
        ys = verts[1::3]
        zs = verts[2::3]
        bmin = [min(xs), min(ys), min(zs)]
        bmax = [max(xs), max(ys), max(zs)]
        cx, cy, cz = ((a + b) / 2 for a, b in zip(bmin, bmax))
        return bmin, bmax, [cx, cy, cz]
    except Exception:
        return None, None, None


def _properties_of(elt) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    rels = _safe_get(elt, "IsDefinedBy", []) or []
    for rel in rels:
        if rel.is_a("IfcRelDefinesByProperties"):
            pset = rel.RelatingPropertyDefinition
            if pset is None:
                continue
            name = _safe_get(pset, "Name", "")
            props: dict[str, Any] = {}
            for sp in (_safe_get(pset, "HasProperties", []) or []):
                pname = _safe_get(sp, "Name", "")
                wrapped = _safe_get(sp, "NominalValue", None)
                pval = getattr(wrapped, "wrappedValue", None) if wrapped is not None else None
                if pname:
                    props[pname] = pval
            for sq in (_safe_get(pset, "Quantities", []) or []):
                qname = _safe_get(sq, "Name", "")
                qval = (
                    _safe_get(sq, "LengthValue")
                    or _safe_get(sq, "AreaValue")
                    or _safe_get(sq, "VolumeValue")
                    or _safe_get(sq, "CountValue")
                )
                if qname and qval is not None:
                    props[qname] = qval
            out.append({"pset_name": name, "properties": props})
    return out


def _classify_pset(pset_name: str, seed_cfg: dict[str, Any]) -> tuple[bool, str, list[str]]:
    seeds = seed_cfg.get("seeds") or {}
    for record_kind, group in seeds.items():
        for cfg in (group or []):
            if cfg.get("pset_name") == pset_name:
                return True, record_kind, list(cfg.get("select_keys") or [])
    return False, seed_cfg.get("default_record_kind", "other"), []


def parse_ifc(path: Path) -> dict[str, Any]:
    import ifcopenshell  # type: ignore

    log.info("ifcopenshell.open(%s)", path)
    f = ifcopenshell.open(str(path))
    schema = _safe_get(f, "schema", "")

    seed_cfg = _load_seed_config()
    elements: list[dict[str, Any]] = []

    for cls in _LANDSCAPE_CLASSES:
        try:
            instances = f.by_type(cls)
        except Exception:
            continue
        for elt in instances:
            sid = _safe_get(elt, "GlobalId", "")
            if not sid:
                continue
            bmin, bmax, centroid = _bbox_from_placement(elt)
            psets = _properties_of(elt)

            element_is_seed = False
            classified_psets = []
            for p in psets:
                is_seed, record_kind, sel_keys = _classify_pset(p["pset_name"], seed_cfg)
                element_is_seed = element_is_seed or is_seed
                slim = (
                    {k: v for k, v in p["properties"].items() if k in sel_keys}
                    if sel_keys else p["properties"]
                )
                classified_psets.append({
                    "pset_name":     p["pset_name"],
                    "is_marpa_seed": is_seed,
                    "record_kind":   record_kind,
                    "selected_keys": sel_keys,
                    "properties":    slim,
                })

            elements.append({
                "source_element_id":   sid,
                "ifc_class":           cls,
                "ifc_predefined_type": _safe_get(elt, "PredefinedType", ""),
                "name":                _safe_get(elt, "Name", "") or "",
                "long_name":           _safe_get(elt, "LongName", "") or "",
                "object_type":         _safe_get(elt, "ObjectType", "") or "",
                "tag":                 _safe_get(elt, "Tag", "") or "",
                "description":         _safe_get(elt, "Description", "") or "",
                "spatial_container_guid":  "",
                "spatial_container_class": "",
                "bbox_min":     bmin,
                "bbox_max":     bmax,
                "centroid":     centroid,
                "elevation_m":  (centroid[2] if centroid else 0.0),
                "marpa_seed":   element_is_seed,
                "raw_attributes": {"GlobalId": sid, "Name": _safe_get(elt, "Name", ""), "Tag": _safe_get(elt, "Tag", "")},
                "property_sets":  classified_psets,
            })

    return {"schema": schema, "elements": elements}


def enrich_payload_with_ifc(payload: dict[str, Any], ifc_path: Path, settings) -> dict[str, Any]:
    """Merge IFC parse into sidecar payload.

    Strategy: IFC is server-side ground truth for `elements[*].source_element_id`,
    `ifc_class`, `bbox_*`, `centroid`, `elevation_m`, `property_sets`.
    Sidecar-supplied semantic data (common_name, botanical_name, etc.) is
    preserved by `source_element_id` join.
    """
    file_size = ifc_path.stat().st_size
    if file_size > settings.IFC_MAX_BYTES:
        raise ValueError(f"IFC file {ifc_path} ({file_size} B) exceeds IFC_MAX_BYTES={settings.IFC_MAX_BYTES}")

    parsed = parse_ifc(ifc_path)
    by_sid = {el["source_element_id"]: el for el in (payload.get("elements") or [])}

    enriched: list[dict[str, Any]] = []
    for el in parsed["elements"]:
        sid = el["source_element_id"]
        prior = by_sid.get(sid, {})
        merged = {**el}
        if "semantic" in prior:
            merged["semantic"] = prior["semantic"]
        merged["marpa_seed"] = bool(merged.get("marpa_seed") or prior.get("marpa_seed"))
        enriched.append(merged)

    payload = {**payload, "elements": enriched}
    payload.setdefault("ifc", {})
    payload["ifc"]["schema"] = parsed.get("schema", payload["ifc"].get("schema", ""))
    payload["ifc"]["byte_size"] = file_size
    payload["ifc"]["filename"] = payload["ifc"].get("filename") or ifc_path.name
    return payload
