---
title: "LATTICE Meta-Harness — Phase 2 Handoff (cold-start orientation)"
type: spec
status: reference
historical_only: false
source: "Phase 1 Closeout amendment §4 (committed 2026-05-12 against HEAD 299c6e7)"
---
# Phase 2 Handoff — Read This First

You are starting a new session with **zero conversation history**. This document is your only source of truth. Read it end to end before doing anything.

## 4.1 Read-this-first orientation (≤ 250 words)

**What is LATTICE?** AI-native AEC digital twin platform for landscape architecture. Pipeline: Vectorworks → IFC4.3 → iTwin (OSS self-hosted) → deck.gl analytical overlays + Cesium 3D Tiles (OSS self-hosted) → Pixeltable knowledge substrate. The pilot is MARPA — a real landscape-architecture firm using a real project.

**What is the meta-harness?** The substrate that lets AI agents safely modify LATTICE itself: a vendored + project-local skill genome at `/.claude/skills/`, polymorphic cellular division semantics for spawning section-scoped harnesses, a knowledge substrate in Pixeltable (`lattice/knowledge/*`), and a doctrine-rule layer enforcing the OSS-self-hosted stance and the five-gate dormancy policy for commercial-tier content.

**What phase are we in?** Phase 2 — polymorphic seeding + live verification — starting cold from `feature/meta-harness` HEAD `299c6e7`.

**What was Phase 1?** Substrate seeded but **inert**. 14-skill genome at root (12 mattpocock pinned to `9f2e0bd0…` + 2 project-local). Migrations 0001–0016 written but never applied to a live Pixeltable. `_gated/` subtree established for commercial content (Bentley + Cesium). OSS-self-hosted doctrine codified. Nothing has been bootstrapped on real hardware yet. See `meta/harness/docs/sessions/2026-05-12-phase-1-closeout-report.md` and `…-phase-1-health-audit.md` for the full picture.

**What is the immediate next step?** Phase B M3 Max bootstrap: `uv run python pixeltable/scripts/bootstrap.py` on Apple Silicon hardware. This is the first time any of the substrate scaffolding meets a real database + a real embedding model + real search-index construction.

## 4.2 Repo state at handoff

