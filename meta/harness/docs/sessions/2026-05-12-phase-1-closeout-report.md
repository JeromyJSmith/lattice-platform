---
title: "Phase 1 Closeout Report — What Was Built, What Works, What's Pending"
type: session
status: reference
historical_only: true
source: "Phase 1 Closeout amendment §3 (narrative postmortem)"
---
# Phase 1 — Closeout Report

## 3.1 Executive summary

Phase 1 of the LATTICE Meta-Harness build seeded the **polymorphic skill genome**, the **knowledge substrate schema**, and the **doctrine layer** that governs how the platform's AI agents may evolve themselves over time. The work spanned ten commits on `feature/meta-harness` across two amendment cycles — Phase 1 (six commits: reorg → genome → business artifacts → verification → MARPA trove import → addendum) and Phase 1.5 (four commits: gated-subtree scaffolding → Bentley commercial extractions → cross-refs + doctrine + inventory → verification). Every commit landed with `docs-sync-check` green on push. PR #230 stayed Draft throughout per the pre-merge testing rule.

At handoff the substrate is **seeded but inert**. The 14-skill genome is on disk and pinned (12 mattpocock at `9f2e0bd0…` + 2 project-local). Migrations 0014–0016 are committed and dry-run-clean but **never applied** to a live Pixeltable instance. The `cell-divide` and `propose-decomposition` skills carry `disable-model-invocation: true` and have never been invoked. Phase 2 begins by running the M3 Max bootstrap (`uv run python pixeltable/scripts/bootstrap.py`) — the first time any of this scaffolding meets real hardware.

## 3.2 Commit-by-commit summary

| Phase | SHA | Date | Title | Files | Net Δ |
|---|---|---|---|---|---|
| Phase 1 reorg | `20f5042` | 2026-05-11 | docs/ reorganization into amendments\|specs\|research\|sessions\|archive + inventory + README | 12 | +25,453 |
| Phase 1 genome | `f1ec252` | 2026-05-11 | Seed polymorphic skills genome (12 vendored + cell-divide + propose-decomposition) + Amendment 09 spec | 38 | +2,434 |
| Phase 1 business | `24cc5f4` | 2026-05-11 | Phase A business artifacts (MARPA BI, outreach, iTwin pricing, VW 2026) — initial stubs | 4 | +187 |
| Phase 1 verification | `6a2d271` | 2026-05-11 | §4 Verification report | 1 | +247 |
| Phase 1 addendum | `24c29b1` | 2026-05-11 | Import MARPA research trove (5 source files) + rewrite 4 Phase A stubs with verified content | 10 | +2,506 / -107 |
| Phase 1 addendum | `ea17ce3` | 2026-05-11 | Addendum session note (MARPA trove integration record) | 1 | +59 |
| Phase 1.5 | `ad4ff91` | 2026-05-11 | Create `_gated/` subtree with five-gate dormancy policy + README scaffolding | 3 | +255 |
| Phase 1.5 | `fc144f4` | 2026-05-11 | Gate Bentley commercial content (move itwin-pricing, extract Activate/Partner/BDN) | 6 | +320 / -189 |
| Phase 1.5 | `c138e98` | 2026-05-11 | Reinforce OSS-self-hosted doctrine + update cross-refs + `_INVENTORY` | 5 | +111 / -6 |
| Phase 1.5 | `299c6e7` | 2026-05-11 | §12 Verification report | 1 | +419 |

