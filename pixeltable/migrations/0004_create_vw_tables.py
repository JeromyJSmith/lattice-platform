"""lattice/bridge/vw/* tables (Vectorworks export manifests)."""

from __future__ import annotations

from migrations._helpers import banner, ensure_table

MIGRATION_ID = "0004_create_vw_tables"

NAMESPACE = "lattice/bridge/vw"


def schemas(pxt) -> dict[str, dict]:
    return {
        f"{NAMESPACE}/vectorworks_exports": {
            "id":                 pxt.String,
            "vw_export_hash":     pxt.String,    # canonical join key
            "vw_export_id":       pxt.String,    # optional VWX-side UUIDv7
            "schema_version":     pxt.String,
            "vw_version":         pxt.String,
            "drawing_name":       pxt.String,
            "sheet_layer":        pxt.String,
            "ifc_filename":       pxt.String,
            "ifc_byte_size":      pxt.Int,
            "ifc_schema":         pxt.String,    # IFC2X3 | IFC4 | IFC4X3 | IFC4X3_ADD2
            "lane_ar_path":       pxt.String,
            "vwx_filename":       pxt.String,
            "vwx_byte_size":      pxt.Int,
            "exported_at":        pxt.Timestamp,
            "ingested_at":        pxt.Timestamp,
            "ingested_by":        pxt.String,    # operator handle
            "harness_run_id":     pxt.String,
            "raw_sidecar":        pxt.Json,      # full sidecar.json verbatim
            "exporter_warnings":  pxt.Json,      # list[str]
        },
    }


def apply(pxt, dry_run: bool) -> dict:
    banner("0004 lattice/bridge/vw tables", dry_run=dry_run)
    out: dict = {}
    for path, schema in schemas(pxt).items():
        action = ensure_table(pxt, path, schema, dry_run)
        out[path] = {"action": action, "cols": len(schema)}
        print(f"  {path:48s} -> {action} ({len(schema)} cols)")
    return out
