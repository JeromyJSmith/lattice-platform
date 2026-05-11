"""lattice/bridge/ifc/* tables (server-side ifcopenshell parse output)."""

from __future__ import annotations

from migrations._helpers import banner, ensure_table

MIGRATION_ID = "0005_create_ifc_tables"

NAMESPACE = "lattice/bridge/ifc"


def schemas(pxt) -> dict[str, dict]:
    return {
        f"{NAMESPACE}/ifc_elements": {
            "id":                pxt.String,
            "vw_export_hash":    pxt.String,
            "source_element_id": pxt.String,    # IfcGloballyUniqueId
            "ifc_class":         pxt.String,    # e.g. IfcGeographicElement
            "ifc_predefined_type": pxt.String,
            "name":              pxt.String,
            "long_name":         pxt.String,
            "object_type":       pxt.String,
            "tag":               pxt.String,
            "description":       pxt.String,
            "spatial_container_guid": pxt.String,
            "spatial_container_class": pxt.String,
            "bbox_min":          pxt.Json,      # [x, y, z]
            "bbox_max":          pxt.Json,      # [x, y, z]
            "centroid":          pxt.Json,      # [x, y, z]
            "elevation_m":       pxt.Float,
            "is_marpa_seed":     pxt.Bool,
            "parsed_at":         pxt.Timestamp,
            "ifc_schema":        pxt.String,
            "raw_attributes":    pxt.Json,      # IFC entity attribute dump
        },
        f"{NAMESPACE}/ifc_property_sets": {
            "id":                pxt.String,
            "vw_export_hash":    pxt.String,
            "source_element_id": pxt.String,
            "pset_name":         pxt.String,
            "is_marpa_seed":     pxt.Bool,
            "record_kind":       pxt.String,    # planting | irrigation | topography | hardscape | other
            "selected_keys":     pxt.Json,      # list[str]
            "properties":        pxt.Json,      # dict[str, Any]
            "parsed_at":         pxt.Timestamp,
        },
    }


def apply(pxt, dry_run: bool) -> dict:
    banner("0005 lattice/bridge/ifc tables", dry_run=dry_run)
    out: dict = {}
    for path, schema in schemas(pxt).items():
        action = ensure_table(pxt, path, schema, dry_run)
        out[path] = {"action": action, "cols": len(schema)}
        print(f"  {path:48s} -> {action} ({len(schema)} cols)")
    return out
