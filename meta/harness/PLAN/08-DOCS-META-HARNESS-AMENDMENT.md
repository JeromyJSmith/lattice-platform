<!-- spec-verified: code.claude.com/docs 2026-05-11 -->
# Phase 0.8 — Documentation Meta-Harness Amendment (9th Section)

**Status:** binding. Phase 1 unblocked once all three amendments (06 + 07 + 08) land.

## Why this exists

The Knowledge Substrate (Amendment 07) ingests tutorials and research docs into Pixeltable, but doesn't keep the upstream source of truth — the tool docs themselves — in sync. A tool ships a new MCP method tomorrow; without a docs-sync layer, our skills + capability registries silently drift.

The Documentation Meta-Harness is the **9th section** of the LATTICE Meta-Harness topology — distinct from the original 8 tool sections (Schema, API, Frontend, Georef/Reality, GenAI/Assets, VW Bridge/iTwin, DDC, CI/Infra). It is **cross-cutting** rather than a peer tool section — it serves all 8 by keeping the underlying docs corpus current, queryable, and gap-tracked.

**Section count: 8 + 1 = 9.** The Landscape Semantic Sidecar stays as an elevated goal inside GenAI/Assets (not a 10th).

## What this amendment ships

### Plan + section context

| File | Purpose |
|---|---|
| `meta/harness/PLAN/08-DOCS-META-HARNESS-AMENDMENT.md` | this file |
| `meta/harness/docs/GOAL.md` | fitness function for the docs harness |
| `meta/harness/docs/MEMORY.md` | session memo for docs-harness agent |
| `meta/harness/docs/AGENT.md` | docs-harness-agent definition (AGORA 3-layer frontmatter) |
| `meta/harness/docs/gold_goals.md` | compact ratchet target |
| `meta/harness/docs/score-docs.sh` | scoring stub (Issue #23 → full impl) |

### Migration 0016

| File | Purpose |
|---|---|
| `pixeltable/migrations/0016_docs_substrate.py` | 4 tables under `lattice/knowledge/`: `docs`, `doc_chunks` (view), `doc_sync_log`, `doc_coverage_gaps` |

Critical: 0016 does NOT overwrite 0015's tables. It calls `ensure_namespace(pxt, 'lattice/knowledge')` which is idempotent (returns "exists" if already present from 0015) and `ensure_table` likewise returns "exists" for any pre-created table. No table from 0015 is recreated.

### Scripts

| File | Purpose |
|---|---|
| `scripts/sync-doc-mirrors.sh` | stub (Issue #24 — sparse-clone all 7 mirrors, write git_sha_before/after) |
| `scripts/ingest-docs.py` | stub (Issue #24 — read manifest, insert pxt.Document rows + populate doc_sync_log) |
| `scripts/detect-doc-gaps.py` | stub (Issue #25 — compare ACTIVE capability rows against doc coverage) |
| `scripts/doc-mirror-manifest.yaml` | **NOT a stub.** Full YAML inventory of 7 doc mirrors. |

### Append to pixeltable/knowledge/tools.py (NOT overwrite)

Three new @pxt.query tools appended:
- `search_docs(query_text, tool_name=None, doc_category=None)`
- `search_api_reference(query_text, tool_name)`
- `get_coverage_gaps(tool_name=None, severity=None)`

### Append to .claude/rules/anti-amnesia.md (NOT overwrite)

Adds: also call `search_docs(query_text, tool_name)` before writing any code that calls a tool API. `search_api_reference()` is mandatory pre-flight for implementation code.

## The 9th-section design choice

| Aspect | Why a 9th section, not bolted onto an existing one |
|---|---|
| Scope | Docs corpus is cross-cutting — serves Schema, API, Frontend, etc. all equally. Putting it inside any one of them would skew its priorities. |
| Owner | Has its own agent (`docs-harness-agent`), GOAL.md, gold_goals.md, scoring script — meets the same template every other section follows. |
| Health signal | Adds a new top-level signal: `docs_coverage_pct` and `sync_freshness_score` roll up to the Global Meta-Harness alongside the other 7 signals. |
| Lifecycle | Docs-sync runs on a different cadence (cron/CI scheduled) than tool-section work (PR-driven). Independent harness lets each cadence breathe. |

## Migration 0016 — what it creates

Order (per owned-parents rule; `lattice/knowledge` already exists from 0015):

1. `ensure_namespace(pxt, 'lattice/knowledge')` — idempotent no-op
2. Table `lattice/knowledge/docs` — base corpus row per source doc
3. View `lattice/knowledge/doc_chunks` — DocumentSplitter with overlap + embedding index
4. Table `lattice/knowledge/doc_sync_log` — one row per sync operation
5. Table `lattice/knowledge/doc_coverage_gaps` — detected gaps (tool/code that lacks doc coverage)

**Verification gate (Phase 2 amendment):** `pxt.list_tables('lattice/knowledge')` should return **8 entries** post-0016 (3 tables + 2 views from 0015 + 3 tables from 0016 = 8).

## Fitness function — meta/harness/docs/GOAL.md

```
Score = (docs_coverage_pct × 0.4)
      + (sync_freshness_score × 0.2)
      + (spec_compliance_pct × 0.3)
      + (gap_resolution_velocity × 0.1)
```

Baseline: **0/100** (correct — no docs synced until Issue #24 runs).
Target: ≥ **80/100** before Phase 8 PR merge to main.

## Cross-link compounding effect

Amendment 06 → *what capabilities exist*
Amendment 07 → *how to use them correctly (from tutorials + research)*
Amendment 08 → *the upstream source of truth is fresh and tracked*

A query for "how do I use graphify's `impact` MCP tool" now hits all three:
1. Capability registry confirms `impact` is ACTIVE
2. `search_tutorials` returns user-recorded walkthroughs
3. `search_docs` returns the upstream README + API reference
4. `search_api_reference` returns the exact signature
5. `get_coverage_gaps` returns nothing → the harness is fully informed

If 4 returns nothing, the docs-sync layer is the failure point — and Job 15 (Phase 7) will have already flagged it as a gap before the agent reached this point.

## Issues created in Phase 8

- **#23** — Full implementation of `meta/harness/docs/score-docs.sh` (parse `doc_coverage_gaps` + `doc_sync_log`, compute weighted score)
- **#24** — Full implementation of `sync-doc-mirrors.sh` + `ingest-docs.py` (sparse clones, git-sha tracking, manifest-driven sync; itwin + citygml feasibility check)
- **#25** — Full implementation of `detect-doc-gaps.py` (cross-reference capability registries ACTIVE rows against doc corpus; produce ranked coverage gaps)
- **#26** — Wire docs-harness scoring into Global Meta-Harness composite via `lattice/harness/health_snapshots` (docs section gets a `docs_coverage_pct` column or its own snapshot row)

## Updates to other planning docs

- `00-OVERVIEW.md` — add Phase 0.8 row; section count noted as **9**
- `02-PLAN.md` — Phase 2 (migration 0016), Phase 4 (`meta/harness/docs/`), Phase 7 (new Job 15: docs-sync-freshness)
- `04-EXECUTION-HANDOFF.md` — Issues #23-26 appended
- `06-CAPABILITY-HARVEST-AMENDMENT.md` — note: capability registries reference `search_docs` as a pre-flight tool when the docs layer is live
- `07-PIXELTABLE-SUBSTRATE-AMENDMENT.md` — compounding effect cross-link
- `pixeltable/knowledge/tools.py` — append (not overwrite) the three new @pxt.query tools

## Exit conditions

Phase 2 (migrations) is not complete until:
1. Existing exits met (0014 + 0015 applied)
2. **NEW:** Migration 0016 applied; `pxt.list_tables('lattice/knowledge')` returns 8 entries total
3. **NEW:** `uv run python -c 'from pixeltable.knowledge.tools import search_docs, search_api_reference, get_coverage_gaps'` succeeds — confirms append didn't break

Phase 4 (Global scaffold) is not complete until:
1. Existing exits met
2. **NEW:** `meta/harness/docs/{GOAL,MEMORY,AGENT,gold_goals}.md` + `score-docs.sh` all exist; AGENT.md has AGORA 3-layer YAML frontmatter

Phase 7 (docs-sync-check expansion) gains:
- **Job 15: docs-sync-freshness** — verify `meta/harness/docs/score-docs.sh` exits 0 and emits valid JSON; verify `scripts/doc-mirror-manifest.yaml` is non-stub (has all 7 mirror entries with required keys)