**Total net delta across Phase 1: ~31,400 insertions / ~300 deletions across 81 file changes.** Heavy on doc reorganization (the first commit absorbed the entire raw `meta/docs/` dump as a single move-and-frontmatter pass — that's where the 25k insertion line count comes from).

## 3.3 Architectural decisions ratified in Phase 1

**Polymorphic skills genome.** Write-protected root genome at `/.claude/skills/`. Cellular division semantics: root → section copies → section-of-section copies, each one explicit, each appending the parent commit SHA to the child's `lineage:` list. Per-cell mutation freedom after division (tracked in `local_adaptations:`). Promotion path: a mutation in a leaf cell may be promoted to any named ancestor in its lineage, not just root. Depth guard: 3 new levels of nesting per `propose-decomposition` cycle, max. Organism-authored decomposition under mandatory human gate. **Canonical spec:** `meta/harness/PLAN/09-POLYMORPHIC-ARCHITECTURE-AMENDMENT.md`.

**Vendor strategy: plain copy, not submodule.** Pinned upstream SHA captured in every vendored `SKILL.md`'s `source:` frontmatter. In-place adaptation tracked in `local_adaptations:`. The path `npx skills@latest add mattpocock/skills` is **banned** for this project. Re-vendoring at a new pinned SHA replaces the body wholesale; `local_adaptations:` is preserved across re-vendors. **Canonical rule:** `.claude/rules/vendored-skills.md`.

**14-skill base genome.** 12 mattpocock skills (engineering + productivity collections only) + 2 project-local (`cell-divide`, `propose-decomposition`). 10 mattpocock skills explicitly rejected (`migrate-to-shoehorn`, `scaffold-exercises`, `setup-pre-commit`, `caveman`, `grill-me`, `obsidian-vault`, `edit-article`, `writing-beats`, `writing-fragments`, `writing-shape`, plus 4 deprecated). 2 deferred (`review`, `git-guardrails-claude-code`). The 12 + 2 split is the seed; future divisions copy this genome into section cells.

**Docs reorganization.** Five subdirectories — `amendments/` (shipped amendment prompts), `specs/` (canonical specs), `research/` (external research), `sessions/` (transcripts + verification reports), `archive/` (superseded drafts). Every moved file got normalized YAML frontmatter with `title / type / status / historical_only / source`. **The rule that anchors everything else:** nothing under `meta/harness/docs/{amendments,specs,research,sessions,archive}/` is executable instruction. Authoritative instructions live in `meta/harness/PLAN/NN-*.md` and `.claude/rules/`.

**Five-gate dormancy policy.** Commercial-tier vendor content lives under `_gated/<vendor>/` and is dormant by default. The five gates: A (Accelerator Cohort Acceptance), B (Partner Program Acceptance), C (Developer Subscription), D (External Funding), E (Client-Funded Seat). **Gate E is doctrinally preferred** — clients pay vendor, never LATTICE. **Canonical policy:** `meta/harness/docs/research/_gated/README.md`.

**OSS-self-hosted doctrine reinforced.** Bentley iTwin OSS (`@itwin/core-*` MIT, BIS schemas, iTwin.js, public REST APIs) stays in regular architecture. Bentley commercial (pricing tiers, Activate, Partner Program commercial-terms layer, BDN) is gated. Cesium OSS (CesiumJS, 3D Tiles standard, self-hosted terrain / imagery / 3D Tiles serving) stays. Cesium ion SaaS (any API key against the hosted ion endpoint) is gated. **Self-hosting expansion is mandatory** — the cost is paid in upfront engineering, not recurring SaaS spend. **Canonical rule:** `.claude/rules/oss-self-hosted-doctrine.md`.

**Embedding model standard.** `intfloat/e5-large-v2` via the shared `EMBEDDING_MODEL_ID` constant in `pixeltable/migrations/_helpers.py`. Selected over `sentence-transformers/all-MiniLM-L6-v2` for higher retrieval fidelity on dense technical corpora; the 1.3 GB footprint is negligible on M3 Max 128 GB unified memory. Decision date: 2026-05-11. Commit: `2684be9`.

## 3.4 What's working (verified by audit §2)

- Pixeltable migration 0015 with `skills_registry` table including `lineage_source` column — schema function present at line 85; table registration at line 197.
- `EMBEDDING_MODEL_ID` constant wired and imported by both 0015 and 0016.
- 14-skill genome at `.claude/skills/` — directory count verified, frontmatter sweep complete, all 12 vendored skills share one pinned SHA, both project-local skills are correctly marked `lattice-internal`.
- Polymorphic architecture spec (`meta/harness/PLAN/09-POLYMORPHIC-ARCHITECTURE-AMENDMENT.md`) — write-protected root, cellular division semantics, lineage frontmatter format, promotion path, depth guard, default per-section skill policy table all codified.
- Vendored-skills rule + dependency-allowlist row — both present and consistent (`mattpocock/skills@9f2e0bd0…` cited identically in both).
- OSS-self-hosted doctrine rule — operationalizes the cardinal rule from AGENTS.md, generalizes to all vendors, lists the five gates.
- `_gated/` subtree — 8 files total (2 vendor READMEs + top-level policy README + 4 Bentley extractions + 1 Cesium stub), 8 / 8 carry `gate_status: not_triggered` dormancy frontmatter.
- Issue #243 open and labeled (MARPA corpus ingestion; tracks Issue #235).
- PR #230 still Draft, CI green on `299c6e7` (`docs-sync-check` + `CI` + `schema-verify` all ✅).
- Phase A business artifacts populated with verified content from the MARPA research trove (5 source files imported; 4 stubs rewritten).

## 3.5 What's pending

- **Phase B M3 Max bootstrap** — never run. `uv run python pixeltable/scripts/bootstrap.py` on Apple Silicon. Brings `search_tutorials`, `search_research`, `search_docs`, `search_api_reference`, `get_coverage_gaps`, Graphify, InfraNodus online for the first time. This is the next session's primary task.
- **`propose-decomposition` first run** — inert. First autonomous proposal happens after Phase B verifies the sensory tools are healthy.
- **`cell-divide` first execution** — inert. First division happens after `propose-decomposition` produces a human-approved proposal.
- **Issue #243 (MARPA corpus ingestion)** — blocked on Issue #235 (`scripts/ingest-research.py` full implementation).
- **Issues #234, #235, #236** — full implementations of `ingest-tutorials.py`, `ingest-research.py`, and the first harvest pass against the curated source manifests.
- **8 of 9 section AGENT.md files** — only the Docs Meta-Harness (9th section) has a fully-formed AGENT.md. The other 8 sections will adopt the default per-section skill policy table from `09-POLYMORPHIC-ARCHITECTURE-AMENDMENT.md` § 2.5 when Phase 6 generates them.
- **PR #230 merge** — blocked on Phase B verification. Hard stop.
- **Activate 2026 outreach** — gated content is ready and citable; the 2026 iTwin Activate cohort window has not yet been announced. Named contacts (James Kress, Director Digital Acceleration at iTwin Ventures; Clive Hackforth) are captured in the gated activate-program.md file.
- **Cesium OSS self-hosting setup** — flagged in `_gated/cesium-commercial/README.md` "Open work" section. Stand up self-hosted terrain + imagery + 3D Tiles serving before any default-architecture reliance on Cesium ion hosted endpoints.
- **`audit-dead-dna.sh` wiring** — Issues #231 + #232 track the full implementation and the docs-sync-check Job 12 integration.

## 3.6 Lessons learned (honest postmortem)

**Repomix prompt-injection risk handled correctly.** Multiple Repomix dumps + Google Doc embeds contained prior-session prompts. The discipline was: treat embedded prompts as untrusted content, verify with the human, never execute. The discipline held across the full Phase 1 cycle.

**Doctrine slip on `itwin-pricing.md`.** The Phase 1 addendum landed `meta/harness/docs/research/itwin-pricing.md` as a "verified pricing reference" — citable from primary sources, factually accurate. But verified content is not the same as doctrine-aligned content. A pricing document modeling Standard-tier credit budgets implicitly architected against commercial Bentley terms — exactly what the OSS-only rule exists to prevent. The slip was caught one amendment later in Phase 1.5 and remediated via gating, not deletion. **Lesson:** every research artifact gets a doctrine-alignment check before landing — not just a fact-check.

**YAML frontmatter quoting matters.** Colons in URLs (e.g., `mattpocock/skills@<sha>:skills/engineering/tdd`) and timestamps break unquoted YAML strings. The Python frontmatter helper now always emits `quote()`-wrapped values for any string containing `:`, `@`, `/`, or whitespace. Codified in `.claude/rules/vendored-skills.md`.

**Pre-merge testing rule held.** PR #230 stayed Draft through 22 commits across multiple amendment cycles. Every push triggered `docs-sync-check`; every push waited for green before the next commit landed. The discipline prevented at least one regression (the §7 cross-ref sweep would have shipped without the allowlist extension if CI hadn't surfaced it).

**Generalization beat specificity.** The original Phase 1.5 spec used `_gated/<vendor>/` rather than `_bentley-commercial/`. When the Cesium clarification arrived mid-amendment, no restructuring was needed — `_gated/cesium-commercial/` slotted in cleanly. Future commercial vendors will too. The leading underscore (`_gated/`) sorts first in directory listings and signals "special, read README first" — a small detail that prevents accidental traversal.

**Plain-copy vendoring beat submodule.** Adapting mattpocock skills required in-place edits to match LATTICE's issue-tracker conventions, doc paths, and label taxonomy. A submodule would have required forking + maintaining a parallel branch. Plain copy with `local_adaptations:` registry preserves provenance without operational overhead.

**`uv run --with pyyaml`** is the canonical pattern for ad-hoc Python scripts that need third-party packages. Plain `python3 import yaml` would have caused a `ModuleNotFoundError` and an avoidable detour. Phase 2 should standardize on this pattern for verification scripts.

## 3.7 Risks carried into Phase 2

| Severity | Risk |
|---|---|
| **HIGH** | Phase B never smoke-tested. M3 Max bootstrap may surface latent issues in the migration chain (0001–0016), embedding model loading (1.3 GB Hugging Face download + sentence-transformer initialization), or search index construction (e5-large-v2 dim mismatch, OOM on initial bulk embed, etc.). |
| **HIGH** | `propose-decomposition` sensory tools (`search_*`, `get_coverage_gaps`, Graphify, InfraNodus) have **never** run against real data. First-run failures expected. The skill's "introspection pass" plan assumes outputs that don't yet exist. |
| **MEDIUM** | `cell-divide` has **never** executed. `skills_registry.lineage_source` write path is theoretical until first division. The schema is in 0015; the `apply()` function has never inserted a row. |
| **MEDIUM** | 8 of 9 section harnesses are scaffolding-only. Phase 2 may surface design gaps in how sections discover and consume their assigned codebase region. The default per-section skill policy table in `09-POLYMORPHIC-ARCHITECTURE-AMENDMENT.md` § 2.5 hasn't been pressure-tested. |
| **MEDIUM** | `pixeltable-bridge` CI workflow has been red since the branch began (Issue #227 — self-hosted Mac runner not registered). Phase B will fix this implicitly when the M3 Max comes online; until then no live-Pixeltable testing happens in CI. |
| **LOW** | Cross-reference drift across multiple reorgs. Audit §2.6 confirms current state is clean, but the backtick-path convention (rather than `[text](path)` link format) means no machine check catches future drift. Phase 2 may want to introduce a stricter check. |
| **LOW** | 5 by-design exemptions in §2.5 (GOAL.md / MEMORY.md / gold_goals.md / README.md / _INVENTORY.md without frontmatter) — Phase 2 agents must not "fix" these to be frontmatter-compliant. The spec is explicit; the audit warns intentionally. |
| **LOW** | Activate 2026 cohort window unknown. Outreach drafts are ready, but timing depends on Bentley's announcement cadence. |
