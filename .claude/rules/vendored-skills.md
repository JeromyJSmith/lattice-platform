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
