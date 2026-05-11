<!-- spec-verified: code.claude.com/docs 2026-05-11 -->
# LATTICE Meta-Harness — Planning Overview

This directory holds the four-phase plan for the LATTICE Meta-Harness build. Nothing under `meta/harness/PLAN/` ships code — these are planning artifacts only. Implementation lives in subsequent commits on this branch (`feature/meta-harness`).

## The four phases

| Phase | Artifact | Purpose | Status |
|---|---|---|---|
| 1 — Research | [`01-RESEARCH.md`](01-RESEARCH.md) | Local-docs queries (Claude Code spec verification) | ✅ initial pass complete |
| 2 — Plan | [`02-PLAN.md`](02-PLAN.md) | Phased execution plan with checkpoints, file inventory, dependency graph, branch strategy | ✅ amended |
| 3 — Docs Delta | [`03-DOCS-DELTA.md`](03-DOCS-DELTA.md) | Diff-level list of every existing doc that needs editing + what gets created where | ✅ amended |
| 4 — Execution Handoff | [`04-EXECUTION-HANDOFF.md`](04-EXECUTION-HANDOFF.md) | Self-contained handoff for whichever agent executes the build | ✅ amended |
| 5 — Research Amendment | [`05-RESEARCH-AMENDMENT.md`](05-RESEARCH-AMENDMENT.md) | MARPA + Meta-Harness research synthesis. **Binding.** Phase 1 blocked until reviewed. | ✅ added |

## Branch contract

- All Meta-Harness work lives on `feature/meta-harness` until merged.
- Draft PR opened against `main`; reviewer-gated merge.
- Required CI: `docs-sync-check` (5 existing jobs) + new spec-compliance job (lands in Phase 3 of execution, not here).
- No force-pushes on `main`. No bypassing branch protection.

## Doctrine (non-negotiable)

1. **No file written from memory.** Every system file is spec-verified against the local doc indexes (`/Users/ojeromyo/.claude-code-docs/`, `/Users/ojeromyo/.vectorworks-docs/`) before creation. Every system file carries a `<!-- spec-verified: <source> <date> -->` comment.
2. **Branch first, write second.** This branch was created before any file touched.
3. **Plan before code.** All four planning artifacts complete and committed before any implementation file (skill, agent, scoring script, migration) is added.
4. **Specs override the original prompt.** Where the human-written amendment disagrees with the verified local docs, the docs win. Divergences are flagged in [`01-RESEARCH.md`](01-RESEARCH.md) § Spec corrections.
5. **Reversibility.** Anything that lands on this branch can be reverted by deleting the branch. Nothing in this PR mutates `main` infrastructure (e.g. branch-protection rules) until the PR is reviewed and merged.

## What this is NOT

- Not an execution of the Meta-Harness build. That happens in subsequent commits on this branch, after these planning artifacts are reviewed.
- Not a replacement for the existing `meta/ARCHITECTURE.md` / `meta/SCHEMA.md` / `meta/API.md`. Those remain canonical for the platform-as-built.
- Not an autonomous loop activation. The autoresearch loop is designed in [`02-PLAN.md`](02-PLAN.md) but does not run until human approval.
