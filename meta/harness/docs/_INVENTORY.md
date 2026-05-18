# `meta/harness/docs/` Inventory — 2026-05-11

Output of the §1.1 inventory pass from Phase 1 Amendment (09-Polymorphic-Genome). All files previously dumped in `meta/docs/` and `meta/vw-itwin-bridge-meta-repomix.xml` have been **moved** (no deletions) into the canonical subfolders below. Authoritative instructions live in `meta/harness/PLAN/NN-*.md`, NOT here — this whole tree is **historical reference only**.

## Manifest

| Original filename | Original size | Detected type | New location | Status | Rationale |
|---|---|---|---|---|---|
| `meta/docs/lattice-meta-harness-0.6-0.9-claude-code-prompt.md` | 25 KB | Amendment prompt (the doc this reorg amendment came from) | `amendments/09-polymorphic-genome-amendment-prompt.md` | keep | Source-of-truth for the Phase 1 reorg + skills-genome amendment. Frontmatter `status: shipped` (will be marked with the commit SHA once landed). |
| `meta/docs/Meta-Harness-Specification.txt` | 180 KB | Canonical spec (compressed session summary) | `specs/meta-harness-specification.md` | keep | Authoritative compression of the full prior conversation — every user directive, every binding rule. Reference doc for future agents. |
| `meta/docs/meta-harness-artifacts.md` | 15 KB | Research notes (canonical DesireRecord / ImprovementGoal / AGORA / GORE) | `research/meta-harness-artifacts.md` | keep | Source-of-truth for the schemas + InfraNodus operating modes synthesized in Amendments 05–08. |
| `meta/docs/github meta-harness (1).md` | 159 KB | Research notes (Stanford IRIS Lab Meta-Harness + InfraNodus deep-dive) | `research/github-meta-harness.md` | keep | Perplexity-derived; the QA technique catalog + InfraNodus API patterns used in Phase 0 spec verification. |
| `meta/docs/i want to critique this text,  reduce the unnecess (1).md` | 224 KB | Session transcript (Perplexity chat export — spec-mode alignment) | `sessions/2026-05-09-spec-critique-session.md` | keep | Provenance of the spec critique that led to evaluation criteria for the VW/iTwin/MARPA bridge. |
| `meta/docs/run_manifest.json` | 605 B | Harness runtime manifest (MARPA claim verification) | `sessions/2026-05-08-marpa-claim-verification-run-manifest.json` | keep | Provenance of the May-8 deep-research run that produced the MARPA dev-stack corpus. |
| `meta/docs/claims.jsonl` | 0 B | Harness runtime artifact (empty placeholder) | `sessions/2026-05-08-marpa-claim-verification-claims.jsonl` | keep | Empty companion to the manifest above. Kept for shape; not for content. |
| `meta/docs/evidence.jsonl` | 0 B | Harness runtime artifact (empty placeholder) | `sessions/2026-05-08-marpa-claim-verification-evidence.jsonl` | keep | Same. |
| `meta/docs/sources.jsonl` | 0 B | Harness runtime artifact (empty placeholder) | `sessions/2026-05-08-marpa-claim-verification-sources.jsonl` | keep | Same. |
| `meta/vw-itwin-bridge-meta-repomix.xml` | 861 KB | Repomix pack of the `meta/` folder (this folder's snapshot) | `sessions/2026-05-11-meta-folder-repomix.xml` | keep | User-generated Repomix dump used to communicate the dump-state at start of this amendment. |

## Frontmatter status (per §1.5)

| File | Frontmatter added | Notes |
|---|---|---|
| `amendments/09-polymorphic-genome-amendment-prompt.md` | ✅ | `status: shipped`, `superseded_by: null` |
| `specs/meta-harness-specification.md` | ✅ | renamed from `.txt` to `.md` |
| `research/meta-harness-artifacts.md` | ✅ | — |
| `research/github-meta-harness.md` | ✅ | — |
| `sessions/2026-05-09-spec-critique-session.md` | ✅ | — |
| `sessions/2026-05-08-*-{run-manifest.json, claims.jsonl, evidence.jsonl, sources.jsonl}` | ❌ — not markdown | JSON / JSONL do not take YAML frontmatter. Provenance captured in this inventory table. |
| `sessions/2026-05-11-meta-folder-repomix.xml` | ❌ — not markdown | XML; provenance captured in this inventory. |

## Status legend

- **keep** — file is referenced or useful enough to retain in current subfolder.
- **archive** — file was superseded; moved to `archive/` (none in this pass).
- **merge** — file content folded into another file in this pass (none in this pass).
- **delete-candidate** — flagged for human review before any deletion. **No deletions occurred in this commit.**

## Operating rule

Worst case for any future file in this tree is `archive/`. Deletion requires an explicit follow-up commit with the human's approval per the Hard Stops in the Phase 1 Amendment.

## 2026-05-11 addendum — Phase C Linear Infrastructure (feature/phase-c-linear)

Phase C delivered on branch `feature/phase-c-linear` (off `feature/meta-harness`).
Files created outside `meta/harness/docs/` but listed here for cross-reference.

| File | Type | Purpose |
|---|---|---|
| `meta/sync-contract.md` | New | Canonical field-direction table, Magic Words, conflict resolution policy |
| `meta/agent-lanes.md` | New | 5 agent lanes + human-only category |
| `meta/harness/PLAN/10-PHASE-C-LINEAR-AMENDMENT.md` | New | Phase C planning artifact |
| `.github/PULL_REQUEST_TEMPLATE.md` | Extended | Linear + Agent Lane header; updated phase labels; agent quality checklist |
| `scripts/agent-context-regenerate.sh` | New | Idempotent regeneration of `.github/agent-context.md` |
| `scripts/linear-reconciliation.py` | New | Stage 5b reconciliation; `--dry-run` default; CSV output here |
| `scripts/linear-notify-commit.sh` | New | Post-commit Linear comment hook |
| `.github/workflows/linear-sync-check.yml` | New | PR title + branch prefix validation CI |
| `.claude/settings.json` | Extended | `linear-notify-commit.sh` added as PostToolUse hook |

Reconciliation output (Stage 5b) will land in:
`sessions/<YYYY-MM-DD>-linear-import-reconciliation.md` (written by `scripts/linear-reconciliation.py`)

## 2026-05-12 addendum — MARPA research trove imported

After the initial reorg, the user pointed to the canonical external research folder at `/Volumes/PixelTable/VW_iTWIN_Bridge/Vectorworks_Bentley_iTwin_MARPA_Research_20260508/`. Five additional source files were copied into the repo tree (not moved — originals remain in the external folder as the authoritative source). The four Phase A stubs created in commit 24cc5f4 were rewritten with real extracted content sourced from these files.

| Original (external) | Copied to | Status |
|---|---|---|
| `bentley_ecosystem_deep_dive_20260508.md` | `research/bentley-ecosystem-deep-dive-20260508.md` | reference (frontmatter pre-existing) |
| `research_report_v2_20260508_verified.md` | `research/marpa-research-report-v2-20260508-verified.md` | reference (frontmatter pre-existing) |
| `research_report_20260508_vectorworks_itwin_marpa.md` | `research/marpa-research-report-v1-20260508.md` | superseded → `marpa-research-report-v2-20260508-verified.md` |
| `Dev_Stack/amended_research_proposal.md` | `specs/amended-research-proposal.md` | reference (frontmatter added) |
| `Dev_Stack/itwin-visgl-slide-bullets.md` | `specs/itwin-visgl-slide-bullets.md` | reference (frontmatter added) — the 28-slide platform architecture spec |

Rewritten stubs (4 files, status flipped from `draft` → `reference`):

| File | Before | After |
|---|---|---|
| `research/marpa-business-intelligence.md` | TODO scaffold | Strategic synthesis pulling competitive landscape, ASLA data points, target client segments, revenue model, risk register, strategic sequence |
| `specs/outreach-templates.md` | TODO scaffold | Four full template skeletons with extracted facts ($199 Standard, $250K Activate SAFE, James Kress / Clive Hackforth contacts, etc.) |
| `research/itwin-pricing.md` | TODO scaffold | Verified pricing tier table; **subsequently moved into `_gated/bentley-commercial/itwin-pricing.md` in Phase 1.5 §5.1** (see "Gated content" section below) |
| `research/vw-2026-toolchain.md` | Partial seed | Verified VW Landmark 2026 capability table + IFC certification status + SDK build prereqs + Nemetschek dTwin gap analysis |

## Gated content (dormant by default)

**Policy:** Commercial-tier vendor content (pricing, accelerator programs, partner programs, developer subscriptions, paid SaaS APIs) is gated under `meta/harness/docs/research/_gated/<vendor>/` and dormant by default per the OSS-self-hosted doctrine. See `meta/harness/docs/research/_gated/README.md` for the full five-gate policy + activation procedure, and `.claude/rules/oss-self-hosted-doctrine.md` for the binding rule.

Landed as Phase 1.5 commits `ad4ff91`, `fc144f4`, plus the cross-ref / doctrine / inventory follow-up commit.

### Subtree layout

| Path | Contents | Status |
|---|---|---|
| `_gated/README.md` | Top-level five-gate dormancy policy | gating-policy / dormant |
| `_gated/bentley-commercial/README.md` | Bentley-specific gate state + activation log + contents inventory | gating-policy / dormant |
| `_gated/bentley-commercial/itwin-pricing.md` | Moved from `research/itwin-pricing.md` per §5.1 (body unchanged; dormancy frontmatter + gating banner added) | research / dormant |
| `_gated/bentley-commercial/activate-program.md` | Extracted from `research/bentley-ecosystem-deep-dive-20260508.md` § Pillar 3 per §5.2 (SAFE / cohort / Ventures pipeline) | research / dormant |
| `_gated/bentley-commercial/partner-program.md` | Extracted from `research/bentley-ecosystem-deep-dive-20260508.md` § Pillar 1 per §5.2 (Standard/Premier tiers / Envision-Design-Sprint / commercial-terms layer) | research / dormant |
| `_gated/bentley-commercial/bdn-developer-access.md` | Extracted from `research/bentley-ecosystem-deep-dive-20260508.md` § Pillar 2 per §5.2 (Commercial + SELECT Subscription tiers + iTwin Platform paid-tier table); appended LATTICE-specific clarification that BDN is NOT required for iTwin REST API development | research / dormant |
| `_gated/cesium-commercial/README.md` | Cesium-specific gate state + self-hosting expansion note (mandatory per doctrine) | gating-policy / dormant |
| `_gated/cesium-commercial/cesium-ion-paid-tiers.md` | Stub — populated only when a real gate fires for Cesium | research / dormant |

### Status changes for files outside `_gated/`

| Path | Change |
|---|---|
| `research/bentley-ecosystem-deep-dive-20260508.md` | Pillars 1, 2, 3 replaced with stub paragraphs pointing at the gated extractions; Pillar 4 (GitHub iTwin org, public API changelogs, YII, Bentley Communities) stays in full as OSS-aligned content. File shrank from 453 → 292 lines. |
| `research/marpa-business-intelligence.md` | Cross-refs to `itwin-pricing.md` now route through `_gated/README.md` (the dormancy policy) and `_gated/bentley-commercial/` (Phase 1.5 §7) |
| `research/vw-2026-toolchain.md` | Same routing fix |
| `specs/outreach-templates.md` | Header gating-context note added; cross-refs now point directly at `_gated/bentley-commercial/*.md` files (outreach is the **one permitted use** of direct pointing into `_gated/`) |

### New rule file

`.claude/rules/oss-self-hosted-doctrine.md` codifies the OSS-self-hosted doctrine and the gated-vendor extension language. It operationalizes the cardinal rule `iTwin OSS self-hosted only` from `AGENTS.md` § cardinal rules and generalizes it across vendors.

## 2026-05-12 addendum — Meta-Harness audit and substrate orientation

This pass added a current-state map for the Meta-Harness incubation work on `feature/meta-harness`. These files are operational orientation docs, not historical session transcripts.

| File | Type | Purpose |
|---|---|---|
| `meta/harness/README.md` | Operational entrypoint | Current doctrine, hard stops, entrypoints, and checks |
| `meta/harness/CURRENT-STATE.md` | Audit snapshot | Inventory of capability registries, verification scripts, Pixeltable migrations, wired surfaces, and open gaps |
| `meta/harness/TODO.md` | Work queue | Prioritized tasks for the first dry run, Pixeltable substrate, capability coverage, legacy Python uplift, and portable extraction |
| `meta/harness/pixeltable-operational-substrate.md` | Doctrine note | Pixeltable as LATTICE operational substrate; DuckDB WASM over Pixeltable-served Arrow/Parquet |
| `scripts/check-python-docstrings.py` | Verification script | Changed-file Python docstring ratchet with `--all` for deliberate full legacy uplift |
| `scripts/lattice-verify.sh` | Verification script | Repo-wide deterministic verifier entrypoint for humans, CI, and Pi-backed verification |

Current capability registry audit:

| Metric | Value |
|---|---|
| Registry files | 22 |
| Capability rows | 193 |
| ACTIVE | 146 |
| DEFERRED | 44 |
| BLOCKED | 3 |
| Bootstrap-empty registries | 4 |

The four bootstrap-empty registries are `claude-code`, `deck-gl`, `pixeltable`, and `web-ifc`; they remain high-priority coverage gaps before the Meta-Harness can claim full capability awareness.

## 2026-05-18 addendum — Governed agent prompt contracts promoted into the Meta-Harness

This pass promoted the FRE-aligned prompt-contract work from ad hoc prompting
into an operational Meta-Harness artifact set. Unlike most files under
`meta/harness/docs/specs/`, these files are operational and intended to govern
bounded agent execution.

| File | Type | Purpose | Status |
|---|---|---|---|
| `meta/harness/docs/copilot-prompting-playbook.md` | Operational playbook | Copilot-specific heavy-run execution doctrine for the current pricing window, including `uv`-first Python policy and no paid API-key-default policy | operational |
| `meta/harness/docs/specs/agent-heavy-run-prompt-index.md` | Operational index | Single local entrypoint describing the prompt-contract artifact set and Meta-Harness usage path | operational |
| `meta/harness/docs/specs/agent-heavy-run-prompt-schema.md` | Operational spec | Human-readable method/spec for governed heavy-run prompt contracts | operational |
| `meta/harness/docs/specs/agent-heavy-run-prompt.schema.json` | Operational schema | Machine-readable validation schema for heavy-run prompt instances | operational |
| `meta/harness/docs/specs/agent-heavy-run-prompt.template.yaml` | Operational template | Fill-in template for new prompt-contract instances | operational |

Operational doctrine note:

- These prompt-contract artifacts are governed by FRE and cross-linked from the
  FRE Notion method/spec/schema pages.
- They are exceptions to the general `docs/specs` historical-reference default
  because they define the actual execution-contract shape used by the
  Meta-Harness.
