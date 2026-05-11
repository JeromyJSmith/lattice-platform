<!-- spec-verified: code.claude.com/docs 2026-05-11 -->
# Phase 1 — Research

## Sources queried

| Source | Path | Last updated | Used for |
|---|---|---|---|
| Claude Code docs mirror | `/Users/ojeromyo/.claude-code-docs/docs/` | 2026-05-11 (auto-synced) | SKILL.md, subagent, hooks, memory/CLAUDE.md, settings, slash commands |
| Vectorworks SDK docs | `/Users/ojeromyo/.vectorworks-docs/` | 2026-05-11 | (reserved for VW plugin section; not used in this planning pass) |
| Anthropic public docs | `https://docs.anthropic.com/en/docs/claude-code/` | live | cross-reference for any field not in cache |
| code.claude.com docs | `https://code.claude.com/docs/` | live | secondary cross-reference |

## Verified specifications

### A. SKILL.md (`.claude/skills/<name>/SKILL.md`)

**Source:** `~/.claude-code-docs/docs/skills.md` § "Frontmatter reference"

- Lives in a **directory** named after the skill. The directory is the unit; `SKILL.md` is the entrypoint.
- YAML frontmatter between `---` markers is REQUIRED in practice. All fields are technically optional; only `description` is recommended so Claude knows when to apply the skill.
- Skill body stays in context across turns once loaded → keep it under 500 lines, state what to do, not how/why.
- Supporting files (`reference.md`, `examples.md`, `scripts/`) load on demand.

**Verified frontmatter fields (complete list as of 2026-05-11):**

| Field | Required | Notes |
|---|---|---|
| `name` | No | Lowercase + numbers + hyphens, max 64 chars. Falls back to directory name. |
| `description` | Recommended | Used for auto-invocation decision. Combined with `when_to_use` capped at 1,536 chars. Put trigger phrase first. |
| `when_to_use` | No | Appended to `description`. |
| `argument-hint` | No | Autocomplete hint, e.g. `[issue-number]`. |
| `arguments` | No | Named positional args (space-separated string or YAML list). |
| `disable-model-invocation` | No | `true` = user-invoked only. Also prevents preload into subagents. |
| `user-invocable` | No | `false` = hidden from `/` menu. |
| `allowed-tools` | No | Space-separated string or YAML list. Tools allowed without per-use approval while skill is active. |
| `model` | No | Override model for skill duration. Accepts `/model` values or `inherit`. |
| `effort` | No | `low \| medium \| high \| xhigh \| max`. |
| `context` | No | `fork` = run in forked subagent. |
| `agent` | No | Which subagent type to use when `context: fork`. |
| `hooks` | No | Lifecycle hooks scoped to this skill. |
| `paths` | No | Glob patterns (comma-separated string or list). Auto-loads only when matching files in play. Same format as path-specific CLAUDE.md rules. |
| `shell` | No | `bash` (default) or `powershell`. PowerShell needs `CLAUDE_CODE_USE_POWERSHELL_TOOL=1`. |

**String substitutions** (in skill body): `$ARGUMENTS`, `$0` / `$ARGUMENTS[0]`, named `$name`, `${CLAUDE_SESSION_ID}`, `${CLAUDE_EFFORT}`, `${CLAUDE_SKILL_DIR}`.

**Dynamic context injection**: prefix line with `!` for single-line shell exec, or use a `!` fenced block for multi-line. Runs before Claude sees the skill body.

### B. Subagent files (`.claude/agents/<name>.md`)

**Source:** `~/.claude-code-docs/docs/sub-agents.md` § "Supported frontmatter fields"

- Markdown with YAML frontmatter; body is the system prompt.
- Loaded at session start. Add/edit on disk → restart session to load.

**REQUIRED fields:** `name`, `description` (both). User-amendment confirmed correct.

**All supported frontmatter fields (verified):**

`name`, `description`, `tools`, `disallowedTools`, `model`, `permissionMode`, `mcpServers`, `hooks`, `maxTurns`, `skills`, `initialPrompt`, `memory`, `effort`, `background`, `isolation`, `color`.

**Spec correction vs amendment:** the user's amendment lists `name: schema-harness` as required — confirmed. The amendment's example is valid.

**Plugin restriction:** plugin-bundled subagents do NOT support `hooks`, `mcpServers`, or `permissionMode`. Our subagents live in `.claude/agents/`, not in a plugin → all fields available.

**Storage priority** (highest wins on name collision): managed settings → `--agents` CLI flag → `.claude/agents/` → `~/.claude/agents/` → plugin `agents/`.

### C. CLAUDE.md

**Source:** `~/.claude-code-docs/docs/memory.md`

- Plain markdown. **No YAML frontmatter on CLAUDE.md itself.** Confirmed.
- Use `@path/to/file` syntax to import other files (load-at-launch).
- Loads hierarchically: parent dirs first, working dir last.
- Subdirectory CLAUDE.md files load on demand when Claude reads files there.
- `CLAUDE.local.md` = personal, gitignored sibling.
- Target under 200 lines per file (community guideline, not a parser rule).

