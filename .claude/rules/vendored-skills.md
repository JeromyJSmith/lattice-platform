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

## Nested `.git/` directories — strip before commit

When you vendor anything by cloning (vs. copying individual files), the upstream's `.git/` directory comes along for the ride. **It MUST be removed before the content lands in this repo.**

If you forget, `git add` will detect the embedded repo and create a gitlink (an unregistered submodule pointer) instead of adding the files. The directory will appear as a single entry in `git ls-files`, the content won't be in our repo, and a fresh clone on another machine will get a broken pointer.

### The procedure

```bash
# After git clone <upstream> .claude/skills/<name>/  (or any nested location)
rm -rf .claude/skills/<name>/.git
git add .claude/skills/<name>/
```

`**/.git/` is **not** in `.gitignore` (we want to be told by `git add`'s "embedded git repository" warning that this happened — silent acceptance hides the recursion problem). The specific path `.claude/skills/*/.git/` IS ignored after PR #230 to absorb the common case for skill bundles. Other vendored locations: strip manually.

### Recovery if you already created a gitlink

```bash
git rm --cached -f .claude/skills/<name>
rm -rf .claude/skills/<name>/.git
git add .claude/skills/<name>/
```

This applies to **every nested git repo** anywhere in the tree — not just `.claude/skills/`. Drop a clone in `tools/`, `meta/harness/`, `analysis/`, `vendored/`, anywhere — strip `.git/` first.

## Disler / IndyDevDan repositories

`github.com/disler/*` (IndyDevDan's repositories) are a recurring source for LATTICE substrate — `single-file-agents`, `benchy`, `agentic-drop-zones`, `claude-code-hooks-mastery`, `the-library`, `pi-vs-claude-code`, `the-verifier-agent`, `agent-sandboxes`, etc. They're listed in `analysis/capabilities/README.md` and most have a capability registry.

**Every Disler vendoring operation gets the strip-`.git/`-before-commit treatment.** This is the most common nested-git-repo case in this codebase, so flag it specifically: if you find yourself cloning `github.com/disler/<anything>`, the inner `.git/` does not belong in the parent repo. Strip it, vendor flat, record the pinned SHA in the `source:` frontmatter of whatever skill/registry references it.

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
