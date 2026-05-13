# Phase 2 — mapping (content work)

Per-row triage + canonical MAP artifacts that connect harvest → operator workflow.

## Landed 2026-05-13 (commit 0dfd23f)

| Artifact | Path | State |
|---|---|---|
| Operator workflow map | `meta/capability-research/mapping/operator-workflow-map.md` | ✅ Landed |
| Source acquisition policy | `meta/capability-research/inventory/source-acquisition-policy.md` | ✅ Landed |
| InfraNodus curated runbook | (in tools/) | ✅ Landed |

## Landed 2026-05-13 (commit 534af6e)

| Artifact | State |
|---|---|
| All 23 advisory-stale rows cleared (per-row decisions) | ✅ Done |

## Still pending

| Artifact | Why not yet | Blocker |
|---|---|---|
| Operator-mapping fields template (the 8 fields) | Not written | None — content work |
| Harness contract for `infranodus-curated-gap-analysis` (formal verifier) | Not written | Needs one successful curated gap analysis run as proof, which needs Phase 1 env-var export |

## Where MAP content lives

Canonical home: `meta/capability-research/mapping/`. Add new map artifacts as siblings
to `operator-workflow-map.md`. Don't pile into `phases/phase-2-mapping/` — that
folder is for staging research/decisions, not final artifacts.
