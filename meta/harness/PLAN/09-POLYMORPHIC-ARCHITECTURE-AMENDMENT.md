<!-- spec-verified: code.claude.com/docs 2026-05-11 -->
# Phase 1 — Polymorphic Architecture Amendment

**Status:** binding. Lands the skill genome seed + the cellular-division architecture for the LATTICE Meta-Harness organism.

## Why this exists

The LATTICE Meta-Harness is not a single fixed agent. It is an **organism** — a tree of section harnesses, each with its own context stack (`CLAUDE.md` + `AGENTS.md` + `MEMORY.md` + `GOAL.md`) and its own copy of the shared skill genome. As sections specialize, their skills can mutate locally; promotions back to ancestors are explicit. This is the polymorphic architecture.

## The Genome

A single source-of-truth tree at `/.claude/skills/` (repo root). Every skill here is **mandatory for every section harness** unless explicitly opted out. The genome is **write-protected** — direct mutation requires a Product Requirements Doc (`meta/harness/PLAN/proposals/<timestamp>-prd-root-genome-<reason>.md`) and a human review.

### Seed contents (14 skills, as of Phase 1)

| Skill | Source | Purpose |
|---|---|---|
| `setup-matt-pocock-skills` | mattpocock | Bootstrap helper for the skill workflow |
| `grill-with-docs` | mattpocock | Doc-grounded clarifying-question generator |
| `to-prd` | mattpocock | Promote a desire into a PRD |
| `to-issues` | mattpocock | Decompose a PRD into GitHub issues |
| `triage` | mattpocock | Issue / incident triage workflow |
| `tdd` | mattpocock | Red-green-refactor TDD loop |
| `diagnose` | mattpocock | Root-cause analysis |
| `prototype` | mattpocock | Disposable prototype lifecycle |
| `improve-codebase-architecture` | mattpocock | Structural refactor proposals |
| `zoom-out` | mattpocock | Anti-rabbit-hole re-framing |
| `handoff` | mattpocock | Inter-session / inter-agent handoff |
| `write-a-skill` | mattpocock | Author new skills (meta-skill) |
| `cell-divide` | lattice-internal | Reproductive function — copies genome into a child cell |
| `propose-decomposition` | lattice-internal | Introspective function — suggests where to divide next |

All 12 mattpocock skills are **plain-copy vendored** (not a submodule, not `npx skills@latest add ...`) and pinned to upstream commit `9f2e0bd0ea776eb6372eb81fa8a4a47814a8404a`. Source provenance is captured in each `SKILL.md`'s `source:` frontmatter field per `.claude/rules/vendored-skills.md`.

## Cellular Division Semantics

The genome reproduces via the `cell-divide` skill. Division is always a **plain copy with lineage append** — never a fork, never a rebase.

### Direction of reproduction

```
/.claude/skills/                                          ← ROOT GENOME (write-protected)
    │
    │  cell-divide(target=meta/harness/sections/schema/.claude/skills/,
    │              parent_commit_sha=<root-commit>,
    │              section=schema)
    ▼
meta/harness/sections/schema/.claude/skills/              ← SECTION CELL (free to mutate)
    │
    │  cell-divide(target=meta/harness/sections/schema/sub/.claude/skills/,
    │              parent_commit_sha=<section-cell-commit>,
    │              section=schema-sub)
    ▼
meta/harness/sections/schema/sub/.claude/skills/          ← SECTION-OF-SECTION CELL
```

Each invocation copies *exactly one level*. To go deeper, the human re-invokes after reviewing the previous level's health snapshot.

### Per-cell mutation freedom

After division, each cell may mutate its skills freely:
- Body changes go into the SKILL.md.
- Every change appends an entry to `local_adaptations:` in the frontmatter — one line per adaptation, with the date and a one-line rationale.
- The cell's section harness owns its cell. The root genome remains untouched by cell-level mutations.

### Lineage frontmatter

```yaml
lineage:
  - <commit-sha-where-this-cell-was-divided-from-its-parent>
  - <commit-sha-where-the-PARENT-cell-was-divided-from-its-grandparent>
  - <commit-sha-of-root-genome-introduction>
```

Order: **youngest ancestor first → oldest last**. Walking the list bottom-up gives the full reproductive history of a leaf cell's SKILL.md back to root.

