"""0014 — LATTICE Meta-Harness tables.

Adds the canonical harness namespace and four tables that support the
automated health-scoring, proposal evaluation, event logging, and
global decision-tracking cycle of the LATTICE Meta-Harness.

What this migration creates:

  lattice/harness/health_snapshots   — periodic health score captures per section
  lattice/harness/harness_proposals  — proposed changes and their evaluation outcome
  lattice/harness/section_events     — log of every harness action across sections
  lattice/harness/global_decisions   — cross-section decisions and policy changes

Type-surface note: Pixeltable 0.6.0 has no native Geometry / PostGIS column
type. All geometry columns store WKT or GeoJSON text in pxt.String. This
migration contains no geometry columns, but the rule stands — see
meta/SCHEMA.md for the canonical geometry-type guidance.
"""

from __future__ import annotations

import argparse
import sys

from migrations._helpers import (
    OWNED_PARENTS,
    assert_ownership,
    banner,
    ensure_namespace,
    ensure_table,
)

MIGRATION_ID = "0014_harness"

_OWNED: tuple[str, ...] = ("lattice/harness",)


# ---------- schema builders -------------------------------------------------

def _health_snapshots_schema(pxt) -> dict[str, object]:
    return {
        "snapshot_id":     pxt.String,    # uuid
        "section":         pxt.String,    # schema|api|frontend|georef-reality|genai|vw-itwin|ddc-infra|global
        "score":           pxt.Int,       # 0-100
        "score_breakdown": pxt.Json,      # per-criterion scores
        "captured_at":     pxt.Timestamp,
        "scoring_script":  pxt.String,    # path to script that produced this
        "git_sha":         pxt.String,    # commit at time of capture
    }


def _harness_proposals_schema(pxt) -> dict[str, object]:
    return {
        "proposal_id":   pxt.String,    # uuid
        "section":       pxt.String,
        "proposed_diff": pxt.String,    # unified diff text
        "score_before":  pxt.Int,
        "score_after":   pxt.Int,       # nullable — null if cycle didn't complete
        "outcome":       pxt.String,    # accepted|rejected|timeout|error
        "proposed_by":   pxt.String,    # agent identifier, e.g. 'claude-cli'
        "proposed_at":   pxt.Timestamp,
        "resolved_at":   pxt.Timestamp, # nullable
        "rationale":     pxt.String,    # nullable — model's stated reason
        "sandbox_path":  pxt.String,    # e.g. /tmp/harness-sandbox
    }


def _section_events_schema(pxt) -> dict[str, object]:
    return {
        "event_id":    pxt.String,    # uuid
        "section":     pxt.String,
        "event_type":  pxt.String,    # proposal.created|proposal.evaluated|proposal.accepted|
                                      # proposal.rejected|score.captured|ratchet.error|
                                      # cycle.started|cycle.completed
        "payload":     pxt.Json,
        "occurred_at": pxt.Timestamp,
        "proposal_id": pxt.String,    # nullable — references harness_proposals
    }


def _global_decisions_schema(pxt) -> dict[str, object]:
    return {
        "decision_id":       pxt.String,    # uuid
        "topic":             pxt.String,
        "decision":          pxt.String,    # the chosen direction
        "affected_sections": pxt.Json,      # list of section names
        "decided_at":        pxt.Timestamp,
        "decided_by":        pxt.String,
        "rationale":         pxt.String,
        "superseded_by":     pxt.String,    # nullable — decision_id of replacement
    }


# ---------- entry point -----------------------------------------------------

def apply(pxt, dry_run: bool) -> dict:
    assert_ownership(pxt, OWNED_PARENTS)
    assert_ownership(pxt, _OWNED)
    banner("0014 LATTICE Meta-Harness", dry_run=dry_run)
    out: dict = {}

    # 1. Namespace (lattice/ already exists; lattice/harness is new).
    out["lattice/harness"] = ensure_namespace(pxt, "lattice/harness", dry_run)
    print(f"  lattice/harness                              -> {out['lattice/harness']}")

    # 2. Harness tables (all new).
    harness = {
        "lattice/harness/health_snapshots":  _health_snapshots_schema(pxt),
        "lattice/harness/harness_proposals": _harness_proposals_schema(pxt),
        "lattice/harness/section_events":    _section_events_schema(pxt),
        "lattice/harness/global_decisions":  _global_decisions_schema(pxt),
    }
    for path, schema in harness.items():
        out[path] = ensure_table(pxt, path, schema, dry_run)
        print(f"  {path:46s} -> {out[path]} ({len(schema)} cols)")

    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run migration 0014_harness")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be created without touching Pixeltable.",
    )
    args = parser.parse_args()

    import pixeltable as pxt  # noqa: E402  (late import — keeps unit tests fast)

    result = apply(pxt, dry_run=args.dry_run)

    print()
    if args.dry_run:
        print("Dry-run complete. No tables were created.")
    else:
        print("Migration 0014_harness applied successfully.")
    sys.exit(0)