**Path-specific rules** live in `.claude/rules/<name>.md` and CAN have YAML frontmatter with a `paths:` field. Without `paths:`, the file loads at launch like `.claude/CLAUDE.md`.

### D. Hooks

**Source:** `~/.claude-code-docs/docs/hooks.md`, `hooks-guide.md`, `settings.md`

- **JSON, not markdown.** Live in:
  - `.claude/settings.json` (project, committed)
  - `.claude/settings.local.json` (project, gitignored)
  - `~/.claude/settings.json` (user, machine-local)
  - Plugin `hooks/hooks.json`
  - **Frontmatter of a skill or subagent** (scoped to that component's lifecycle)
- Event types: `PreToolUse`, `PostToolUse`, `Notification`, `Stop`, `SubagentStart`, `InstructionsLoaded` (+ others — see docs).
- Each hook has a `matcher` (tool name pattern or `*`) and a list of `hooks` (`type: command`, `command`, optional `timeout`).
- Exit code 2 from a PreToolUse hook **blocks the tool**.

### E. AGENTS.md

**Source:** widely-adopted convention; Claude Code uses `CLAUDE.md` as its primary file but supports `AGENTS.md` import.

- The convention: `AGENTS.md` is the cross-agent contract (Codex / Copilot / Gemini CLI / OpenCode read this).
- Claude Code reads `CLAUDE.md`; we make each section's `CLAUDE.md` start with `@AGENTS.md` to pull in the cross-agent content.

### F. Settings.json (project)

**Source:** `~/.claude-code-docs/docs/settings.md`

- JSON, committed to repo.
- Holds `permissions`, `hooks`, `model`, `env`, `additionalDirectories`, MCP overrides, `auto-mode` config, etc.
- `settings.local.json` overrides `settings.json` for personal use.

## Local doc evidence (citation pointers)

| Claim | File | Line/section |
|---|---|---|
| SKILL.md frontmatter table | `~/.claude-code-docs/docs/skills.md` | § "Frontmatter reference" |
| Subagent required fields = name + description | `~/.claude-code-docs/docs/sub-agents.md` | § "Supported frontmatter fields" (table preamble) |
| CLAUDE.md hierarchical load | `~/.claude-code-docs/docs/memory.md` | § "How memory files work" |
| `.claude/rules/` with `paths:` frontmatter | `~/.claude-code-docs/docs/memory.md` | § "Path-specific rules" |
| Hooks in JSON | `~/.claude-code-docs/docs/hooks.md` | § "Configuration" |
| Subagent priority table | `~/.claude-code-docs/docs/sub-agents.md` | § "Storage and discovery" |

## Spec corrections to original amendment

The amendment is **substantially correct** as a spec summary. Minor calibrations:

| Amendment claim | Doc reality | Treatment |
|---|---|---|
| "All fields are optional except description is strongly recommended" (for SKILL.md) | Confirmed verbatim | ✅ no change |
| "name and description are THE ONLY REQUIRED FIELDS" (for subagent) | Confirmed | ✅ no change |
| "CLAUDE.md files are plain markdown. They do NOT use YAML frontmatter." | Confirmed | ✅ no change |
| "Hooks are JSON in .claude/settings.json (or skill/agent YAML frontmatter)" | Confirmed | ✅ no change |
| ".claude/skills/lattice-schema/SKILL.md (directory structure mandatory)" | Confirmed — skills ARE directories | ✅ no change |
| "If the spec is ambiguous, emit a comment: `<!-- spec-verified: <source> <date> -->`" | Not a spec rule; LATTICE-internal convention | ✅ adopt as our convention |
| "Section CLAUDE.md files must import their AGENTS.md via `@AGENTS.md`" | `@import` syntax is real; treating it as mandatory is our policy | ✅ adopt as our policy |

## Vectorworks docs

Reserved for the VW Bridge section's CLAUDE.md / SKILL.md authoring. Will query `/Users/ojeromyo/.vectorworks-docs/sources.json` and `docs/` in Phase 4 of the execution (Section 6: VW Bridge & iTwin). Not consumed during the planning pass.

## Open research questions (defer to execution phase)

1. **InfraNodus API key sourcing.** Free tier vs paid? Required for Global Meta-Harness or only Section harnesses? → mark as `agent-ready` issue, do not block execution.
2. **GitNexus vs Graphify scope overlap.** Both index call graphs; clarify whether we run both or pick one per section. → spike during Section 1 (Schema) execution.
3. **Self-hosted runner for `test-pxt`.** Already tracked as issue #227 — not a Meta-Harness blocker, but autoresearch loop scoring for `.github/` section depends on its registration.
4. **Pixeltable `pxt.Float` vs `pxt.Float64`.** The amendment mentions guarding against `pxt.Float` misuse — verify the actual API surface during migration 0014 authoring (not now; we are not writing 0014 in this pass).

These are documented now so the execution agent does not have to rediscover them.
