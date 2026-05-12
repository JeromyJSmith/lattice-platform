---
title: "Phase 1 Amendment — Verification Report"
type: session
status: reference
historical_only: true
source: "§4 Verification & Reporting (lattice-meta-harness-0.6-0.9 prompt)"
---

# Phase 1 Amendment — Verification Report

Posted to PR #230 via `gh pr comment 230 --body-file <this-file>`.

## 1. `git log --oneline 2684be9..HEAD` — every new commit

```
24cc5f4 docs(meta-harness): land Phase A business artifacts (MARPA BI, outreach, iTwin pricing, VW 2026)
f1ec252 feat(meta-harness): seed polymorphic skills genome (12 vendored + cell-divide + propose-decomposition) + polymorphic architecture spec
20f5042 docs(meta-harness): reorganize docs/ into amendments|specs|research|sessions|archive + add inventory and README
```

## 2. `tree meta/harness/docs/ -L 2` — reorganized layout

```
meta/harness/docs/
|-- AGENT.md
|-- GOAL.md
|-- MEMORY.md
|-- README.md
|-- _INVENTORY.md
|-- amendments
|   `-- 09-polymorphic-genome-amendment-prompt.md
|-- archive
|-- gold_goals.md
|-- research
|   |-- github-meta-harness.md
|   |-- itwin-pricing.md
|   |-- marpa-business-intelligence.md
|   |-- meta-harness-artifacts.md
|   `-- vw-2026-toolchain.md
|-- score-docs.sh
|-- sessions
|   |-- 2026-05-08-marpa-claim-verification-claims.jsonl
|   |-- 2026-05-08-marpa-claim-verification-evidence.jsonl
|   |-- 2026-05-08-marpa-claim-verification-run-manifest.json
|   |-- 2026-05-08-marpa-claim-verification-sources.jsonl
|   |-- 2026-05-09-spec-critique-session.md
|   |-- 2026-05-11-meta-folder-repomix.xml
|   `-- 2026-05-12-phase-1-verification.md
`-- specs
    |-- meta-harness-specification.md
    `-- outreach-templates.md

6 directories, 22 files
```

## 3. `tree .claude/skills/ -L 2` — seeded genome

```
.claude/skills/
|-- cell-divide
|   `-- SKILL.md
|-- diagnose
|   |-- SKILL.md
|   `-- scripts
|-- grill-with-docs
|   |-- ADR-FORMAT.md
|   |-- CONTEXT-FORMAT.md
|   `-- SKILL.md
|-- handoff
|   `-- SKILL.md
|-- improve-codebase-architecture
|   |-- DEEPENING.md
|   |-- INTERFACE-DESIGN.md
|   |-- LANGUAGE.md
|   `-- SKILL.md
|-- propose-decomposition
|   `-- SKILL.md
|-- prototype
|   |-- LOGIC.md
|   |-- SKILL.md
|   `-- UI.md
|-- setup-matt-pocock-skills
|   |-- SKILL.md
|   |-- domain.md
|   |-- issue-tracker-github.md
|   |-- issue-tracker-gitlab.md
|   |-- issue-tracker-local.md
|   `-- triage-labels.md
|-- tdd
|   |-- SKILL.md
|   |-- deep-modules.md
|   |-- interface-design.md
|   |-- mocking.md
|   |-- refactoring.md
|   `-- tests.md
|-- to-issues
|   `-- SKILL.md
|-- to-prd
|   `-- SKILL.md
|-- triage
|   |-- AGENT-BRIEF.md
|   |-- OUT-OF-SCOPE.md
|   `-- SKILL.md
|-- write-a-skill
|   `-- SKILL.md
`-- zoom-out
    `-- SKILL.md

16 directories, 33 files
```

## 4. `tail -25 .claude/rules/dependency-allowlist.md` — new mattpocock row