Lineage also lives in `lattice/knowledge/skills_registry.lineage_source` (one row per skill per cell). The on-disk frontmatter is the primary source; the substrate row is the queryable index. The two must agree — `audit-dead-dna.sh` (Issue #17 → #232) will eventually enforce this.

### Promotion path

A mutation in a leaf cell may be promoted to **any named ancestor** in its lineage, not just root. Promotion is a separate workflow (out of scope for this amendment) but the design supports it:

1. The promoting agent picks an ancestor SHA in the leaf cell's `lineage:` list.
2. The mutation diff is applied to that ancestor's SKILL.md.
3. The ancestor's `local_adaptations:` gains an entry recording the promotion (source leaf, date, rationale).
4. All descendant cells of that ancestor receive the change in their *next* `cell-divide` (or via an explicit refresh — also out of scope for this amendment).

### Depth guard

`propose-decomposition` will not propose more than **3 new levels of nesting per cycle**. Deeper recursion requires a follow-up cycle after the previous level is verified healthy (composite section score above plateau threshold in `meta/harness/sections/<section>/GOAL.md`).

### Organism-authored decomposition with human gate

After Phase B completes (live execution + bootstrap verification on the M3 Max), the organism's **first autonomous act** is to run `propose-decomposition`. The output is a markdown proposal at `meta/harness/PLAN/proposals/<timestamp>-decomposition.md`. **Nothing divides without explicit human approval of that proposal.**

## Persistence

| Layer | What it holds | Update on |
|---|---|---|
| On-disk frontmatter (`SKILL.md`'s `lineage:` + `local_adaptations:`) | Primary record of provenance | Every `cell-divide` and every cell-level mutation |
| `lattice/knowledge/skills_registry` (migration 0015) | Queryable index — `lineage_source`, `committed_path`, `content`, `created_at` | Every `cell-divide` (one row per skill copied) |
| `audit-dead-dna.sh` (Issue #232) | Will cross-check disk ↔ substrate consistency | Every CI run once Issue #232 lands |

## Hard constraints in this amendment (Phase 1)

- The `cell-divide` and `propose-decomposition` skills are **on disk but inert**. They do not run in Phase 1.
- Root genome is **write-protected**: direct edits require a PRD + human review.
- The 12 vendored skills' `source:` and `vendored_at:` fields are **immutable after vendor** (they capture the upstream provenance; replace by re-vendoring at a new pinned SHA, never by editing in place).
- `npx skills@latest add mattpocock/skills` is **banned** for this project per `.claude/rules/vendored-skills.md`. Vendoring is always plain-copy from a pinned `git clone`.

## Cross-references

- `.claude/rules/vendored-skills.md` — vendor strategy + adaptation registry
- `.claude/rules/dependency-allowlist.md` — mattpocock pinned-SHA row
- `.claude/skills/cell-divide/SKILL.md` — reproductive function (inert)
- `.claude/skills/propose-decomposition/SKILL.md` — introspective function (inert)
- `pixeltable/migrations/0015_knowledge_substrate.py` — `lattice/knowledge/skills_registry` schema
- Section AGENT.md files in `meta/harness/sections/*/AGENT.md` — declare which of the 14 skills are mandatory per section

## §2.5 — Default per-section skill policy

This table is the authoritative source for every section AGENT.md `skills:` block. The docs-harness AGENT.md (the only section AGENT.md that exists today) has already been updated to match. The other 8 section AGENT.md files will be generated during Phase 6 of execution using this table as their template.

| Skill | Default mandatory? | Rationale |
|---|---|---|
| `to-prd` | **mandatory** | Every section turns desires into PRDs before code lands. |
| `to-issues` | **mandatory** | PRD → GitHub issues is the universal decomposition step. |
| `tdd` | **mandatory** | Red-green-refactor applies to every new code path. |
| `diagnose` | **mandatory** | Root-cause analysis is required before any incident close-out. |
| `triage` | **mandatory** | Incident / issue prioritization is universal. |
| `handoff` | **mandatory** | Every section writes its `MEMORY.md` at session end via this skill. |
| `setup-matt-pocock-skills` | optional | Bootstrap helper; needed once at section onboarding. |
| `grill-with-docs` | optional | Useful for sections with heavy doc surface (docs, schema, api). |
| `prototype` | optional | Useful for sections with frequent disposable experiments (frontend, genai). |
| `improve-codebase-architecture` | optional | Useful for refactor-heavy sections (schema, api, vw-itwin). |
| `zoom-out` | optional | Useful when a section's autoresearch loop plateaus in narrow optimum. |
| `write-a-skill` | optional | Used only when the section authors new skills (gated by root-genome write-protection). |
| `cell-divide` | optional (INERT in Phase 1) | Reproductive function. Inert until Phase B. |
| `propose-decomposition` | optional (INERT in Phase 1) | Introspective function. Inert until Phase B. |

### Per-section overrides

A section MAY upgrade an optional skill to mandatory in its own AGENT.md frontmatter, but MUST NOT downgrade a default-mandatory skill to optional without an explicit override note in the section's `gold_goals.md` (`Required guardrails` block).

### Phase 6 execution checklist

When Phase 6 generates the 8 missing section AGENT.md files (schema, api, frontend, georef-reality, genai, vw-itwin, ddc-infra, ci/infra), each one must:

1. Copy the AGORA-3-layer frontmatter shape from `meta/harness/docs/AGENT.md`.
2. Adopt the `skills:` block from this table verbatim (the 6 mandatory + 8 optional split).
3. Add section-specific upgrades to the optional set with a one-line rationale comment.
4. Update its own `MEMORY.md` `Open Decisions` to note any skill it deferred or overrode.
