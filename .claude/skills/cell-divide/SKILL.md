---
name: cell-divide
description: "Reproductive function. Copies the root .claude/skills/ genome into a target section's .claude/skills/ location (or deeper), appends the parent commit SHA to each child SKILL.md lineage, and registers the new cell in lattice/knowledge/skills_registry. INERT in Phase 1 — do not execute recursive division yet."
arguments: "[target_path] [parent_commit_sha] [section_name]"
disable-model-invocation: true
user-invocable: true
source: "lattice-internal (Phase 1 Amendment §2.2)"
vendored_at: null
vendor_strategy: lattice-authored
local_adaptations: []
lineage: []
---
# cell-divide — Polymorphic Skill Genome Reproduction

> **HARD CONSTRAINT — Phase 1:** This skill is *inert*. The body below documents its eventual behavior. Do NOT invoke recursive division in this phase. Division begins only after Phase B (live execution + bootstrap verification on the M3 Max) completes successfully and a human approves a `propose-decomposition` output.

## Purpose

Copy the genome (the contents of `/.claude/skills/`) into a target sub-tree (typically `meta/harness/sections/<section>/.claude/skills/`), preserving lineage and registering the new cell in the knowledge substrate.

## Inputs

| Argument | Required | Meaning |
|---|---|---|
| `target_path` | yes | Absolute path *inside the repo* where the new cell's `.claude/skills/` should land. Typically `meta/harness/sections/<section>/.claude/skills/`. |
| `parent_commit_sha` | yes | The commit SHA of the parent genome being copied (root genome = first commit that introduced the skill tree; deeper cells = the commit at which the parent cell forked). |
| `section_name` | yes | Human-readable section name (e.g. `schema`, `api`, `frontend`, `docs`). Recorded in `skills_registry.lineage_source` metadata. |

## Behavior (Phase 2+)

1. Verify `target_path` is inside the repo and inside an `meta/harness/sections/*` subtree (defense-in-depth against arbitrary writes).
2. Snapshot the parent genome at `parent_commit_sha`. Use `git archive` or a plain recursive copy of the parent path's contents.
3. For each child `SKILL.md`, append `parent_commit_sha` to the YAML `lineage:` list. Order: youngest ancestor first → oldest last.
4. For each child `SKILL.md` that has no `local_adaptations:` key yet, add `local_adaptations: []`.
5. Insert one row per skill into `lattice/knowledge/skills_registry` (table already exists from migration 0015):
   - `skill_name = <skill-name>`
   - `tool_name = "lattice-meta-harness"`
   - `skill_md_path = <target_path>/<skill-name>/SKILL.md`
   - `lineage_source = parent_commit_sha`
   - `content = <SKILL.md body>`
   - `created_at = NOW()`
6. Commit the new cell to git as a separate commit with message `feat(harness/<section>): cell-divide from <parent_sha[:7]>`. Do NOT merge or push — the human reviews each division on a feature branch.

## What this skill does NOT do

- It does NOT mutate the parent genome. Source is read-only.
- It does NOT invoke `propose-decomposition`. That is a separate, introspective skill.
- It does NOT recurse automatically. Each invocation copies exactly one level. To go deeper, the human must re-invoke after reviewing the previous level's health.
- It does NOT touch `lattice/knowledge/skills_registry.committed_path` if the row already has a non-null value. (Promotion paths preserve that field.)

## Hard constraint reminder

Per Phase 1 Amendment §2.2 + §5:
- **Do not run this skill in Phase 1.**
- **Do not run `propose-decomposition` in Phase 1.**
- The skill exists on disk so its presence is auditable and its frontmatter is testable, but it remains inert until Phase B sign-off.
