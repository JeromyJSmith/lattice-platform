<!-- spec-verified: disler/bash-damage-from-within f639414 2026-05-12 -->
# IndyDevDan Incorporation Rule

LATTICE treats Disler / IndyDevDan repositories as compact operating doctrine and harness patterns to incorporate into the system, not as vendor blobs.

## Rule

When an IndyDevDan repository is selected for LATTICE:

1. Read it as a complete minimal pattern.
2. Preserve the core workflow instead of cherry-picking fragments.
3. Convert the pattern into LATTICE doctrine, scripts, harness jobs, or capability registries.
4. Keep provenance in docs and registries.
5. Do not vendor-copy the repo unless the repo's runtime code is itself required.

## Why

These repositories are intentionally concise. They are best-practice patterns for making agentic systems work: task delegation, verifier loops, bash safety, script-only execution, and model routing. The point is to incorporate the principle and operating shape into LATTICE so the whole system gets better.

## Incorporation checklist

For each selected repo:

| Step | Required output |
|---|---|
| Harvest | `analysis/capabilities/<repo>-capability-registry.yaml` |
| Doctrine | `meta/harness/` or `meta/verification/` doc explaining the incorporated rule |
| Execution | Repo-owned scripts, Pi jobs, or verifier tools when runtime behavior is needed |
| Verification | A deterministic command or report proving the incorporated pattern is active |
| Provenance | Source repo URL, commit SHA, harvest date |

## Current incorporated repos

| Repo | Incorporated as |
|---|---|
| `disler/the-verifier-agent` | Pi top-down observer pattern, verifier report/correction loop |
| `disler/bash-damage-from-within` | Bash safety ladder, L4/L5 policy for Pi and verifier jobs |
| `disler/the-library` | Private-first catalog for skills, agents, prompts, and harness jobs |
| `disler/install-and-maintain` | Executable install/maintenance docs: deterministic scripts plus agentic reports |
| `disler/fork-repository-skill` | Fork terminal delegation, context handoff, and parallel model/tool comparison |
| `disler/agent-sandbox-skill` | E2B sandbox skill, plan-build-host-test lifecycle, and browser validation prompts |
| `disler/agent-sandboxes` | E2B sandbox CLI/MCP/obox parallel fork workflows and sandbox observability |
| `disler/pi-vs-claude-code` | Pi extension stack, Pi-vs-Claude routing, teams/chains/coms, and damage-control patterns |
| `disler/claude-code-hooks-mastery` | Claude Code hook lifecycle, uv single-file hook scripts, and team validation |
| `disler/claude-code-hooks-multi-agent-observability` | Hook event streaming, SQLite event store, and multi-agent observability dashboard |
| `disler/claude-code-is-programmable` | Programmatic Claude Code as a Unix-style utility with allowed tool contracts |
| `disler/single-file-agents` | uv single-file task agents and provider-specific variants |
| `disler/agentic-drop-zones` | YAML-configured file event intake and agent dispatch workflows |
| `disler/benchy` | Live task-specific model benchmarking and report evidence |
