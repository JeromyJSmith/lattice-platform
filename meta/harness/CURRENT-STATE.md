# Meta-Harness Current State

Snapshot date: 2026-05-12.

## Inventory

| Area | Current state |
|---|---|
| Capability registries | 23 registry files under `analysis/capabilities/` |
| Capability rows | 200 total: 153 ACTIVE, 44 DEFERRED, 3 BLOCKED |
| Bootstrap-empty registries | 4: `claude-code`, `deck-gl`, `pixeltable`, `web-ifc` |
| Pixeltable migrations | 16 landed migrations, next migration is `0017` |
| Harness docs | Top-level docs now exist for delegation, library, model fit, verifier, benchmarking, drop zones, hooks, sandboxes, DDC, and bash safety |
| Verification scripts | `scripts/lattice-verify.sh`, `scripts/audit-dead-dna.sh`, `scripts/check-python-docstrings.py`, `scripts/pre-commit-docs-check.sh` |
| Library catalog | `meta/harness/library.yaml` catalogs prompts, capabilities, references, and jobs |
| Outer wrapper | `/Volumes/PixelTable/VW_iTWIN_Bridge/meta/` registers this repo as body cell `body.vw_itwin_bridge` |
| Source grounding | `meta/harness/source-grounding.md` now records the Meta-Harness, GOAL.md, and autoresearch lineage |
| Domain spec | `meta/harness/domain_spec.md` now exists with unknowns explicit |

## What Is Wired

| Surface | Wired artifact |
|---|---|
| Capability lifecycle | `analysis/capabilities/README.md`, templates, registry audit |
| Zero Dead DNA | `scripts/audit-dead-dna.sh`, local pre-commit, CI job |
| Python docstring rule | `scripts/check-python-docstrings.py`, local pre-commit, CI job |
| Verifier core | `scripts/lattice-verify.sh`, `meta/verification/VERIFIER.md` |
| Pi verifier pattern | `meta/verification/pi-verifier-surface.md` |
| Disler / IndyDevDan patterns | Capability registries plus `meta/harness/indydevdan-incorporation.md` |
| uv single-file agents | `meta/harness/single-file-harness-agents.md` |
| Ephemeral library pattern | `meta/harness/agentics-library.md`, `meta/harness/library.yaml` |
| Model-fit loop | `meta/harness/model-fit.md`, `meta/harness/benchmarking.md` |
| DDC capability registry | `analysis/capabilities/ddc-capability-registry.yaml` with six contract-only rows |
| Capability operator surface | `/harness/capabilities`, `/harness/benchmarks`, `pixeltable/service/routes/harness.py` |

## What Is Still Stubbed Or Not Live

| Gap | Current file |
|---|---|
| Docs scoring implementation | `meta/harness/docs/score-docs.sh` |
| Docs mirror sync | `scripts/sync-doc-mirrors.sh` |
| Docs ingestion | `scripts/ingest-docs.py` |
| Tutorial ingestion | `scripts/ingest-tutorials.py` |
| Research ingestion | `scripts/ingest-research.py` |
| Docs gap detection | `scripts/detect-doc-gaps.py` |
| Outer wrapper ingestion/evidence contract | Exists as folders and config, but not yet wired to body-cell verification output |
| Pixeltable population of harness registries | Not implemented |
| DuckDB WASM analytical surface over harness data | Not implemented |
| Legacy Python uplift | Not implemented beyond changed-file docstring ratchet |
| Standalone Meta-Harness extraction | Not started |
| DDC proof promotion | Registry exists; no DDC row is proof-backed yet |

## Important Directional Decisions

- Pixeltable holds everything in LATTICE over time: capabilities, evidence, runs, docs, diagrams, scripts, benchmark results, task state, and relationships.
- Git still owns source changes and review until the Pixeltable substrate is mature enough to act as the operational source of truth.
- DuckDB WASM consumes Arrow/Parquet served from Pixeltable for browser-side analytics.
- uv inline metadata is the default shape for runnable one-shot Python harness scripts.
- Legacy Python files need an uplift pipeline, not ad hoc cleanup in unrelated PRs.
- Meta-Harness should likely become its own reusable repository after the first LATTICE dry run proves the contract.

## Repomix Cross-Check

The outer wrapper Repomix at `/Volumes/PixelTable/VW_iTWIN_Bridge/meta/meta-repomix.xml` confirms that this repo is not the whole harness. It is the active body cell inside an enclosing root harness.

| Wrapper artifact | Current implication |
|---|---|
| `/Volumes/PixelTable/VW_iTWIN_Bridge/meta/body-registry.yaml` | Body cell is `/Volumes/PixelTable/VW_iTWIN_Bridge/VW_iTwin_Bridge` |
| `/Volumes/PixelTable/VW_iTWIN_Bridge/meta/config.yaml` | Current phase is still `runtime_mvp`: prove browser -> router -> agent runtime -> event ledger -> replay |
| `/Volumes/PixelTable/VW_iTWIN_Bridge/meta/{inbox,outbox,runs,evidence,graph,memory,relationships}/` | First dry run needs to emit or reference wrapper-level evidence, not only chat output |
| `/Volumes/PixelTable/VW_iTWIN_Bridge/meta/docs/lattice-meta-harness-0.6-0.9-claude-code-prompt.md` | Docs mirror and Docs Meta-Harness details are part of the pre-dry-run contract |

Conclusion: we are directionally on track, but the next dry-run task was too early as written. Add a pre-dry-run reconciliation gate first, then complete the domain spec before any implementation run.

## Verification Snapshot

Last local checks performed for commit `c83c8b4`:

```bash
bash scripts/audit-dead-dna.sh
uv run python scripts/check-python-docstrings.py
uv run --extra dev pytest tests/no_pxt/test_harness_capability_runs.py
bun test src/runtime/pixeltable/sidecar-client.test.ts
bunx biome check src/components/Header.tsx src/runtime/pixeltable/sidecar-client.ts src/runtime/pixeltable/sidecar-client.test.ts src/routes/harness src/server/harness
bash scripts/pre-commit-docs-check.sh
bash scripts/lattice-verify.sh HEAD
bun run build
git diff --check
```

All listed checks passed before commit `c83c8b4`. Run them again before the next commit.
