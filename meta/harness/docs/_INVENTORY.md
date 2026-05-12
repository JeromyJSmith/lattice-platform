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
| `research/itwin-pricing.md` | TODO scaffold | Verified pricing tier table (Community / Standard $199 / Premium $499 / Enterprise), credit cost structure, Activate $250K + $100M iTwin Ventures fund details, BDN unknowns flagged |
| `research/vw-2026-toolchain.md` | Partial seed | Verified VW Landmark 2026 capability table + IFC certification status + SDK build prereqs + Nemetschek dTwin gap analysis |
