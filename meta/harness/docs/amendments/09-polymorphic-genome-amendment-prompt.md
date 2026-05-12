---
title: "Lattice Meta-Harness Phase 1 Amendment — Polymorphic Skills Genome"
type: "amendment"
status: "shipped"
historical_only: true
shipped_in_commit: TBD-Phase-1
superseded_by: null
source: "lattice-meta-harness-0.6-0.9-claude-code-prompt.md"
---
You are resuming work on branch `feature/meta-harness` of the LATTICE platform.

---

## CURRENT STATE

- Last commit: `3d1c80b` — "feat(harness): Phase 0.6 — Capability Harvest Amendment"
- Branch is 4 commits ahead of main.

**Committed under `.claude/`:**
- `.claude/rules/capability-harvest-protocol.md`
- `.claude/rules/zero-dead-dna.md`
- `.claude/rules/dependency-allowlist.md`
- `.claude/rules/infranodus-corpus.md`

**Missing / To Be Created:**
- `.mcp.json` (root)
- `.claude/settings.json` (hooks)
- `.claude/commands/` (slash commands)
- `.claude/skills/` (InfraNodus bundled + GitNexus generated)
- `.claude/rules/anti-amnesia.md`
- `.claude/rules/lattice-security.md`
- `pixeltable/migrations/0015_knowledge_substrate.py`
- `pixeltable/migrations/0016_docs_substrate.py`
- `pixeltable/knowledge/__init__.py`
- `pixeltable/knowledge/tools.py`
- Script stubs: `ingest-tutorials.py`, `ingest-research.py`, `ingest-docs.py`, `sync-doc-mirrors.sh`, `detect-doc-gaps.py`, `audit-dead-dna.sh`
- `scripts/doc-mirror-manifest.yaml`
- `meta/harness/PLAN/07-PIXELTABLE-SUBSTRATE-AMENDMENT.md`
- `meta/harness/PLAN/08-DOCS-META-HARNESS-AMENDMENT.md`
- `meta/harness/docs/` scaffold: `GOAL.md`, `MEMORY.md`, `AGENT.md`, `gold_goals.md`, `score-docs.sh`
- `analysis/capabilities/*.yaml` (registries)

---

## GOVERNING RULES & API FACTS

### Pixeltable API Constraints (Verified)

- **Types:** `pxt.Video`, `pxt.Audio`, `pxt.Document`, `pxt.String` (use for WKT geometry; `pxt.Geometry` does NOT exist), `pxt.Timestamp`, `pxt.Json`
- **Required pattern:** Must call `pxt.create_dir()` for all ancestors before creating tables
- **Tool patterns:** Define `@pxt.query` inside `tools.py`, NEVER inside a migration file
- **Migrations are write-once.** Never edit landed migrations `0001–0013`
- **Migration path:** `pixeltable/migrations/` (NOT `pixeltable/service/migrations/`)
- **Next migration number:** `0015` (check if `0014` exists first)

### Environment Constraints

- `uv` only for Python
- No Anthropic SDK in client code
- Every commit adding a migration MUST update: `meta/SCHEMA.md`, `meta/ARCHITECTURE.md`, `meta/HANDOFF.md`, and the `CLAUDE.md` LIVE STATE block
- Run `scripts/pre-commit-docs-check.sh` before every commit

---

## TASK — Execute strictly in this sequence

**Do NOT ask clarifying questions. Execute fully, commit after each step.**

---

## STEP 0: Audit First

Before writing anything, run:

```bash
find .claude -type f | sort
ls analysis/capabilities/
ls pixeltable/migrations/ | grep -E "001[4-9]"
cat meta/SCHEMA.md | grep "Migrations applied"
```

Print the results, then proceed.

---

## STEP 1: AMENDMENT 09 — Security Remediation

Create `.claude/rules/lattice-security.md`:

