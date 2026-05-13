<!-- spec-verified: disler/single-file-agents ae5826a 2026-05-12 -->
# Single-File Harness Agents

LATTICE uses uv single-file harness agents for small repeatable tasks.

## Rule

A single-file harness agent should:

- do one thing
- carry its dependencies in uv inline script metadata when Python-based
- accept explicit input
- emit one bounded artifact
- avoid hidden global state
- expose a verification command
- be registered in the library when reusable
- include module and function docstrings

## Python default

For Python harness jobs, the default shape is a uv single-file script:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""One-sentence module docstring explaining the harness job."""


def main() -> int:
    """Run the one-shot harness job and return a process exit code."""
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

This gives us a portable "one-up" execution unit: `uv run path/to/script.py` works locally, in Pi, in E2B, and in ephemeral sandboxes without polluting the repo environment.

The script may call an agent or model inside it, but the script still owns the input shape, output artifact, and verification boundary.

## Sidecar endpoint model

Single-file agents are not exposed as free-form callable tools. The FastAPI
sidecar owns the public surface and dispatches registered scripts as bounded
harness jobs.

Initial endpoint shape:

```text
GET  /v1/harness/single-file-agents/catalog
POST /v1/harness/single-file-agents/runs
GET  /v1/harness/single-file-agents/runs/{run_id}
GET  /v1/harness/single-file-agents/runs/{run_id}/events
```

Only the catalog endpoint is live initially. The run endpoints must enforce:

- registered script IDs only
- explicit input schema
- timeout
- sandbox/workdir policy
- captured stdout, stderr, exit code, and artifact path
- Pixeltable/evidence write
- no inherited secrets except the named provider keys required by that script

The operator console should call the sidecar endpoints and visualize the report;
it should not execute scripts directly in the browser.

## Docstring enforcement

Every new or changed Python script must include a module docstring and docstrings on public functions, classes, and methods. The local gate is:

```bash
uv run python scripts/check-python-docstrings.py
```

Use `--base <ref>` for PR-style changed-file checks and `--all` only when deliberately paying down the full legacy baseline. Landed migrations `0001` through `0016` remain write-once and are excluded from automated docstring rewrites.

## Good targets

| Task class | Example |
|---|---|
| JSON processing | generate or validate `jq` transformations |
| SQLite/DuckDB queries | constrained local data analysis |
| CSV transforms | Polars-based one-shot analysis |
| prompt generation | create a reusable prompt from purpose/sections/examples |
| docs extraction | scrape or summarize a known source into a known artifact |

## Model-fit connection

Single-file agents are ideal benchmark units. The same task can have provider-specific variants, and the Meta-Harness can measure accuracy, latency, cost, and artifact validity.

## Repository policy

Do not create a new service for a one-shot harness task. Start with a single file. Promote only after repeated use proves the abstraction is needed.

Disler's `single-file-agents` repository should be incorporated as a LATTICE
tool source, not treated as a generic vendor blob. The source repo can be
mirrored for reference, but runnable scripts should be promoted into
LATTICE-owned paths under `meta/harness/tools/` with provenance, docstrings,
explicit CLI arguments, and a sidecar endpoint registration.
