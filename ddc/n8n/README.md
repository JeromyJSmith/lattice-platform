# n8n Workflow Patterns

DDC ships its automation as n8n workflows: visual DAGs that orchestrate IFC/DWG extraction, LLM calls, code generation, and report assembly. The two source repos are:

1. **CAD-BIM-to-Code-Automation-Pipeline-DDC-Workflow-with-LLM-ChatGPT** — extraction + LLM pipelines
2. **Project-management-n8n-with-task-management-and-photo-reports** — field PM, Telegram bot, photo evidence

LATTICE does NOT run n8n. We translate n8n DAGs into native LATTICE FastAPI pipelines.

## Directory layout

| Path | What |
|---|---|
| [`workflows/`](workflows/) | n8n JSON exports, fetched from upstream DDC repos. Not committed — pulled by the sync script when implemented. |
| [`pipeline-templates/`](pipeline-templates/) | LATTICE-native equivalents. Each one is a FastAPI handler in `pixeltable/service/routes/` plus, optionally, Pixeltable computed columns. |

## Translation rules

| n8n node | LATTICE equivalent |
|---|---|
| HTTP Request | `httpx.AsyncClient` call in a FastAPI handler |
| Function (JS) | Pure Python function in the same handler |
| OpenAI Chat | `claude -p` subprocess via the worker's `_claude_cli_chunks` (no API key, see `worker.py`) |
| Spreadsheet | DuckDB WASM cell in a Marimo notebook, or `lattice/bridge/*` Parquet export |
| Schedule trigger | FastAPI background task + asyncio timer, or GitHub Actions `cron` (see `release.yml`) |
| Webhook | FastAPI route + Idempotency-Key header |
| Code (Python) | Direct import — most DDC n8n Python is already shaped like a `@pxt.udf` |

## Why translate, not import

n8n locks workflows behind its visual editor and a runtime daemon. A LATTICE FastAPI handler is:

- Source-controlled as plain Python
- Testable via `make test-no-pxt`
- Observable via the same `lattice/execution/*` ledger as every other agent run
- Free of an extra process to keep alive

The n8n JSON is useful as *executable documentation* of the intent, not as the runtime.

Tracked in [`../../meta/FEATURE_BACKLOG.md`](../../meta/FEATURE_BACKLOG.md) § DDC INTEGRATION → "DDC n8n workflow patterns".
