# Meta-Harness Source Adoption Audit

This audit records what was read before the first Meta-Harness dry run and what
should be incorporated into LATTICE. The rule is conservative: keep source repos
as references unless runtime code is required to implement a specific LATTICE
behavior.

## Decision

Do not vendor the audited repositories wholesale into LATTICE.

Use them in three ways:

1. Copy exact contracts where the contract is the point, such as event envelopes,
   candidate outcome states, report blocks, benchmark YAML shapes, and
   proof-run gates.
2. Adapt runtime code only when a LATTICE feature needs it, such as sandbox
   path gating, hook event forwarding, or verifier IPC.
3. Reference tutorial/demo stacks externally when LATTICE already owns the
   equivalent surface through FastAPI, TanStack, Pixeltable, or repo scripts.

## Source Heads

| Source | Commit read | Incorporation level |
|---|---:|---|
| `stanford-iris-lab/meta-harness` | `95175f70c758` | Adopt outer-loop protocol and onboarding gates |
| `SuperagenticAI/metaharness` | `6e858aa4301d` | Adopt run-store, candidate ledger, outcome taxonomy, bootstrap snapshot |
| `jmilinovich/goal-md` | `8f39b8ab5afa` | Adopt ruler-first GOAL contract and score loop |
| `trevin-creator/autoresearch-mlx` | `ba6ebf6d3594` | Adopt fixed file, fixed metric, fixed budget, keep/discard loop |
| `disler/the-verifier-agent` | `aa18d68bcf88` | Adapt Pi builder/verifier observer runtime |
| `disler/bash-damage-from-within` | `f639414d3037` | Adapt L4/L5 bash safety ladder and attack tests |
| `disler/pi-vs-claude-code` | `3ce16391a1f4` | Adapt Pi extension stack as internal LATTICE task runner |
| `disler/the-library` | `47f455cd139b` | Adapt catalog pattern into `meta/harness/library.yaml` |
| `disler/install-and-maintain` | `558b5c8f5ebb` | Adapt deterministic script plus agent report pattern |
| `disler/fork-repository-skill` | `ba196f646bc9` | Adapt bounded delegation handoff pattern |
| `disler/agent-sandbox-skill` | `ac460eea626b` | Adapt plan-build-host-test-report lifecycle |
| `disler/agent-sandboxes` | `1a72555a3da4` | Extract minimal sandbox CLI/MCP/path-gating pieces only if needed |
| `disler/agentic-drop-zones` | `16a347bf60af` | Adapt YAML intake shape; productionize through queue/workers |
| `disler/claude-code-hooks-mastery` | `052ad1cbd5ae` | Adapt hook envelope and uv hook script pattern |
| `disler/claude-code-hooks-multi-agent-observability` | `8a6e5cf795df` | Adapt event schema and swimlane UI pattern, not SQLite/Vue stack |
| `disler/claude-code-is-programmable` | `388926529ccd` | Adapt programmable CLI runner pattern |
| `disler/single-file-agents` | `ae5826a4165c` | Adopt uv inline metadata single-file task agent pattern |
| `disler/benchy` | `31e83770263c` | Adapt benchmark YAML and evaluator structure |

## Exact Patterns To Preserve

### Meta-Harness Core

- Domain onboarding must be filled or marked `unknown` before implementation.
- Candidate runs must preserve baseline, candidate workspace, prompt, events,
  diffs, validation result, evaluation result, and manifest.
- Candidate outcomes should include at least `keep`, `discard`, `crash`,
  `timeout`, `no-change`, and `scope-violation`.
- Proposers make candidate changes; the outer loop validates and evaluates.
- Search-set and held-out evaluation must be distinct before claiming general
  improvement.

### GOAL and Autoresearch

- Build the scorer before optimizing the harness.
- Keep a deterministic metric with clear `score` and `max` output.
- Keep evaluation files fixed while allowing only the candidate surface to
  mutate.
- Use a fixed budget and explicit keep/discard decision.
- Record every attempt in append-only history.

### Capability Activation

Capability rows start at zero. Harvest and matrix rows can describe potential,
but a capability enters the manifest and registry only after a proof run
produces the desired outcome and writes evidence.

Promotion requires:

- runnable invocation
- expected output or outcome
- verifier or scoring command
- evidence artifact
- one passing proof run

After promotion, track pass rate, runtime, cost, model/provider, input shape,
output shape, and failure patterns.

### Pi Verifier and Bash Safety

- Pi is internal to LATTICE, not a separate top-level system.
- Use the builder/verifier observer pattern: lifecycle events over a socket,
  verifier reads session JSONL slice, verifier sends one corrective prompt and a
  structured report.
- Verifier bash should target L5: no arbitrary shell, only safe tools or
  repo-owned verification scripts.
- Adapt attack tests for LATTICE protected assets: `.env*`, landed migrations,
  `pxt.Geometry`, wrong migration path, destructive git, branch protection,
  merges to `main`, and secret exfiltration.

### Hooks, Single-File Agents, and Benchmarks

- Use a hook event envelope with `source_app`, `session_id`,
  `hook_event_type`, `payload`, `timestamp`, `model_name`, and promoted fields
  such as `tool_name`, `tool_use_id`, `agent_id`, `agent_type`, `error`,
  `is_interrupt`, and `reason`.
- Store hook events in Pixeltable/FastAPI surfaces, not the audited SQLite demo
  store.
- Use PEP 723 uv inline metadata for one-shot Python harness agents and hook
  scripts.
- Use benchmark packs with `benchmark_name`, `purpose`, `base_prompt`,
  `models`, `prompts`, `expectation`, and `evaluator`.

### Library, Sandboxes, and Drop Zones

- `meta/harness/library.yaml` is the durable catalog, not the proof manifest.
- Library references may point to repo, gist, doc page, workflow, skill, agent,
  prompt, or local script.
- Sandbox jobs should run in E2B/temp/worktree surfaces and write evidence back
  to LATTICE; do not make the sandbox state the source of truth.
- Drop zones are intake only. Every job needs output, archive, verification,
  Pixeltable target, and sandbox policy.

## What Not To Copy

- Demo Vue, SQLite, or TTS/audio stacks.
- Old model lists, pricing, or benchmark assumptions as authoritative data.
- Permission-bypass `justfile` patterns.
- Dynamic tool generation or broad Pi networking before the verifier substrate
  is mature.
- Single-file examples that use SQLite or DuckDB as durable stores.

## First Runtime Target

Build one LATTICE-owned proof-run path:

1. Define one benchmark/capability candidate in a YAML pack.
2. Run it through a uv single-file task agent or Pi safe tool.
3. Call `bash scripts/lattice-verify.sh HEAD` as the first oracle.
4. Write an evidence artifact under the wrapper run directory.
5. Promote the capability into manifest/registry only if the proof run passes.