```yaml
    upstream: "github.com/mattpocock/skills"
    pinned_commit: "9f2e0bd0ea776eb6372eb81fa8a4a47814a8404a"
    language: markdown_bundle
    install_method: git_clone_to_tmp_plain_copy
    install_target: "/.claude/skills/<skill-name>/"
    vendor_strategy: plain-copy
    scope: project-local
    justification: |
      12 vendored skills (setup-matt-pocock-skills, grill-with-docs, to-prd,
      to-issues, triage, tdd, diagnose, prototype, improve-codebase-architecture,
      zoom-out, handoff, write-a-skill) form the seed of the polymorphic skill
      genome (Phase 1 Amendment §2). Source provenance + adaptation registry
      in .claude/rules/vendored-skills.md. Never installed via
      `npx skills@latest add` — always plain-copy from a pinned git clone.
    phase_added: 1
    rule_reference: .claude/rules/vendored-skills.md
    capability_registry: null  # vendored skill bundle, not a runtime tool with MCP surface
```

## Adding a new dependency

1. Open a PR that appends a row to the YAML above
2. Same PR creates `analysis/capabilities/<id>-capability-registry.yaml` (stub OK, but every capability surface enumerated per Capability Harvest Protocol)
3. PR description includes: what alternative was considered, why this one was chosen, install footprint, runtime cost, security surface
4. Merge gated on reviewer approval (Zero Dead DNA enforced from first commit)
```

## 5. `.claude/rules/vendored-skills.md` — the new rule

<!-- spec-verified: code.claude.com/docs 2026-05-11 -->
# Vendored Skills Rule

**Standard introduced by Phase 1 Amendment (§2.4)** — see `meta/harness/PLAN/09-POLYMORPHIC-ARCHITECTURE-AMENDMENT.md`.

## The rule

Skills imported from an upstream source repository are **vendored as plain copies** into `/.claude/skills/<skill-name>/`, pinned to a specific upstream commit SHA. They are NOT submodules, NOT installed via `npx skills@latest add ...`, and NOT live-fetched at runtime.

## Why plain-copy

| Concern | Why plain-copy wins |
|---|---|
| Reproducibility | The SHA is in every SKILL.md `source:` field; rebuilding the tree from scratch produces byte-identical content. |
| Local adaptation | The vendored body is editable in-place. Adaptations go in `local_adaptations:` frontmatter, with one line per change. |
| Offline operation | No network call to install. Repo clone is sufficient. |
| Audit trail | Diff vs. upstream is `git diff` against a re-vendor at the same SHA. |
| Security | No automatic upstream updates can sneak in. Re-vendor is an explicit human decision. |

## Currently vendored skill sources

| Upstream | Pinned commit | First vendored | Notes |
|---|---|---|---|
| `github.com/mattpocock/skills` | `9f2e0bd0ea776eb6372eb81fa8a4a47814a8404a` | 2026-05-11 | 12 of the engineering + productivity skills. See `meta/harness/PLAN/09-POLYMORPHIC-ARCHITECTURE-AMENDMENT.md` for the per-skill table. |

## Local adaptations registry

Every adapted skill MUST list its adaptations in the SKILL.md frontmatter:

```yaml
local_adaptations:
  - date: "2026-05-11"
    change: "Replaced 'pnpm install' with 'uv sync' in setup steps"
    rationale: "LATTICE uses uv only — no pnpm in the toolchain"
  - date: "2026-06-15"
    change: "Added LATTICE-specific issue label conventions (agent-ready, meta-harness)"
    rationale: "Match the GitHub label taxonomy added in Phase 0"
```

The same audit script that enforces Zero Dead DNA (`scripts/audit-dead-dna.sh`, Issue #232) will eventually cross-check `local_adaptations` against the diff between the vendored body and the pinned upstream body. Adaptations not listed will be flagged.

## Prohibited operations

- `npx skills@latest add mattpocock/skills` — **banned for this project**. Always vendor via `git clone` → copy → delete clone.
- `npx skills@latest add <anything>` — same.
- `git submodule add github.com/mattpocock/skills .claude/skills/...` — banned.
- Editing the `source:` or `vendored_at:` fields of a vendored skill — banned. To update, re-vendor the whole skill at a new pinned SHA.

## Re-vendoring procedure (when upstream evolves)

1. Clone upstream to `/tmp` and pin a new SHA: `git clone https://github.com/<upstream>/<repo> /tmp/<repo> && git -C /tmp/<repo> rev-parse HEAD`.
2. Copy the new skill directory over the existing `/.claude/skills/<skill>/`.
3. Preserve `local_adaptations:` from the existing SKILL.md frontmatter. Bump `source:` and `vendored_at:` to the new SHA + timestamp.
4. Run `git diff` to verify the impact. If the upstream change conflicts with a local adaptation, the human resolves before commit.
5. Commit with `chore(skills): re-vendor <skill> to <new-sha[:7]>`.

