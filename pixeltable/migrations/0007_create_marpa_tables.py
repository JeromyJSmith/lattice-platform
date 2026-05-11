"""lattice/bridge/marpa/marpa_parse_runs (one row per parse attempt)."""

from __future__ import annotations

from migrations._helpers import banner, ensure_table

MIGRATION_ID = "0007_create_marpa_tables"

NAMESPACE = "lattice/bridge/marpa"


def schemas(pxt) -> dict[str, dict]:
    return {
        f"{NAMESPACE}/marpa_parse_runs": {
            "id":                pxt.String,
            "parse_run_id":      pxt.String,    # UUIDv7
            "vw_export_hash":    pxt.String,
            "source_element_id": pxt.String,
            "pset_name":         pxt.String,
            "record_kind":       pxt.String,    # planting | irrigation | topography | hardscape
            "grammar_version":   pxt.String,    # e.g. marpa.landscape.v1.0.0
            "input_tokens":      pxt.Json,      # list[str] flattened from pset
            "parse_status":      pxt.String,    # 'success' | 'partial' | 'fail'
            "ambiguity_score":   pxt.Float,     # 0.0 unambiguous .. 1.0 hard fail
            "partial_parse_json": pxt.Json,     # ActionResult.record
            "error_message":     pxt.String,
            "duration_ms":       pxt.Int,
            "runner_kind":       pxt.String,    # 'subprocess.r3' | 'python.fallback'
            "started_at":        pxt.Timestamp,
            "ended_at":          pxt.Timestamp,
            "harness_run_id":    pxt.String,
        },
    }


def apply(pxt, dry_run: bool) -> dict:
    banner("0007 lattice/bridge/marpa tables", dry_run=dry_run)
    out: dict = {}
    for path, schema in schemas(pxt).items():
        action = ensure_table(pxt, path, schema, dry_run)
        out[path] = {"action": action, "cols": len(schema)}
        print(f"  {path:48s} -> {action} ({len(schema)} cols)")
    return out
