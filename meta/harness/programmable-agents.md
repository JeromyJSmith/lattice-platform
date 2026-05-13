<!-- spec-verified: disler/claude-code-is-programmable 3889265 2026-05-12 -->
# Programmable Agents

Agents are executable components. LATTICE can call Claude CLI, Pi, Codex, Gemini, OpenRouter, Ollama, MLX, or local scripts from other scripts when the task is bounded and verified.

## Rule

Programmatic agent calls must declare:

- input prompt or spec
- allowed tools
- model/provider
- output format
- output artifact path
- verification command

Do not let programmatic agent calls become ambient authority.

## Claude Code pattern

Claude Code can run as a Unix-style utility:

```bash
claude -p "<prompt>" --allowedTools "Read" "Write" --output-format json
```

For LATTICE, this should be wrapped by a repo-owned script or Pi job, not pasted ad hoc into conversations.

## Output policy

Prefer machine-readable outputs when downstream harnesses need to consume the result:

- `text` for human-only reports
- `json` for one-shot structured outputs
- `stream-json` for live event processing

Every programmatic call needs evidence of what was asked, what tools were allowed, and what was produced.

## Safety

Allowed tools should be task-specific. If a call only needs to write one report, it should not receive broad Bash authority. If it needs Bash, route through the L4/L5 policy in `meta/harness/bash-safety.md`.
