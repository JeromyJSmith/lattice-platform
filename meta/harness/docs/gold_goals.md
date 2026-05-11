<!-- spec-verified: code.claude.com/docs 2026-05-11 -->
# Gold Goals — docs (Documentation Meta-Harness, 9th section)

## Current Winning Criteria
- All 7 active mirrors in `scripts/doc-mirror-manifest.yaml` synced within last 14 days
- Every ACTIVE capability row in `analysis/capabilities/*-capability-registry.yaml` has at least one matching `lattice/knowledge/doc_chunks` row above 0.7 similarity
- Zero critical-severity rows in `lattice/knowledge/doc_coverage_gaps` table
- `score-docs.sh` exits 0 and returns valid JSON

## Required guardrails
- Must not regress: any other section's score
- Security / safety constraints: never commit doc-mirror local_path contents to repo (`.gitignore` `~/.lattice-doc-mirrors/`)
- Performance ceilings: full sync of all 7 mirrors must complete in under 5 minutes (cold) / 30 seconds (warm)
- Dependency constraints: mirror clones use `git clone --filter=blob:none --sparse` (no full-history pulls)

## Open gaps
- Gap: iTwin sparse-clone strategy undefined (~84 sub-repos)
  Blocking dependency: Issue #24
  Unknowns: which sub-repos map to Tier 1 from `meta/ITWIN_MAPPING.md`
- Gap: CityGML Vegetation ADE has no normative XSD as of 2026-05
  Blocking dependency: OGC publication timeline
  Unknowns: when ADE moves from conceptual model to published spec
- Gap: gap-detection heuristic threshold (0.7) is a guess; needs empirical tuning
  Blocking dependency: Issue #25
  Unknowns: precision/recall curve against hand-labeled doc coverage

## Candidate harness improvements
- Improvement: switch from `git clone --sparse` to `git archive` for read-only mirrors
  Expected contribution: +0.05 to sync_freshness (faster syncs)
  Evaluation plan: time both approaches over 3 runs; compare
- Improvement: auto-open GitHub issues for critical-severity coverage gaps
  Expected contribution: +0.10 to gap_resolution_velocity
  Evaluation plan: measure resolution time before/after over 2 weeks
- Improvement: cache embedding generation across mirror syncs (only re-embed changed chunks)
  Expected contribution: +0.15 to sync_freshness; reduces re-embed cost
  Evaluation plan: instrument run time; require ≥3x speedup before accepting

## Ratchet rule
Accept a change only if benchmark results improve on weighted goals and no guardrail fails.
