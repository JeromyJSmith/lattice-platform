<!-- spec-verified: code.claude.com/docs 2026-05-11 -->
# Phase 0.7 — Pixeltable Knowledge Substrate Amendment

**Status:** binding. Phase 1 BLOCKED until Amendments 06 + 07 + 08 are all committed.

## Why this exists

The harness needs external memory. Without it, every fresh agent session re-derives knowledge from scratch or invents it from training-data priors that may be stale. The substrate gives the harness a queryable, embedding-indexed, computed-column-driven knowledge layer that backs the **anti-amnesia rule**.

This amendment is built atop verified Pixeltable 0.6.x facts:

- `pxt.Video`, `pxt.Audio`, `pxt.Document`, `pxt.Image`, `pxt.String` — all real types
- `pxt.Geometry` does NOT exist — geometry stays as `pxt.String` (WKT)
- Migration path is `pixeltable/migrations/` (NOT `pixeltable/service/migrations/`)
- `pxt.create_dir()` must be called for every ancestor namespace before tables

## File inventory added by this amendment

| File | Purpose |
|---|---|
| `pixeltable/migrations/0015_knowledge_substrate.py` | Creates `lattice/knowledge/*` (3 tables + 2 views with embedding indices) |
| `pixeltable/knowledge/__init__.py` | Package marker |
| `pixeltable/knowledge/tools.py` | `@pxt.query` tools: `search_tutorials`, `search_research`, `get_skill_for_tool` |
| `scripts/ingest-tutorials.py` | Stub (Issue #20 → full impl) |
| `scripts/ingest-research.py` | Stub (Issue #21 → full impl) |
| `.claude/rules/anti-amnesia.md` | Mandatory pre-flight rule for any external-tool code/doc |

## Migration 0015 — what it creates

**Order matters** (per Pixeltable owned-parents rule):

1. `pxt.create_dir('lattice')` — idempotent (already exists from 0001)
2. `pxt.create_dir('lattice/knowledge')` — new namespace
3. Table `lattice/knowledge/tutorials` with columns: `video` (`pxt.Video`), `source_url`, `tool_name`, `channel`, `title`, `view_count` (`pxt.Int`), `published_at` (`pxt.Timestamp`), `ingested_at` (`pxt.Timestamp`), `harvest_run`
4. Computed columns on tutorials (via `add_computed_column`):
   - `audio = extract_audio(tutorials.video, format='mp3')`
   - `audio_meta = get_metadata(tutorials.audio)`
   - `transcription = whisper.transcribe(audio=tutorials.audio, model='base.en')`
5. View `lattice/knowledge/tutorial_sentences` — iterator: `string_splitter(tutorials.transcription.text, separators='sentence')`; embedding index on `text` using `sentence_transformer.using(model_id='intfloat/e5-large-v2')`
6. Table `lattice/knowledge/research_docs` with columns: `document` (`pxt.Document`), `source_path`, `doc_type`, `tool_name`, `research_run`, `ingested_at` (`pxt.Timestamp`)
7. View `lattice/knowledge/research_chunks` — iterator: `DocumentSplitter` + embedding index on `text`
8. Table `lattice/knowledge/skills_registry` with columns: `skill_name`, `tool_name`, `skill_content`, `source_queries` (`pxt.Json`), `generated_at` (`pxt.Timestamp`), `generation_run`, `committed_path`

**`_helpers.py` update:** `lattice/knowledge` added to `OWNED_PARENTS` (plus `lattice/harness` from Amendment 06's migration 0014).

## pixeltable/knowledge/tools.py — three @pxt.query tools

- `search_tutorials(query_text, tool_name=None)` — top-10 sentences from tutorial_sentences, ranked by cosine similarity
- `search_research(query_text, tool_name=None)` — top-10 chunks from research_chunks
- `get_skill_for_tool(tool_name)` — most recent 5 generated skills for a tool

**Forbidden import:** `import Anthropic` does NOT appear in this file (cardinal rule).

## .claude/rules/anti-amnesia.md — when this fires

Pre-flight required before:

- Any `SKILL.md` write
- Any migration that adds an external service
- Any plan document
- Any architectural decision
- Any implementation code that calls a tool API

Threshold: 0.7 cosine similarity. Below this = harvest first, write second.

## Compounding effect with Amendment 06

The Capability Harvest Protocol (Amendment 06) produces *what tools can do*. The Knowledge Substrate (Amendment 07) produces *how to use them correctly*. Together they answer:

| Question | Answered by |
|---|---|
| Does graphify have an `impact` MCP tool? | Capability registry (Amendment 06) |
| What does graphify's `impact` tool actually do in practice? | `search_tutorials("graphify impact", tool_name="graphify-parisgroup")` (Amendment 07) |
| What's our current state for using it? | Registry row's `state:` field |
| What's the recommended invocation pattern? | `get_skill_for_tool("graphify-parisgroup")` |

Without both, the harness is half-blind.

## Issues created in Phase 8

- **#20** — Full implementation of `scripts/ingest-tutorials.py` (curated playlist manifests per tool, `graphifyy ingest`, video download, Pixeltable insert)
- **#21** — Full implementation of `scripts/ingest-research.py` (PDF/HTML/MD fetching, Document row creation)
- **#22** — First harvest pass on Graphify + GitNexus + InfraNodus tutorial coverage (run #20 + #21 against curated manifests)

## Exit conditions (Phase 2 amended)

Phase 2 (migrations) is not complete until:

1. Original Phase 2 exits met (migration 0014 applied; `pxt.list_tables('lattice/harness')` returns 4 tables)
2. **NEW:** migration 0015 applied; `pxt.list_tables('lattice/knowledge')` returns 5 entries (3 tables + 2 views)
3. **NEW:** `pixeltable/knowledge/tools.py` imports cleanly under `uv run python -c 'import pixeltable.knowledge.tools'` — no Anthropic SDK import, no NameError

## Anti-amnesia integration timeline

- This amendment lands the rule + the query tools + the schema
- Issue #20/#21 lands the harvest pipelines (fills the substrate with real content)
- Issue #22 runs the first harvest
- After that, every section harness's pre-propose step includes anti-amnesia pre-flight

Until the harvest runs, the substrate is empty and the rule fails-open (no results = no veto). Once content is in, the rule starts veto-ing low-confidence writes.

## Compounding effect with Amendment 08 (Docs Meta-Harness)

Amendment 08 (9th section) adds three more `@pxt.query` tools to `pixeltable/knowledge/tools.py`:

- `search_docs(query, tool_name, doc_category)` — upstream tool docs corpus (separate from `search_research`)
- `search_api_reference(query, tool_name)` — convenience wrapper, doc_category=api-reference
- `get_coverage_gaps(tool_name, severity)` — open gaps in `lattice/knowledge/doc_coverage_gaps`

The anti-amnesia rule is extended (in Amendment 08) so `search_api_reference` is **mandatory** pre-flight for implementation code. This closes the loop: registries say what exists, substrate (07) says how it's used in practice, docs substrate (08) says what the canonical spec is.

Migration 0016 (Amendment 08) adds 3 more tables + 1 view to `lattice/knowledge/` — does NOT recreate any 0015 entity. Post-0016 the namespace has 8 entries total.
