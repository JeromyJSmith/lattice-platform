"""lattice/bridge/health/{schema_drift_events, bridge_gap_matrix}."""

from __future__ import annotations

from migrations._helpers import banner, ensure_table

MIGRATION_ID = "0010_create_health_tables"

NAMESPACE = "lattice/bridge/health"


def schemas(pxt) -> dict[str, dict]:
    return {
        f"{NAMESPACE}/schema_drift_events": {
            "id":               pxt.String,
            "drift_event_id":   pxt.String,    # UUIDv7
            "severity":         pxt.String,    # 'info' | 'warn' | 'error'
            "drift_kind":       pxt.String,    # 'pxt_table_added' | 'pxt_table_missing' | 'vw_pset_added' | 'vw_pset_removed' | 'itwin_bis_class_changed' | 'contract_supersession'
            "scope":            pxt.String,    # 'lattice.execution' | 'lattice.bridge.vw' | ...
            "summary":          pxt.String,
            "before":           pxt.Json,
            "after":            pxt.Json,
            "detected_by":      pxt.String,    # 'bootstrap' | 'verify' | 'sync_observer' | 'sidecar.recorder'
            "detected_at":      pxt.Timestamp,
            "harness_run_id":   pxt.String,
        },
        f"{NAMESPACE}/bridge_gap_matrix": {
            "id":               pxt.String,
            "vw_export_hash":   pxt.String,
            "sync_run_id":      pxt.String,
            "vw_element_count":         pxt.Int,
            "ifc_element_count":        pxt.Int,
            "sidecar_element_count":    pxt.Int,
            "marpa_seed_count":         pxt.Int,
            "marpa_success_count":      pxt.Int,
            "marpa_partial_count":      pxt.Int,
            "marpa_fail_count":         pxt.Int,
            "itwin_changed_count":      pxt.Int,
            "promoted_entity_count":    pxt.Int,
            "supply_demand_ratio":      pxt.Float,
            "gap_score":                pxt.Float,    # 0.0 perfect .. 1.0 broken
            "computed_at":              pxt.Timestamp,
            "raw_breakdown":            pxt.Json,
        },
    }


def apply(pxt, dry_run: bool) -> dict:
    banner("0010 lattice/bridge/health tables", dry_run=dry_run)
    out: dict = {}
    for path, schema in schemas(pxt).items():
        action = ensure_table(pxt, path, schema, dry_run)
        out[path] = {"action": action, "cols": len(schema)}
        print(f"  {path:48s} -> {action} ({len(schema)} cols)")
    return out
