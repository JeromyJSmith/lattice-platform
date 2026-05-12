# `meta/harness/docs/` — Documentation Meta-Harness Section + Historical Reference

This folder serves two distinct purposes. Read both before adding anything.

## Purpose 1: Operational files for the 9th section (Docs Meta-Harness)

Five files at the top of this folder belong to the **Documentation Meta-Harness section** introduced in Amendment 08. They are *not* historical and they *are* operational artifacts:

| File | Role |
|---|---|
| `AGENT.md` | Subagent definition for `docs-harness-agent` (AGORA 3-layer YAML frontmatter) |
| `GOAL.md` | Fitness function for this section harness |
| `MEMORY.md` | Section memo — agent writes / reads across sessions |
| `gold_goals.md` | Compact ratchet target |
| `score-docs.sh` | Scoring stub (Issue #23 fills in the real impl) |

Touching these files updates the docs-harness section's behavior. They follow the same template as every other section context stack in `meta/harness/sections/<section>/`.

## Purpose 2: Historical and reference documentation (everything else)

The five subfolders below house the **non-authoritative** documentation tree:

- **`amendments/`** — historical amendment prompts that already shipped. Each carries `status: shipped`, `historical_only: true`, and a `shipped_in_commit` reference. Useful as a paper trail; do not execute their contents.
- **`specs/`** — canonical specs and source-of-truth compressions (e.g., the full session compression at `meta-harness-specification.md`). Reference material for any agent that needs to recover prior intent.
- **`research/`** — external research notes (Stanford Meta-Harness deep-dive, MARPA dev-stack research, InfraNodus / Graphify / GitNexus eval notes). Provenance for design decisions captured in `meta/harness/PLAN/`.
- **`sessions/`** — raw session transcripts, Repomix dumps, chat exports, and harness-runtime manifests. Pure provenance — nothing in this folder should ever be cited as authoritative.
- **`archive/`** — superseded drafts kept for traceability only. Frontmatter on archived files MUST include `superseded_by:` pointing at the replacement file.

## The rule that anchors everything else

> **Nothing in `meta/harness/docs/{amendments,specs,research,sessions,archive}/` is executable instruction.**
>
> Authoritative instructions for the meta-harness live in:
> - `meta/harness/PLAN/NN-*.md` (numbered amendment plans — current source of truth)
> - `.claude/rules/*.md` (binding agent rules)
> - The section context stacks under `meta/harness/sections/<section>/`
>
> If you find yourself reaching for a file in `docs/*/` to decide what to do, you are reaching for a reference, not an order.

## Adding a new doc

| Doc type | Goes in | Frontmatter requirement |
|---|---|---|
| Amendment prompt that already shipped | `amendments/NN-<slug>.md` | `type: amendment`, `status: shipped`, `shipped_in_commit: <sha>`, `historical_only: true`, `superseded_by: null` |
| Canonical spec (or compressed source-of-truth) | `specs/<slug>.md` | `type: spec`, `status: reference`, `historical_only: true`, `source: "<original>"` |
| External research note | `research/<slug>.md` | `type: research`, `status: reference`, `historical_only: true`, `source: "<original or URL>"` |
| Session / transcript / dump | `sessions/<YYYY-MM-DD>-<slug>.<ext>` | If markdown: `type: session`, `status: reference`, `historical_only: true`, `source: "<original>"`. Non-markdown (JSON/JSONL/XML): no frontmatter; instead add a row to `_INVENTORY.md`. |
| Superseded draft | `archive/<original-slug>.md` | All of the above + `superseded_by: "<path/to/replacement>"` |

YAML frontmatter values containing `:`, `@`, `/`, spaces, or other special chars MUST be double-quoted (e.g., `source: "mattpocock/skills@<sha>:skills/engineering/tdd"`). Unquoted colons silently break YAML parsing.

## How this folder is audited

The Documentation Meta-Harness section (the `AGENT.md` at the top of this folder) treats this whole tree as one of its corpus inputs. When the docs-harness section's autoresearch loop runs, it indexes `_INVENTORY.md` + every file under `amendments/specs/research/` into the knowledge substrate via `scripts/ingest-docs.py` (tracked by Issue #24). That is the *only* mechanism by which content in this folder influences agent behavior — never directly.
