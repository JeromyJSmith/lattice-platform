"""lattice/bridge/itwin/* tables (Bentley iTwin Platform mirrors)."""

from __future__ import annotations

from migrations._helpers import banner, ensure_table

MIGRATION_ID = "0006_create_itwin_tables"

NAMESPACE = "lattice/bridge/itwin"


def schemas(pxt) -> dict[str, dict]:
    return {
        f"{NAMESPACE}/itwin_sync_jobs": {
            "id":                pxt.String,
            "itwin_id":          pxt.String,
            "imodel_id":         pxt.String,
            "sync_run_id":       pxt.String,
            "state":             pxt.String,    # 'NotStarted' | 'Queued' | 'Running' | 'Completed' | 'Failed'
            "result":            pxt.String,    # 'Success' | 'PartialSuccess' | 'Error'
            "started_at":        pxt.Timestamp,
            "ended_at":          pxt.Timestamp,
            "duration_ms":       pxt.Int,
            "vw_export_hash":    pxt.String,    # nullable; only populated when traceable
            "connector_count":   pxt.Int,
            "raw_payload":       pxt.Json,      # API response verbatim
            "observed_at":       pxt.Timestamp,
        },
        f"{NAMESPACE}/itwin_changed_elements": {
            "id":                pxt.String,
            "itwin_id":          pxt.String,
            "imodel_id":         pxt.String,
            "changeset_id":      pxt.String,
            "source_element_id": pxt.String,    # joins to ifc_elements + sidecars
            "change_kind":       pxt.String,    # 'inserted' | 'updated' | 'deleted'
            "bis_class":         pxt.String,
            "bis_subcategory":   pxt.String,
            "before_hash":       pxt.String,
            "after_hash":        pxt.String,
            "page":              pxt.Int,
            "page_size":         pxt.Int,
            "observed_at":       pxt.Timestamp,
            "raw_payload":       pxt.Json,
        },
        f"{NAMESPACE}/connector_versions": {
            "id":                pxt.String,
            "sync_run_id":       pxt.String,
            "connector_name":    pxt.String,    # e.g. 'IFC' | 'MicroStation' | 'OpenBuildings'  # allow-forbidden
            "connector_version": pxt.String,
            "bridge_assembly":   pxt.String,
            "observed_at":       pxt.Timestamp,
            "raw_payload":       pxt.Json,
        },
    }


def apply(pxt, dry_run: bool) -> dict:
    banner("0006 lattice/bridge/itwin tables", dry_run=dry_run)
    out: dict = {}
    for path, schema in schemas(pxt).items():
        action = ensure_table(pxt, path, schema, dry_run)
        out[path] = {"action": action, "cols": len(schema)}
        print(f"  {path:48s} -> {action} ({len(schema)} cols)")
    return out
