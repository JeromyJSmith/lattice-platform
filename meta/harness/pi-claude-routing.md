<!-- spec-verified: disler/pi-vs-claude-code 3ce1639 2026-05-12 -->
# Pi And Claude Routing

LATTICE uses both Pi and Claude CLI. Neither replaces the other.

## Routing rule

Use Pi when the job benefits from:

- model/provider flexibility
- OpenRouter, Ollama, MLX, or other local/remote routing
- TypeScript extensions
- top-down verifier loops
- peer Pi communication
- purpose gates, task discipline, or visible session widgets
- ephemeral execution and try-without-install behavior

Use Claude CLI when the job benefits from:

- Claude-native repository editing
- mature Claude Code hooks and skills
- Claude-specific planning/review workflows
- existing project Claude docs and commands

The Meta-Harness decides based on evidence, not loyalty to a tool.

## Pi extensions to incorporate

| Extension pattern | LATTICE use |
|---|---|
| `cross-agent` | load Claude/Gemini/Codex skills and commands into Pi sessions |
| `purpose-gate` | force session intent before harness jobs start |
| `tilldone` | track bounded tasks through completion |
| `agent-team` | dispatcher-style Pi teams when top-down delegation is appropriate |
| `agent-chain` | sequential pipelines where each state feeds the next |
| `coms` / `coms-net` | peer Pi communication on one machine, LAN, or remote hub |
| `damage-control` | Pi-side bash/path safety rules |
| `session-replay` | observable session timelines for debugging |

## Model-fit connection

Pi is the primary model-routing surface for model-fit benchmarks. Candidate models can be selected per task, with output scored by deterministic checks and verifier reports.

## Dry-run use

The first Meta-Harness dry run should use only the smallest useful extension stack:

```text
purpose-gate + tilldone + damage-control + verifier surface
```

Add teams, chains, and coms after the dry run proves the basic loop.
