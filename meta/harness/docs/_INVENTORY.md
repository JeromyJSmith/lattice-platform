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
