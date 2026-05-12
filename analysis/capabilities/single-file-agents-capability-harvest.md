# Capability Harvest — single-file-agents

| Field | Value |
|---|---|
| Source repo | `https://github.com/disler/single-file-agents` |
| Reviewed commit | `ae5826a` |
| Harvest date | `2026-05-12` |
| LATTICE owner | Meta-Harness |

## Source Surfaces

| Capability | Source example | LATTICE use |
|---|---|---|
| uv inline metadata script | `sfa_poc.py` | Portable one-shot harness jobs |
| codebase context agent | `sfa_codebase_context_agent_w_ripgrep_v3.py` | Select task-relevant files before bounded work |
| meta-prompt agent | `sfa_meta_prompt_openai_v1.py` | Generate reusable prompt contracts |
| guardrailed agent runner | `openai-agents-examples/10_agent_with_guardrails.py` | Run bounded agents behind validation |
| data query agents | `sfa_duckdb_*`, `sfa_sqlite_openai_v2.py`, `sfa_polars_*` | Analyze explicit exported datasets |
| provider variants | OpenAI, Anthropic, Gemini examples | Benchmark model fit for a task |

## First Promotion Target

The first promoted target is a deterministic LATTICE-owned adaptation of the
codebase context pattern:

```text
meta/harness/tools/codebase-context-agent.py
```

The initial proof run starts metrics at zero and promotes only after the JSON
artifact passes verification.
