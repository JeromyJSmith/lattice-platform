<!-- spec-verified: code.claude.com/docs 2026-05-11 -->
# MEMORY — docs (Documentation Meta-Harness)

## Platform State

- Section: docs (9th cross-cutting section)
- Owner agent: `docs-harness-agent` (see `meta/harness/docs/AGENT.md`)
- Substrate tables: `lattice/knowledge/{docs, doc_chunks, doc_sync_log, doc_coverage_gaps}` — planning artifacts in migration 0016, not yet applied
- Manifest: `scripts/doc-mirror-manifest.yaml` — 7 active mirrors + 2 deferred
- Current score: 0/100 (no syncs run yet; expected baseline)

## Open Decisions

- iTwin sparse-clone strategy (Issue #24) — full 84-repo sweep is wasteful; need to pick the subset that maps to LATTICE Tier 1 from `meta/ITWIN_MAPPING.md`
- CityGML Vegetation ADE mirror target unclear until OGC publishes normative XSD
- Sync cadence: nightly vs on-tool-version-bump (driven by capability registry `tool_version` field changes)
- Whether `doc_coverage_gaps` rows should auto-open GitHub issues (severity=critical) or accumulate for batch review

## Failed Experiments

- (none yet — section is new in Amendment 08)

## Session Handoff Notes

- Stubs only. Score will sit at 0/100 until Issues #23–#26 execute.
- Do NOT edit any landed migration; if 0016 needs adjustment, write 0017.
- When implementing `scripts/sync-doc-mirrors.sh`, use sparse-clone (`git clone --depth 1 --filter=blob:none --sparse`) — do NOT clone full repos for tools that ship 10+ MB of binary assets.
- When implementing `detect-doc-gaps.py`, cross-reference `analysis/capabilities/*-capability-registry.yaml` ACTIVE rows against `lattice/knowledge/docs` rows by `tool_name` — gap = ACTIVE capability with no doc coverage above similarity 0.7.