```markdown
# LATTICE Security Rules

Project-local security rules for the LATTICE platform.
These live in `.claude/rules/` (version-controlled) and override
the minimal global baseline in `~/.claude/rules/security.md`.

## Approved install patterns for this project

- `curl` to `/tmp/` for inspection THEN exec after review — OK for graphify-parisgroup
- `uv tool install graphify` — OK (isolated uv tool environment)
- `npx -y infranodus-mcp-server` — OK (ephemeral, no global install)
- `npm install gitnexus --save-dev` — OK (project-local devDep, never `-g`)

## Approved cross-project read/write paths

- `~/.lattice-docs/`          read/write (doc mirrors)
- `~/.claude-code-docs/`      read/write (Claude Code doc mirror)
- `~/.vectorworks-docs/`      read-only  (VW SDK docs)
- `~/.gitnexus/`              read/write (GitNexus registry, managed by CLI)
- `/tmp/`                     write then clean (temporary downloads)

## Banned Patterns

- `npm install -g <anything>` — global installs are banned for this project
- `pip` / `conda` / `poetry` / `pipenv` — `uv` only
- Reading `~/.ssh/`, `~/.aws/`, `~/.config/` without explicit per-session user confirmation
- Any write outside the repo root or the approved paths above without explicit user confirmation

## Pipe-to-shell rule (project-specific override)

For this project, `curl | bash` and `wget | sh` are BLOCKED unless:
  1. The source URL is a verified GitHub release asset (`github.com/*/releases/*`)
  2. The content is first downloaded to `/tmp/`, inspected by the agent, then executed
  3. The user has explicitly approved the dependency in `dependency-allowlist.md`
```

**Commit:** `fix(security): Add project-local security rules — supersedes blocking global rule`

---

## STEP 2: AMENDMENT 07 — Pixeltable Knowledge Substrate

### 2a. Create `.claude/rules/anti-amnesia.md`

```markdown
# Anti-Amnesia Rule

Before writing ANY plan, skill, migration, or implementation code for a tool
integration, the agent MUST query Pixeltable's knowledge substrate first:

  search_tutorials(query_text, tool_name)
  search_research(query_text, tool_name)
  search_docs(query_text, tool_name)

If any query returns results above 0.7 → read them before writing code.
If ALL queries return below 0.7 → knowledge gap detected → trigger Capability
Harvest Protocol. Do NOT proceed with implementation.

Also call `search_docs` before writing any code that calls a tool API.
`search_api_reference` is the mandatory pre-flight for any implementation code.
```

### 2b. Create `pixeltable/migrations/0015_knowledge_substrate.py`

```python
# pixeltable/migrations/0015_knowledge_substrate.py
"""
Migration 0015 — lattice/knowledge/ substrate
Adds: tutorials, tutorial_sentences (view), research_docs, research_chunks (view), skills_registry
"""
import pixeltable as pxt
from pixeltable.functions import video, audio, string
from pixeltable.functions.huggingface import sentence_transformer
import pixeltable.functions.whisper as whisper
from pixeltable.iterators import DocumentSplitter
from pixeltable.migrations._helpers import ensure_namespace, ensure_table

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
_embed = sentence_transformer.using(model_id=EMBEDDING_MODEL)


def up():
    ensure_namespace("lattice")
    ensure_namespace("lattice/knowledge")

    tutorials = ensure_table(
        "lattice/knowledge/tutorials",
        {
            "url": pxt.String,
            "title": pxt.String,
            "tool_name": pxt.String,
            "source": pxt.String,
            "added_at": pxt.Timestamp,
            "video": pxt.Video,
        }
    )
    tutorials.add_computed_column(audio=video.extract_audio(tutorials.video, format="mp3"))
    tutorials.add_computed_column(transcript=whisper.transcribe(tutorials.audio, model="base.en"))

    tutorial_sentences = pxt.create_view(
        "lattice/knowledge/tutorial_sentences",
        tutorials,
        iterator=string.string_splitter.using(separators="sentence")(tutorials.transcript),
    )
    tutorial_sentences.add_embedding_index("text", embedding=_embed)

    research_docs = ensure_table(
        "lattice/knowledge/research_docs",
        {
            "path": pxt.String,
            "tool_name": pxt.String,
            "source_type": pxt.String,
            "added_at": pxt.Timestamp,
            "doc": pxt.Document,
        }
    )

    research_chunks = pxt.create_view(
        "lattice/knowledge/research_chunks",
        research_docs,
        iterator=DocumentSplitter.create(
            document=research_docs.doc,
            separators="token_limit",
            limit=512
        )
    )
    research_chunks.add_embedding_index("text", embedding=_embed)

    ensure_table(
        "lattice/knowledge/skills_registry",
        {
            "skill_name": pxt.String,
            "tool_name": pxt.String,
            "skill_md_path": pxt.String,
            "lineage_source": pxt.String,
            "content": pxt.String,
            "created_at": pxt.Timestamp,
        }
    )


def down():
    pxt.drop_table("lattice/knowledge/tutorial_sentences", force=True)
    pxt.drop_table("lattice/knowledge/research_chunks", force=True)
    pxt.drop_table("lattice/knowledge/research_docs", force=True)
    pxt.drop_table("lattice/knowledge/tutorials", force=True)
    pxt.drop_table("lattice/knowledge/skills_registry", force=True)
```

### 2c. Create Knowledge Tools

**`pixeltable/knowledge/__init__.py`** — empty file.

**`pixeltable/knowledge/tools.py`:**

```python
import pixeltable as pxt


@pxt.query
def search_tutorials(query_text: str, tool_name: str = None):
    ts = pxt.get_table("lattice/knowledge/tutorial_sentences")
    sim = ts.text.similarity(query_text)
    q = ts.select(ts.text, ts.tool_name, ts.title, similarity=sim)
    if tool_name:
        q = q.where(ts.tool_name == tool_name)
    return q.where(sim > 0.7).order_by(sim, asc=False).limit(10)


@pxt.query
def search_research(query_text: str, tool_name: str = None):
    rc = pxt.get_table("lattice/knowledge/research_chunks")
    sim = rc.text.similarity(query_text)
    q = rc.select(rc.text, rc.tool_name, rc.source_type, similarity=sim)
    if tool_name:
        q = q.where(rc.tool_name == tool_name)
    return q.where(sim > 0.7).order_by(sim, asc=False).limit(10)


@pxt.query
def get_skill_for_tool(tool_name: str):
    sr = pxt.get_table("lattice/knowledge/skills_registry")
    return (
        sr.select(sr.skill_name, sr.content, sr.skill_md_path)
        .where(sr.tool_name == tool_name)
        .order_by(sr.created_at, asc=False)
        .limit(5)
    )


KNOWLEDGE_TOOLS = pxt.tools(search_tutorials, search_research, get_skill_for_tool)
```

### 2d. Create Stub Scripts

**`scripts/ingest-tutorials.py`:**
```python
#!/usr/bin/env python3
"""Ingest tutorial videos into lattice/knowledge/tutorials. Tracks Issue #20."""
# TODO Issue #20: Implement tutorial ingestion pipeline
raise SystemExit(0)
```

**`scripts/ingest-research.py`:**
```python
#!/usr/bin/env python3
"""Ingest research documents into lattice/knowledge/research_docs. Tracks Issue #21."""
# TODO Issue #21: Implement research document ingestion pipeline
raise SystemExit(0)
```

### 2e. Documentation & Meta Updates

Create `meta/harness/PLAN/07-PIXELTABLE-SUBSTRATE-AMENDMENT.md` with these sections:
1. Binding Directive
2. Architecture Overview
3. Schema Reference (tutorials, tutorial_sentences, research_docs, research_chunks, skills_registry)
4. Agent Tool Catalog (search_tutorials, search_research, get_skill_for_tool, KNOWLEDGE_TOOLS)
5. Anti-Amnesia Rule (reference `.claude/rules/anti-amnesia.md`)
6. Migration 0015 Scope
7. Issues Added (#20 ingest-tutorials, #21 ingest-research, #22 skills-registry-populate)

Update `meta/harness/PLAN/00-OVERVIEW.md` — add Phase 0.7 row.
Update `meta/harness/PLAN/02-PLAN.md` — add `0015_knowledge_substrate.py` to Phase 2 migration list.
Update `meta/harness/PLAN/04-EXECUTION-HANDOFF.md` — add Issues #20, #21, #22.
Update `meta/harness/PLAN/06-CAPABILITY-HARVEST-AMENDMENT.md` — add "Pixeltable Integration" section.
Update `CLAUDE.md` LIVE STATE block, `meta/SCHEMA.md`, `meta/ARCHITECTURE.md`.

Run `scripts/pre-commit-docs-check.sh`.

**Commit:** `feat(harness): Phase 0.7 — Pixeltable knowledge substrate`

---

## STEP 3: AMENDMENT 08 — Docs Meta-Harness

### 3a. Create `pixeltable/migrations/0016_docs_substrate.py`

Schema requirements — implement `up()` and `down()`:

| Table | Columns |
|---|---|
| `lattice/knowledge/docs` | `path: pxt.String`, `tool_name: pxt.String`, `doc_category: pxt.String`, `mirror_id: pxt.String`, `added_at: pxt.Timestamp`, `doc: pxt.Document` |
| `lattice/knowledge/doc_chunks` | View of `docs` with `DocumentSplitter` (token_limit=512) + embedding index on `text` |
| `lattice/knowledge/doc_sync_log` | `mirror_id: pxt.String`, `synced_at: pxt.Timestamp`, `git_sha: pxt.String`, `file_count: pxt.Json`, `status: pxt.String` |
| `lattice/knowledge/doc_coverage_gaps` | `tool_name: pxt.String`, `gap_type: pxt.String`, `severity: pxt.String`, `description: pxt.String`, `detected_at: pxt.Timestamp`, `resolved: pxt.String` |

Use the same `ensure_namespace` / `ensure_table` helpers. Use same `_embed` embedding model.

### 3b. Update `pixeltable/knowledge/tools.py`

Add these `@pxt.query` stubs at the bottom (before `KNOWLEDGE_TOOLS`):

```python
@pxt.query
def search_docs(query_text: str, tool_name: str = None, doc_category: str = None):
    """Search API documentation chunks. Mandatory pre-flight before any tool API call."""
    dc = pxt.get_table("lattice/knowledge/doc_chunks")
    sim = dc.text.similarity(query_text)
    q = dc.select(dc.text, dc.tool_name, dc.doc_category, similarity=sim)
    if tool_name:
        q = q.where(dc.tool_name == tool_name)
    if doc_category:
        q = q.where(dc.doc_category == doc_category)
    return q.where(sim > 0.7).order_by(sim, asc=False).limit(10)


@pxt.query
def search_api_reference(query_text: str, tool_name: str):
    """Mandatory pre-flight for any implementation code. Searches API reference docs."""
    return search_docs(query_text, tool_name=tool_name, doc_category="api_reference")


@pxt.query
def get_coverage_gaps(tool_name: str = None, severity: str = None):
    """Return detected documentation coverage gaps."""
    cg = pxt.get_table("lattice/knowledge/doc_coverage_gaps")
    q = cg.select(cg.tool_name, cg.gap_type, cg.severity, cg.description, cg.detected_at)
    q = q.where(cg.resolved == "false")
    if tool_name:
        q = q.where(cg.tool_name == tool_name)
    if severity:
        q = q.where(cg.severity == severity)
    return q.order_by(cg.detected_at, asc=False).limit(50)
```

Update `KNOWLEDGE_TOOLS` to include the new functions:
```python
KNOWLEDGE_TOOLS = pxt.tools(
    search_tutorials, search_research, get_skill_for_tool,
    search_docs, search_api_reference, get_coverage_gaps
)
```

### 3c. Create `meta/harness/docs/` Scaffold

**`meta/harness/docs/GOAL.md`** — Define the 4 Gold Goals:
1. All doc mirrors synced within the last 7 days (measured by `doc_sync_log.synced_at`)
2. Zero critical coverage gaps in `doc_coverage_gaps` (severity = "critical", resolved = "false")
3. `score-docs.sh` CI run catches 100% of gaps present in `doc_coverage_gaps`
4. All `doc_chunks` rows have non-null embeddings (embedding index is fully populated)

**`meta/harness/docs/MEMORY.md`** — Detail the 7 planned doc mirrors and note that docs-meta is the 9th harness section:

| id | display_name | priority | doc_category |
|---|---|---|---|
| pixeltable | Pixeltable | critical | core_substrate |
| claude-code | Claude Code | critical | agent_runtime |
| infranodus | InfraNodus MCP Server | high | graph_analysis |
| graphify-parisgroup | Graphify | high | code_graph |
| gitnexus | GitNexus | high | code_graph |
| web-ifc | web-ifc | medium | ifc_runtime |
| deck-gl | deck.gl | medium | analytical_layer |

Note: Two additional mirrors (vectorworks, rhino-compute) are planned but not yet scheduled. Docs-meta harness is section 9 of the meta-harness.

**`meta/harness/docs/AGENT.md`** — AGORA 3-layer frontmatter:
```yaml
---
role: docs-sync-agent
description: |
  Keeps all doc mirrors fresh, detects coverage gaps, and populates
  lattice/knowledge/docs via ingest-docs.py after each sync.
triggers:
  - schedule: "0 9 * * 1"   # Weekly Monday 9am
  - event: post_tool_use     # After any tool-use that modifies .lattice-docs/
permissions:
  read:
    - ~/.lattice-docs/
    - ~/.claude-code-docs/
  write:
    - ~/.lattice-docs/
    - ~/.claude-code-docs/
    - ~/.gitnexus/
---
```
Body: describe the 3-step agent loop (sync → ingest → detect-gaps).

**`meta/harness/docs/gold_goals.md`** — YAML copy of the 4 Gold Goals from GOAL.md:
```yaml
gold_goals:
  - id: mirrors_fresh
    description: "All doc mirrors synced within last 7 days"
    metric: "MAX(doc_sync_log.synced_at) per mirror_id > NOW() - INTERVAL 7 DAYS"
    severity: critical
  - id: zero_critical_gaps
    description: "Zero critical coverage gaps unresolved"
    metric: "COUNT(*) FROM doc_coverage_gaps WHERE severity='critical' AND resolved='false' = 0"
    severity: critical
  - id: score_docs_catches_all
    description: "score-docs.sh CI run catches 100% of gaps"
    metric: "score-docs.sh exit code 0 iff zero_critical_gaps is true"
    severity: high
  - id: embeddings_complete
    description: "All doc_chunks have non-null embeddings"
    metric: "COUNT(*) FROM doc_chunks WHERE embedding IS NULL = 0"
    severity: high
```

**`meta/harness/docs/score-docs.sh`** — stub:
```bash
#!/usr/bin/env bash
# score-docs.sh — Score documentation coverage. Tracks Issue #23.
# TODO Issue #23: Implement doc coverage scoring logic
echo "[score-docs] stub — not yet implemented (Issue #23)"
exit 0
```

### 3d. Create `scripts/doc-mirror-manifest.yaml`

```yaml
# scripts/doc-mirror-manifest.yaml
# Full doc mirror manifest for LATTICE docs-meta-harness (Amendment 08)
mirrors:
  - id: pixeltable
    display_name: Pixeltable
    upstream_repo: github.com/pixeltable/pixeltable
    mirror_path: ~/.lattice-docs/pixeltable/
    clone_type: sparse
    sparse_paths: [docs/release/]
    llms_txt: https://docs.pixeltable.com/llms.txt
    sync_schedule: "0 9 * * 1"
    doc_category: core_substrate
    tool_name: pixeltable
    priority: critical

  - id: claude-code
    display_name: Claude Code
    upstream_source: https://code.claude.com/docs/en/llms.txt
    mirror_path: ~/.claude-code-docs/
    clone_type: llms_txt_scrape
    llms_txt: https://code.claude.com/docs/en/llms.txt
    sync_schedule: "0 9 * * 1"
    doc_category: agent_runtime
    tool_name: claude-code
    priority: critical

  - id: infranodus
    display_name: InfraNodus MCP Server
    upstream_repo: github.com/infranodus/mcp-server-infranodus
    mirror_path: ~/.lattice-docs/infranodus/
    clone_type: sparse
    sparse_paths: [docs/, README.md, CHANGELOG.md]
    sync_schedule: "0 9 * * 1"
    doc_category: graph_analysis
    tool_name: infranodus
    priority: high

  - id: graphify-parisgroup
    display_name: Graphify
    upstream_repo: github.com/parisgroup-ai/graphify
    mirror_path: ~/.lattice-docs/graphify-parisgroup/
    clone_type: sparse
    sparse_paths: [docs/, README.md, CHANGELOG.md]
    sync_schedule: "0 9 * * 1"
    doc_category: code_graph
    tool_name: graphify-parisgroup
    priority: high

  - id: gitnexus
    display_name: GitNexus
    upstream_repo: github.com/abhigyanpatwari/GitNexus
    mirror_path: ~/.lattice-docs/gitnexus/
    clone_type: sparse
    sparse_paths: [ARCHITECTURE.md, RUNBOOK.md, GUARDRAILS.md, CONTRIBUTING.md, README.md]
    sync_schedule: "0 9 * * 1"
    doc_category: code_graph
    tool_name: gitnexus
    priority: high

  - id: web-ifc
    display_name: web-ifc
    upstream_repo: github.com/IFCjs/web-ifc
    mirror_path: ~/.lattice-docs/web-ifc/
    clone_type: sparse
    sparse_paths: [docs/, README.md]
    sync_schedule: "0 9 * * 2"
    doc_category: ifc_runtime
    tool_name: web-ifc
    priority: medium

  - id: deck-gl
    display_name: deck.gl
    upstream_repo: github.com/visgl/deck.gl
    mirror_path: ~/.lattice-docs/deck-gl/
    clone_type: sparse
    sparse_paths: [docs/, README.md]
    sync_schedule: "0 9 * * 2"
    doc_category: analytical_layer
    tool_name: deck-gl
    priority: medium
```

### 3e. Create Script Stubs

**`scripts/sync-doc-mirrors.sh`** (Issue #24):
```bash
#!/usr/bin/env bash
# sync-doc-mirrors.sh — Sync all doc mirrors per doc-mirror-manifest.yaml. Tracks Issue #24.
echo "[sync-doc-mirrors] stub — not yet implemented (Issue #24)"
exit 0
```

**`scripts/ingest-docs.py`** (Issue #24):
```python
#!/usr/bin/env python3
"""Ingest synced doc mirror files into lattice/knowledge/docs. Tracks Issue #24."""
raise SystemExit(0)
```

**`scripts/detect-doc-gaps.py`** (Issue #25):
```python
#!/usr/bin/env python3
"""Detect documentation coverage gaps and write to lattice/knowledge/doc_coverage_gaps. Tracks Issue #25."""
raise SystemExit(0)
```

### 3f. Create `meta/harness/PLAN/08-DOCS-META-HARNESS-AMENDMENT.md`

Sections:
1. Binding Directive
2. Architecture Overview (7 mirrors, sync → ingest → detect loop)
3. Schema Reference (docs, doc_chunks, doc_sync_log, doc_coverage_gaps)
4. Agent Tool Catalog (search_docs, search_api_reference, get_coverage_gaps)
5. Doc Mirror Manifest (reference `scripts/doc-mirror-manifest.yaml`)
6. Gold Goals (reference `meta/harness/docs/gold_goals.md`)
7. CI Integration (Job 15: run score-docs.sh on PR)
8. Issues Added (#23 score-docs, #24 sync-and-ingest, #25 detect-gaps, #26 embeddings-audit)

### 3g. Meta Updates

Update `meta/harness/PLAN/00-OVERVIEW.md` — add Phase 0.8 row, update total section count to 9.
Update `meta/harness/PLAN/02-PLAN.md` — add migration 0016, docs scaffold, CI Job 15.
Update `meta/harness/PLAN/04-EXECUTION-HANDOFF.md` — add Issues #23–#26.
Update `CLAUDE.md`, `meta/SCHEMA.md`, `meta/ARCHITECTURE.md`, `meta/HANDOFF.md`.

Run `scripts/pre-commit-docs-check.sh`.

**Commit:** `feat(harness): Phase 0.8 — Docs Meta-Harness (9th section)`

---

## STEP 4: AMENDMENT 06 COMPLETION

### 4a. Create `.mcp.json` at repo root

```json
{
  "mcpServers": {
    "infranodus": {
      "command": "npx",
      "args": ["-y", "infranodus-mcp-server"],
      "env": {
        "INFRANODUS_API_KEY": "${INFRANODUS_API_KEY}"
      }
    }
  }
}
```

### 4b. Create `.claude/settings.json`

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "node node_modules/.bin/gitnexus detect-changes --pre-check 2>/dev/null || true"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "node node_modules/.bin/gitnexus index --incremental 2>/dev/null || true"
          }
        ]
      },
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "graphify check --silent 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

### 4c. Create Graphify Slash Commands in `.claude/commands/`

Create each file as a single-page Markdown with a `description:` frontmatter field and a `command:` field containing the shell command.

**`.claude/commands/gf-setup.md`:**
```markdown
---
description: "Initialize Graphify code graph analysis for the LATTICE repo"
command: "uv tool run graphify setup --root . --output .graphify/"
---
Run this once after cloning or after major structural refactors to build the initial Graphify code graph.
```

**`.claude/commands/gf-analyze.md`:**
```markdown
---
description: "Run a full Graphify code graph analysis and print summary"
command: "uv tool run graphify analyze --root . --format summary"
---
Outputs a dependency graph summary including dead code candidates, high-coupling nodes, and circular dependencies.
```

**`.claude/commands/gf-onboard.md`:**
```markdown
---
description: "Generate an onboarding walkthrough of the LATTICE codebase via Graphify"
command: "uv tool run graphify onboard --root . --entry pixeltable/ --output meta/onboarding-graph.md"
---
Produces a guided walkthrough document from the code graph, written to `meta/onboarding-graph.md`.
```

**`.claude/commands/gf-refactor-plan.md`:**
```markdown
---
description: "Generate a Graphify-based refactor plan for a specific module"
command: "uv tool run graphify refactor-plan --module ${MODULE:-pixeltable/} --output /tmp/refactor-plan.md && cat /tmp/refactor-plan.md"
---
Set `MODULE` env var to target a specific path. Defaults to `pixeltable/`. Prints the plan to stdout.
```

**`.claude/commands/gf-drift-check.md`:**
```markdown
---
description: "Check for code graph drift since last Graphify snapshot"
command: "uv tool run graphify diff --baseline .graphify/snapshot.json --current . --format diff"
---
Compares the current code graph against the last saved snapshot. Use after large commits to surface unexpected coupling or dead code introductions.
```

**Commit:** `feat(harness): Phase 0.6 completion — .mcp.json, hooks, slash commands`

---

## STEP 5: FINAL REGISTRY AUDIT

Run `ls analysis/capabilities/`. For each of the following registries that is **missing** (not just empty), create the stub file with the required headers and a `capabilities: []` placeholder:

- `analysis/capabilities/infranodus-capability-registry.yaml`
- `analysis/capabilities/graphify-parisgroup-capability-registry.yaml`
- `analysis/capabilities/gitnexus-capability-registry.yaml`
- `analysis/capabilities/graphify-safishamsi-capability-registry.yaml`
- `analysis/capabilities/pixeltable-capability-registry.yaml`
- `analysis/capabilities/claude-code-capability-registry.yaml`
- `analysis/capabilities/web-ifc-capability-registry.yaml`
- `analysis/capabilities/deck-gl-capability-registry.yaml`

Each stub must include these frontmatter headers:

```yaml
spec-verified: false
tool: <tool-name>
tool_version: null
canonical_docs: null
last_harvested: null
harvested_by: null
capabilities: []
```

**Commit:** `feat(harness): Capability registry stubs for all 8 doc mirror tools`