| Field | Value |
|---|---|
| Branch | `feature/meta-harness` |
| HEAD SHA | `299c6e7` (Phase 1.5 verification report) |
| Commits ahead of `main` | **20** (10 in Phase 1 range `2684be9..HEAD`; 10 pre-Phase-1 Amendments 0.6 / 0.7 / 0.8 / 06-completion / security on the branch) |
| PR | [#230](https://github.com/JeromyJSmith/lattice-platform/pull/230) — Draft, MERGEABLE, do **NOT** merge until Phase B passes |
| Open `meta-harness` label issues | **13** — `#231`-`#243` (full list in audit §2.8) |
| CI on HEAD | `docs-sync-check` ✅ · `CI` ✅ · `schema-verify` ✅ · `pixeltable-bridge` ❌ (Issue #227, known pre-existing, fixes when M3 Max runner comes online) |

## 4.3 The cardinal rules (binding, non-negotiable)

| Rule | Canonical home |
|---|---|
| No Revit / DGN / MicroStation — IFC4.3 only at boundary | `AGENTS.md` § cardinal rules |
| Pixeltable is the only database | `AGENTS.md` |
| iTwin OSS self-hosted only — commercial gated | `AGENTS.md` + `.claude/rules/oss-self-hosted-doctrine.md` |
| Cesium OSS self-hosted wherever possible — ion SaaS gated | `.claude/rules/oss-self-hosted-doctrine.md` |
| deck.gl analytical layer ONLY (never the 3D scene) | `AGENTS.md` |
| Plant Style Manager controls all VW instances | `AGENTS.md` |
| All coordinates EPSG-normalized before Pixeltable write | `AGENTS.md` |
| `uv` only for Python (never pip / conda / poetry) | `AGENTS.md` + global rule |
| Mac Apple Silicon first | `AGENTS.md` |
| Never import Anthropic SDK in client code | `AGENTS.md` + `CLAUDE.md` |
| Claude CLI (`claude -p`) is the agent backend | `AGENTS.md` |
| `pxt.Geometry` does **NOT** exist — use `pxt.String` (WKT) | `CLAUDE.md` |
| Migrations live in `pixeltable/migrations/` and are **write-once** | `CLAUDE.md` |
| `CLAUDE.md` = plain markdown, NO YAML frontmatter | `CLAUDE.md` |
| `SKILL.md` = YAML frontmatter REQUIRED, must be a directory | `.claude/skills/` convention |
| Capability Harvest Protocol mandatory before tool integration | `.claude/rules/capability-harvest-protocol.md` |
| Zero Dead DNA Rule | `.claude/rules/zero-dead-dna.md` |
| Always-Running CI/CD Health Loop | `.github/workflows/` (`docs-sync-check.yml`) |
| Anti-Amnesia Rule (search substrate before authoring) | `.claude/rules/anti-amnesia.md` |
| Embedding model: `intfloat/e5-large-v2` via `EMBEDDING_MODEL_ID` | `pixeltable/migrations/_helpers.py:22` |
| Five-gate dormancy policy for commercial content | `meta/harness/docs/research/_gated/README.md` |
| Pre-merge testing — nothing merges until end-to-end tested | PR #230 stays Draft |

## 4.4 The substrate map

```
lattice-platform/
├── .claude/
│   ├── skills/                                  ← 14-skill genome (write-protected root)
│   │   ├── cell-divide/                         ← reproductive function. INERT in Phase 1.
│   │   ├── propose-decomposition/               ← introspective function. INERT until Phase B verifies.
│   │   └── <12 mattpocock skills>/              ← pinned to mattpocock/skills@9f2e0bd0ea776eb6372eb81fa8a4a47814a8404a
│   │       (diagnose, grill-with-docs, handoff, improve-codebase-architecture,
│   │        prototype, setup-matt-pocock-skills, tdd, to-issues, to-prd,
│   │        triage, write-a-skill, zoom-out)
│   ├── rules/                                   ← 8 doctrine rule files
│   │   ├── anti-amnesia.md                      ← Phase 0.7
│   │   ├── capability-harvest-protocol.md       ← Phase 0.6
│   │   ├── dependency-allowlist.md              ← Phase 0.6 (mattpocock row in Phase 1)
│   │   ├── infranodus-corpus.md                 ← Phase 0.7
│   │   ├── lattice-security.md                  ← Amendment 09
│   │   ├── oss-self-hosted-doctrine.md          ← Phase 1.5  ★ binding for Phase 2
│   │   ├── vendored-skills.md                   ← Phase 1
│   │   └── zero-dead-dna.md                     ← Phase 0.6
│   ├── agents/                                  ← section harness AGENT files
│   ├── commands/                                ← 5 graphify-* slash commands (Phase 0.6 completion)
│   ├── settings.json                            ← project-scoped hooks
│   └── .mcp.json (repo root)                    ← InfraNodus + InfraNodus-skills + GitNexus
├── pixeltable/
│   ├── migrations/                              ← 0001-0016 (write-once)
│   │   ├── _helpers.py                          ← EMBEDDING_MODEL_ID = "intfloat/e5-large-v2"
│   │   ├── 0014_harness_schema.py
│   │   ├── 0015_knowledge_substrate.py          ← skills_registry, research_docs, tutorials
│   │   └── 0016_docs_substrate.py               ← docs corpus + api_reference
│   ├── service/                                 ← FastAPI sidecar + routes
│   └── scripts/
│       └── bootstrap.py                         ← Phase B target ★
├── meta/harness/
│   ├── PLAN/                                    ← amendment specs (00-OVERVIEW → 09-POLYMORPHIC)
│   │   └── 09-POLYMORPHIC-ARCHITECTURE-AMENDMENT.md  ★ read this
│   ├── docs/
│   │   ├── README.md                            ← navigation index (dual role: 9th-section files at top + historical subtree below)
│   │   ├── _INVENTORY.md                        ← every file's status, including gated content
│   │   ├── AGENT.md                             ← Docs Meta-Harness section agent (AGORA 3-layer, only fully-formed section AGENT.md)
│   │   ├── GOAL.md                              ← Docs Meta-Harness section fitness function
│   │   ├── MEMORY.md                            ← Docs Meta-Harness section memo
│   │   ├── gold_goals.md                        ← Docs Meta-Harness ratchet target
│   │   ├── score-docs.sh                        ← stub scorer (Issue #237)
│   │   ├── amendments/                          ← historical amendment prompts (status: shipped)
│   │   ├── specs/                               ← canonical specs (outreach-templates, amended-research-proposal, etc.)
│   │   ├── research/                            ← external research (MARPA trove imported in Phase 1 addendum)
│   │   │   └── _gated/                          ← ★ DORMANT commercial-tier content
│   │   │       ├── README.md                    ← five-gate dormancy policy (read before anything inside)
│   │   │       ├── bentley-commercial/          ← itwin-pricing, activate-program, partner-program, bdn-developer-access
│   │   │       └── cesium-commercial/           ← cesium-ion-paid-tiers (stub)
│   │   ├── sessions/                            ← session transcripts + verification reports
│   │   │   ├── 2026-05-12-phase-1-health-audit.md      ★ read this
│   │   │   └── 2026-05-12-phase-1-closeout-report.md   ★ read this
│   │   └── archive/                             ← superseded drafts (empty in Phase 1)
│   ├── sections/                                ← 8 section harnesses scaffolding-only + 9th (Docs) fully formed
│   │                                              (Phase 6 of execution will generate the missing 8)
│   └── HANDOFF-PHASE-2.md                       ← ★ THIS DOCUMENT
├── AGENTS.md                                    ← cardinal rules canonical home
├── CLAUDE.md                                    ← Claude Code conventions
└── ...
```

## 4.5 Phase 2 execution plan

### Step 1 — Read this document end to end, then read in order

1. `meta/harness/PLAN/09-POLYMORPHIC-ARCHITECTURE-AMENDMENT.md` — the polymorphic engine spec (write-protected root, cellular division semantics, lineage frontmatter, depth guard, default per-section skill policy)
2. `meta/harness/docs/sessions/2026-05-12-phase-1-health-audit.md` — the §2 audit from this amendment (substrate / skills / rules / docs / YAML / cross-refs / CI / GitHub)
3. `meta/harness/docs/sessions/2026-05-12-phase-1-closeout-report.md` — the §3 closeout from this amendment (commits / decisions / what's working / what's pending / risks)
4. `meta/harness/docs/research/_gated/README.md` — the five-gate dormancy policy (forbidden vs. permitted use of gated content; activation procedure)
5. `.claude/rules/vendored-skills.md` and `.claude/rules/oss-self-hosted-doctrine.md` — the two Phase-1-introduced doctrine rules
6. `AGENTS.md` and `CLAUDE.md` — cardinal rules + Claude Code conventions

### Step 2 — Phase B M3 Max bootstrap

Human runs on Apple Silicon hardware (Mac with M-series CPU + ≥32 GB unified memory; M3 Max + 128 GB is the verified target):

```bash
cd lattice-platform
uv run python pixeltable/scripts/bootstrap.py
```

**Expected:**
- Pixeltable tables created from migrations 0001–0016 (no `pxt.Geometry` usage; all geometry as `pxt.String` WKT)
- `intfloat/e5-large-v2` embedding model downloaded + cached (~1.3 GB)
- Knowledge-substrate tables populated to schema-ready state (rows arrive via Issues #234/#235/#236)
- Hugging Face / sentence-transformers initialization clean

**Failure modes to expect on first run** (per audit §3.7 HIGH-severity risks):
- Migration-chain ordering issues if any FK / namespace dependency is implicit
- Embedding-model loading OOM on memory-constrained hardware
- Search-index dim mismatch if any vector column wasn't created with the right dimension

**Write all results to:** `meta/harness/docs/sessions/<YYYY-MM-DD>-phase-2-bootstrap-verification.md`. Commit + push, do NOT merge.

### Step 3 — Verify the substrate query tools come online

After Step 2 succeeds, smoke-test the substrate query layer:

```python
# Pseudo — actual invocation depends on how Phase 2 wires Pixeltable's @pxt.query tools
search_tutorials("polymorphic skill cellular division")
search_research("OSS self-hosted Bentley")
search_docs("Pixeltable migrations apply pattern")
search_api_reference("pxt.create_dir owned-parents rule")
get_coverage_gaps()
```

Each should return ≥ 1 hit on the corpora populated during Step 2 (or correctly return "empty" if Issues #234/#235/#236 haven't run yet — that is acceptable for a substrate-shape-only verification).

Then run a small Graphify dep-graph and InfraNodus topic analysis on a constrained codebase region (e.g., `pixeltable/migrations/` only) to confirm those tools are wired.

### Step 4 — Verify `skills_registry.lineage_source` accepts writes

Before any `cell-divide` execution, write a **dummy row** to `lattice/knowledge/skills_registry` with `lineage_source = "phase-2-smoke-test"`, then immediately delete it. Confirms:

- The migration 0015 schema is applied
- The `lineage_source` column accepts a `pxt.String` value
- The insert + delete round-trip is clean

Document the dummy SQL / Python in the bootstrap verification report.

### Step 5 — `propose-decomposition` first run

Only after Steps 2–4 are green:

1. Flip `disable-model-invocation: true` → `false` in `.claude/skills/propose-decomposition/SKILL.md`. **Commit this as a separate, single-purpose commit** so it can be reverted independently if the first run misbehaves.
2. Invoke the skill. Its body specifies the substrate-query pass, structural pass (Graphify), semantic pass (InfraNodus), and synthesis step.
3. Output lands at `meta/harness/PLAN/proposals/<YYYY-MM-DD>-decomposition.md`. Do NOT commit the proposal file automatically — wait for human review.
4. Human reviews the proposal. **Only with human approval** does `cell-divide` execute on the proposed targets.
5. After the first division: re-run the audit script (`meta/harness/docs/sessions/2026-05-12-phase-1-health-audit.md` is the template) and confirm the new cell carries correct `lineage:` frontmatter + a row in `skills_registry` with the correct `lineage_source`.

### Hard stops carried into Phase 2

- Do **NOT** merge PR #230 until Phase B (Steps 2–4) passes end-to-end
- Do **NOT** invoke `cell-divide` until `propose-decomposition` has run and a human has approved its proposal
- Do **NOT** edit any landed migration (0001–0016 are write-once)
- Do **NOT** install any dependency not in `.claude/rules/dependency-allowlist.md` without appending a new row + opening a PR
- Do **NOT** modify content under `meta/harness/docs/research/_gated/<vendor>/` for architectural purposes — that subtree is dormant; the only permitted use is drafting outreach (per `_gated/README.md`)
- Do **NOT** add a Cesium ion API key against the hosted SaaS endpoint in default architecture — self-host the equivalent capability per `.claude/rules/oss-self-hosted-doctrine.md`

## Quick links

- Branch: `feature/meta-harness`
- PR: <https://github.com/JeromyJSmith/lattice-platform/pull/230>
- Phase 1 health audit: [`meta/harness/docs/sessions/2026-05-12-phase-1-health-audit.md`](docs/sessions/2026-05-12-phase-1-health-audit.md)
- Phase 1 closeout report: [`meta/harness/docs/sessions/2026-05-12-phase-1-closeout-report.md`](docs/sessions/2026-05-12-phase-1-closeout-report.md)
- Polymorphic architecture spec: [`meta/harness/PLAN/09-POLYMORPHIC-ARCHITECTURE-AMENDMENT.md`](PLAN/09-POLYMORPHIC-ARCHITECTURE-AMENDMENT.md)
- Gated content policy: [`meta/harness/docs/research/_gated/README.md`](docs/research/_gated/README.md)
- OSS-self-hosted doctrine: [`.claude/rules/oss-self-hosted-doctrine.md`](../../.claude/rules/oss-self-hosted-doctrine.md)
- Vendored-skills rule: [`.claude/rules/vendored-skills.md`](../../.claude/rules/vendored-skills.md)
- Cardinal rules: [`AGENTS.md`](../../AGENTS.md)

---

End of Phase 2 handoff. The next session reads this, then reads the six docs listed in Step 1, then runs Phase B. Nothing else happens before Step 1 completes.
