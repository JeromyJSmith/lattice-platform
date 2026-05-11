"""0014 — Meta-Harness schema (Phase 2 of the harness build).

Creates `lattice/harness/*` — the four tables that back the Global
Meta-Harness's seven health signals and the section-event reporting
protocol.

What this migration creates:

  lattice/harness/                       (new namespace)
  lattice/harness/health_snapshots       — 7 health signals per section per timestamp
  lattice/harness/harness_proposals      — proposals made, accepted/rejected, evidence ref
  lattice/harness/section_events         — events fired upward from section harnesses
  lattice/harness/global_decisions       — decisions made by Global Meta-Harness

Type-surface notes (verified against Pixeltable 0.6.x docs):
  - pxt.String, pxt.Float, pxt.Int, pxt.Timestamp, pxt.Bool, pxt.Json — all real
  - pxt.Geometry does NOT exist — n/a here (no geometry columns)
  - Migration path is pixeltable/migrations/ (verified)

Ordering: applies after 0013 (georef + reality + mirror) and before 0015
(knowledge substrate). No cross-namespace FK; lattice/harness is
independent of other namespaces.
"""

from __future__ import annotations

from migrations._helpers import (
    OWNED_PARENTS,
    assert_ownership,
    banner,
    ensure_namespace,
    ensure_table,
)

MIGRATION_ID = "0014_harness_schema"


# ---------- schemas -------------------------------------------------------

def _health_snapshots_schema(pxt) -> dict[str, object]:
    return {
        "id":                          pxt.String,
        "snapshot_id":                 pxt.String,
        "timestamp":                   pxt.Timestamp,
        "section":                     pxt.String,
        "schema_health":               pxt.Float,
        "graph_structural_health":     pxt.Float,
        "graph_execution_health":      pxt.Float,
        "semantic_gap_score":          pxt.Float,
        "ci_health":                   pxt.Float,
        "issue_velocity":              pxt.Float,
        "agent_onboarding_coverage":   pxt.Float,
        "composite_score":             pxt.Float,
        "notes":                       pxt.String,
    }


def _harness_proposals_schema(pxt) -> dict[str, object]:
    return {
        "id":                pxt.String,
        "proposal_id":       pxt.String,
        "timestamp":         pxt.Timestamp,
        "section":           pxt.String,
        "proposer_agent":    pxt.String,
        "proposal_summary":  pxt.String,
        "files_changed":     pxt.Json,
        "eval_score":        pxt.Float,
        "outcome":           pxt.String,    # accepted | rejected | superseded | rolled-back
        "evidence_path":     pxt.String,
        "run_id":            pxt.String,    # FK to lattice/execution/agent_runs
    }


def _section_events_schema(pxt) -> dict[str, object]:
    return {
        "id":               pxt.String,
        "event_id":         pxt.String,
        "timestamp":        pxt.Timestamp,
        "section":          pxt.String,
        "event_type":       pxt.String,
        "signal":           pxt.String,
        "score_before":     pxt.Float,
        "score_after":      pxt.Float,
        "cause":            pxt.String,
        "proposed_fix":     pxt.String,
        "evidence_ref":     pxt.String,
        "resolved":         pxt.Bool,
    }


def _global_decisions_schema(pxt) -> dict[str, object]:
    return {
        "id":                       pxt.String,
        "decision_id":              pxt.String,
        "timestamp":                pxt.Timestamp,
        "trigger_events":           pxt.Json,
        "lowest_health_section":    pxt.String,
        "proposed_action":          pxt.String,
        "action_taken":             pxt.String,
        "result_summary":           pxt.String,
        "session_id":               pxt.String,
    }


# ---------- entry point ---------------------------------------------------

def apply(pxt, dry_run: bool) -> dict:
    assert_ownership(pxt, OWNED_PARENTS)
    banner("0014 meta-harness schema", dry_run=dry_run)
    out: dict = {}

    # 1. Ancestor namespace (idempotent).
    out["lattice"] = ensure_namespace(pxt, "lattice", dry_run)
    print(f"  lattice                                      -> {out['lattice']}")

    # 2. lattice/harness namespace (new).
    out["lattice/harness"] = ensure_namespace(pxt, "lattice/harness", dry_run)
    print(f"  lattice/harness                              -> {out['lattice/harness']}")

    # 3. Four tables.
    tables = {
        "lattice/harness/health_snapshots":   _health_snapshots_schema(pxt),
        "lattice/harness/harness_proposals":  _harness_proposals_schema(pxt),
        "lattice/harness/section_events":     _section_events_schema(pxt),
        "lattice/harness/global_decisions":   _global_decisions_schema(pxt),
    }
    for path, schema in tables.items():
        out[path] = ensure_table(pxt, path, schema, dry_run)
        print(f"  {path:46s} -> {out[path]} ({len(schema)} cols)")

    return out
