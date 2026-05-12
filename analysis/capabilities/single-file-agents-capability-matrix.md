# Capability Matrix — single-file-agents

| Capability ID | Harness | Value | Risk | Decision | Proof run | Registry state after proof | Verification target | Tracking |
|---|---|---|---|---|---|---|---|---|
| `codebase-context-ripgrep` | `meta-harness` | `high` | `medium` | `candidate` | `pass` | `ACTIVE` | `uv run meta/harness/tools/codebase-context-agent.py --verify <artifact> --repo-root .` | `meta/harness/golden_path.md` |
| `meta-prompt-generator` | `meta-harness` | `medium` | `medium` | `defer` | `none` | `DEFERRED` | prompt schema + provider-key policy | future model-fit run |
| `guardrailed-agent-runner` | `meta-harness` | `high` | `high` | `defer` | `none` | `DEFERRED` | input guardrail fixture + sandbox policy | future sidecar run |
| `duckdb-analysis-agent` | `analytics-harness` | `high` | `medium` | `defer` | `none` | `DEFERRED` | Arrow/Parquet fixture over Pixeltable export | future Pixeltable export run |

## First Proof Target

```text
Goal: identify files relevant to changing a FastAPI sidecar route.
Expected: selected files include pixeltable/service/routes/harness.py and
meta/harness/single-file-harness-agents.md.
Verifier: codebase-context-agent --verify over the emitted JSON artifact.
```