## Cross-references

- `meta/harness/PLAN/09-POLYMORPHIC-ARCHITECTURE-AMENDMENT.md` — genome design + cellular division
- `.claude/rules/dependency-allowlist.md` — pinned-SHA row for each vendored source
- `.claude/rules/capability-harvest-protocol.md` — sibling rule for tool capabilities
- `.claude/rules/zero-dead-dna.md` — sibling rule for unused vendored skills

## 6. `ls meta/harness/PLAN/` — confirm 09-POLYMORPHIC-ARCHITECTURE-AMENDMENT.md exists

```
Permissions  Size User     Date Modified Git Name
.rw-r--r--   3.9k ojeromyo 11 May 17:21   -- 00-OVERVIEW.md
.rw-r--r--   9.2k ojeromyo 11 May 15:33   -- 01-RESEARCH.md
.rw-r--r--    16k ojeromyo 11 May 17:21   -- 02-PLAN.md
.rw-r--r--   7.9k ojeromyo 11 May 16:14   -- 03-DOCS-DELTA.md
.rw-r--r--    16k ojeromyo 11 May 17:22   -- 04-EXECUTION-HANDOFF.md
.rw-r--r--    21k ojeromyo 11 May 16:13   -- 05-RESEARCH-AMENDMENT.md
.rw-r--r--   6.1k ojeromyo 11 May 17:22   -- 06-CAPABILITY-HARVEST-AMENDMENT.md
.rw-r--r--   6.8k ojeromyo 11 May 17:22   -- 07-PIXELTABLE-SUBSTRATE-AMENDMENT.md
.rw-r--r--   7.7k ojeromyo 11 May 17:17   -- 08-DOCS-META-HARNESS-AMENDMENT.md
.rw-r--r--  10.0k ojeromyo 11 May 19:34   -- 09-POLYMORPHIC-ARCHITECTURE-AMENDMENT.md
```

## 7. GitHub Issue #27 URL

Created via `gh issue create` (real API call, not a local draft): <https://github.com/JeromyJSmith/lattice-platform/issues/243>

Note: the prompt-internal number "#27" became GitHub Issue **#243** because issues #17 through #26 from prior amendments landed on the live GitHub repo as #231–#240 + #241–#242. #243 is the next available number; the issue body cross-references the prompt's logical "#27" identity.

## 8. Pinned `mattpocock/skills` upstream commit SHA

`9f2e0bd0ea776eb6372eb81fa8a4a47814a8404a`

Verified by re-cloning to /tmp, running `git rev-parse HEAD`, copying the 12 skill directories, then deleting the clone. SHA recorded in every vendored `SKILL.md`'s `source:` frontmatter field, in `.claude/rules/vendored-skills.md`, and in `.claude/rules/dependency-allowlist.md`.

## 9. cell-divide / propose-decomposition confirmation

- `cell-divide` was NOT executed in this phase. The skill exists on disk at `.claude/skills/cell-divide/SKILL.md` with `disable-model-invocation: true` and explicit HARD-CONSTRAINT-Phase-1 notices in its body.
- `propose-decomposition` was NOT invoked in this phase. Same constraints, same on-disk shape, same notices.
- The genome (14 skills) is seeded but inert. The first autonomous division act will happen only after Phase B (M3 Max live bootstrap + verification) completes and a human approves a `propose-decomposition` output.

## Branch state at report time

```
current HEAD: 24cc5f4cc6b919532b72c31895aac2da3f37eddd
current branch: feature/meta-harness
commits ahead of main: 13
```
