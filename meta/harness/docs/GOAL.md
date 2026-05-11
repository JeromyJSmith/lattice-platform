<!-- spec-verified: code.claude.com/docs 2026-05-11 -->
# GOAL — docs (Documentation Meta-Harness, 9th section)

## Fitness Function
- Primary metric: output of `meta/harness/docs/score-docs.sh`
- Formula: `Score = (docs_coverage_pct × 0.4) + (sync_freshness_score × 0.2) + (spec_compliance_pct × 0.3) + (gap_resolution_velocity × 0.1)`
- Baseline: **0/100** (expected — no docs synced until Issue #24 runs)
- Target plateau: **≥ 80/100** before Phase 8 PR merge to `main`

## Required guardrails
- Must not regress: any other section's score (docs sync should never break upstream tool query paths)
- Spec compliance: every newly-ingested doc passes the InfraNodus corpus checklist (`.claude/rules/infranodus-corpus.md`)
- Freshness ceiling: no mirror older than 14 days at score-time
- Sync atomicity: `doc_sync_log.sync_status` must be `ok` for every active mirror to count toward score

## Improvement Loop
1. Read `meta/harness/docs/gold_goals.md` for current winning criteria
2. Read `analysis/infranodus/goals.graph.json` for structural gaps in goals (optimize=gaps)
3. Consult `analysis/gaps/docs-gap-report.md` for ranked coverage gaps (will exist post-Issue #25)
4. Propose ONE docs-harness change (sync schedule tune, new mirror, gap-detector heuristic)
5. Run `bash meta/harness/docs/score-docs.sh` — accept only if score improves AND no guardrail fails
6. Write result to `meta/harness/docs/iterations.jsonl`
7. If stuck for 3+ iterations → switch InfraNodus mode to `optimize=reinforce`

## Action Catalog
- Modify own `CLAUDE.md` / `MEMORY.md` context
- Edit `scripts/doc-mirror-manifest.yaml` to add/remove mirrors (PR-reviewed)
- Tune sync cadence (cron expression in `.github/workflows/`)
- Propose new gap-detection heuristic (`scripts/detect-doc-gaps.py` extension)
- Update `gold_goals.md` when plateau reached
- File coverage-gap issues for un-documented tool surfaces

## Operating Mode
infranodus_mode: gaps
last_score: 0
last_run: never
iterations_completed: 0
plateau_detected: false
