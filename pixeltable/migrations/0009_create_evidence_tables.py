"""lattice/bridge/evidence/{promotion_events, harness_run_refs}.

The harness's `runtime-runs/<run_id>/evidence-manifest.yaml` lands verbatim
into `promotion_events.evidence_manifest_yaml`, plus a parsed JSON copy.
`harness_run_refs` is the cross-walk between agent runs and bridge artifacts
they touched (sidecars, IFC parses, sync jobs, MARPA parses).
"""

from __future__ import annotations

from migrations._helpers import banner, ensure_table

MIGRATION_ID = "0009_create_evidence_tables"

NAMESPACE = "lattice/bridge/evidence"


def schemas(pxt) -> dict[str, dict]:
    return {
        f"{NAMESPACE}/promotion_events": {
            "id":                       pxt.String,
            "promotion_event_id":       pxt.String,    # UUIDv7
            "promotion_kind":           pxt.String,    # 'draw' | 'validate' | 'promote' | 'reject' | 'withdraw'
            "target_kind":              pxt.String,    # 'landscape_entity' | 'vw_export' | 'sync_run' | 'marpa_parse_run'
            "target_id":                pxt.String,
            "verdict":                  pxt.String,    # 'pass' | 'fail' | 'inconclusive'
            "triggered_by":             pxt.String,    # 'verifier.review.v1' | 'ci.pixeltable.gate' | 'operator.<handle>' | 'webhook.itwin.changedelements'
            "operator_handle":          pxt.String,
            "harness_run_id":           pxt.String,
            "outcome_md":               pxt.String,
            "evidence_manifest_yaml":   pxt.String,    # verbatim
            "evidence_manifest_parsed": pxt.Json,
            "skill_id":                 pxt.String,    # e.g. verifier.review.v1
            "skill_version":            pxt.String,
            "created_at":               pxt.Timestamp,
        },
        f"{NAMESPACE}/harness_run_refs": {
            "id":             pxt.String,
            "harness_run_id": pxt.String,
            "artifact_kind":  pxt.String,    # 'vw_export' | 'ifc_element' | 'itwin_sync_job' | 'marpa_parse_run' | 'changed_element'
            "artifact_id":    pxt.String,    # source-of-truth key (vw_export_hash, parse_run_id, etc.)
            "artifact_table": pxt.String,    # canonical PXT path
            "relation":       pxt.String,    # 'produced' | 'consumed' | 'observed' | 'promoted'
            "linked_at":      pxt.Timestamp,
            "raw_event":      pxt.Json,
        },
    }


def apply(pxt, dry_run: bool) -> dict:
    banner("0009 lattice/bridge/evidence tables", dry_run=dry_run)
    out: dict = {}
    for path, schema in schemas(pxt).items():
        action = ensure_table(pxt, path, schema, dry_run)
        out[path] = {"action": action, "cols": len(schema)}
        print(f"  {path:48s} -> {action} ({len(schema)} cols)")
    return out
