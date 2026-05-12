<!-- spec-verified: disler/claude-code-hooks-mastery 052ad1c; disler/claude-code-hooks-multi-agent-observability 8a6e5cf 2026-05-12 -->
# Hooks And Observability

LATTICE incorporates Claude Code hooks as deterministic control points and event emitters.

## Hook doctrine

Hooks are not chat instructions. Hooks are executable control points:

- validate prompts before the model sees them
- block dangerous tool calls before execution
- log tool calls, failures, stops, compaction, subagent lifecycle, and session lifecycle
- inject setup or project context deterministically
- emit events into an observability stream

Hook scripts should be small uv single-file Python scripts with embedded dependencies when practical.

## Event surface

The Meta-Harness should treat hook events as evidence:

| Event class | LATTICE use |
|---|---|
| user prompt | intake, routing, and prompt validation |
| pre-tool | bash/path/secret guardrails |
| post-tool | command evidence and artifact capture |
| failure | diagnostic evidence |
| stop | verification trigger |
| subagent start/stop | delegated work tracking |
| compact | context-loss audit |
| session start/end | setup, cleanup, and run boundary |

## Observability target

The incorporated observability pattern is:

```text
Claude hooks -> event sender -> HTTP server -> SQLite -> WebSocket -> dashboard
```

LATTICE does not need to vendor the dashboard before the dry run. It does need a stable event contract so the first dry run can produce evidence that later feeds a dashboard or Pixeltable ledger.

## Dry-run rule

For the first Meta-Harness dry run, capture:

- start/end time
- selected execution surface
- commands/scripts invoked
- verifier status
- blocked guardrail attempts, if any
- output artifact paths

If a hook does not produce evidence, it is not part of the dry-run gate yet.
