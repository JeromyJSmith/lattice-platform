<!-- spec-verified: code.claude.com/docs 2026-05-11 -->
# Anti-Amnesia Rule

**Standard introduced by Amendment 07** (see `meta/harness/PLAN/07-PIXELTABLE-SUBSTRATE-AMENDMENT.md`).

## The rule

Before writing any of the following, the agent MUST call the knowledge-substrate query tools and accept results above the **0.7 similarity threshold**. Below-threshold results = knowledge gap = stop and run the harvest pipeline before writing.

Fires before:

- Any `SKILL.md` write (call `get_skill_for_tool(tool_name)` first; if a registered skill exists, extend it rather than recreate)
- Any migration that adds an external service (call `search_research(query, tool_name)` first; pin the answer to a doc chunk)
- Any plan document (`search_research` to confirm prior decisions don't already exist)
- Any architectural decision (same)
- Any implementation code that calls a tool API (`search_tutorials` + `search_research`)

## Pre-flight contract

```python
# Before writing code that calls graphify's `impact` MCP tool, for example:
from pixeltable.knowledge.tools import search_tutorials, search_research, get_skill_for_tool

# 1. Is there a tutorial covering this?
tutorials = search_tutorials("graphify impact blast radius", tool_name="graphify-parisgroup").collect()
top_sim = max((r["similarity"] for r in tutorials), default=0.0)

# 2. Is there research-doc coverage?
research = search_research("graphify impact analysis", tool_name="graphify-parisgroup").collect()
top_research_sim = max((r["similarity"] for r in research), default=0.0)

# 3. Is there an existing skill?
skills = get_skill_for_tool("graphify-parisgroup").collect()

# Decision rule:
THRESHOLD = 0.7
if top_sim < THRESHOLD and top_research_sim < THRESHOLD and not skills:
    # Knowledge gap. Stop and run:
    #   bash scripts/ingest-tutorials.py
    #   bash scripts/ingest-research.py
    # Then re-query. Do NOT proceed to write the code with no substrate backing.
    raise RuntimeError("anti-amnesia: knowledge gap; run harvest before writing")
```

## Why

The agent does not retain memory across sessions. Without the substrate, every fresh session re-derives knowledge from scratch — or worse, invents knowledge based on training-data priors that may be stale or wrong for the specific tool version we're using.

The substrate (lattice/knowledge/tutorials + research_docs + skills_registry) is the agent's external memory. Anti-amnesia ensures the agent **uses** that memory before producing output.

## Similarity threshold rationale

`0.7` is the operational floor. Empirically:

- `> 0.85` = strong match; cite verbatim
- `0.7 – 0.85` = relevant; quote + paraphrase
- `0.5 – 0.7` = adjacent; treat as context, not authority — still must look elsewhere
- `< 0.5` = no real coverage; harvest must run first

The threshold can be tuned per-section in `<section-root>/gold_goals.md` if some sections need stricter retrieval.

## Enforcement

| Mechanism | Where | When |
|---|---|---|
| Rule file present | `.claude/rules/anti-amnesia.md` | Always loads at session start |
| Pre-flight check baked into section skills | `.claude/skills/lattice-*/SKILL.md` (Phase 6) | When the skill activates |
| CI gate | Phase 7 Job 14 will scan new SKILL.md / migration / plan files for `search_tutorials` or `search_research` invocation evidence in commit messages | On PR |
| `search_docs` (Amendment 08 append) | Added to this file by Amendment 08 — also call before implementation code | Always |

## What this rule does NOT do

- Does NOT prevent the agent from writing. It requires the agent to **check first**.
- Does NOT replace human review. A reviewer can still reject content that passed the substrate threshold but doesn't fit the use case.
- Does NOT mean "if substrate is empty, do nothing". It means "if substrate is empty, harvest first, then write."

## Amendment 08 extension — docs queries are mandatory pre-flight too

In addition to `search_tutorials` and `search_research`, the agent MUST call:

- **`search_docs(query_text, tool_name)`** — before writing any code that calls a tool API. The Documentation Meta-Harness (9th section) keeps upstream tool docs synced into `lattice/knowledge/doc_chunks`. If `search_docs` returns nothing above threshold for the tool you're about to use, the docs-sync layer hasn't covered that tool yet — file or escalate to Issue #24.
- **`search_api_reference(query_text, tool_name)`** — **mandatory** for implementation code. Stricter than `search_docs` because it returns only the canonical API reference chunks. If empty, do not invent function signatures from memory.
- **`get_coverage_gaps(tool_name, severity='critical')`** — call before any decision that depends on a tool. A critical-severity gap on the tool you're about to use is a hard stop; harvest the docs first via `scripts/sync-doc-mirrors.sh` + `scripts/ingest-docs.py`.

The three tools compound:

1. `get_skill_for_tool` → reuse existing skill if present
2. `search_api_reference` → ground new code in the canonical API signature
3. `search_tutorials` + `search_research` → ground new code in real-world usage
4. `get_coverage_gaps` → confirm no known gap blocks this work

If any of (2) returns < 0.7 similarity, the agent must:
- Stop coding
- Run `bash scripts/sync-doc-mirrors.sh && uv run python scripts/ingest-docs.py`
- Re-query — and if STILL empty, file a coverage gap rather than proceeding

## Cross-references

- `pixeltable/migrations/0015_knowledge_substrate.py` — tutorials/research/skills schema
- `pixeltable/migrations/0016_docs_substrate.py` — docs/doc_chunks/sync_log/coverage_gaps schema
- `pixeltable/knowledge/tools.py` — the `@pxt.query` tools to call (6 total after Amendment 08)
- `scripts/ingest-tutorials.py` / `scripts/ingest-research.py` / `scripts/ingest-docs.py` / `scripts/sync-doc-mirrors.sh` / `scripts/detect-doc-gaps.py` — the harvest pipelines (stubs now)
- `meta/harness/docs/` — the 9th-section harness that owns the docs corpus
- `.claude/rules/capability-harvest-protocol.md` — sibling rule for tool capabilities
- `.claude/rules/zero-dead-dna.md` — sibling rule for unused capabilities
