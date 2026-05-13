# Phase 1 — foundation (green lights)

Zero-risk, idempotent setup work. No architectural decisions, no per-row triage.

## Status as of 2026-05-13

| Item | State | Evidence |
|---|---|---|
| `bash scripts/setup-portless.sh` | ✅ DONE | commit 534af6e — all 5 `.portless.json` files materialized |
| Export `INFRANODUS_API_KEY` + restart Claude Code | ⏳ PENDING (user shell action) | Token in handoff §3 of `meta/harness/HANDOFF-2026-05-13-meta-harness-substrate.md` |

## The remaining task

The InfraNodus MCP server reads `${INFRANODUS_API_KEY}` from Claude Code's parent
env. The literal placeholder string is currently being sent instead of a real token,
which is why all MCP calls return "Invalid authorization token."

Fix (one-time, user shell):

```bash
# Add to ~/.zshrc (or your shell rc):
export INFRANODUS_API_KEY="21813:f39d3ec8a5cd92f8d2fb379ffa73b289766503bf4c9db626a6ea144a92642437"

# Then fully quit Claude Code (Cmd+Q) and relaunch.
# New process inherits the env, MCP server picks it up.
```

Verification next session:

```
mcp__infranodus__analyze_text(text="hello world")
```

If it returns analysis (not "Invalid authorization token"), wiring is complete and
the 8 InfraNodus advisory-stale rows can be re-walked against the now-working MCP.

Also worth checking before relaunch — make sure no stale empty value shadows it:

```bash
cat ~/.claude/env 2>/dev/null | grep -i infranodus
```
