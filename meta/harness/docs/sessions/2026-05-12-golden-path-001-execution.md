# Golden Path 001 Execution

## Goal

Promote and execute the first LATTICE-owned uv single-file harness agent:

```text
meta/harness/tools/codebase-context-agent.py
```

The proof target was a bounded codebase-context task for FastAPI sidecar route
work.

## Result

Status: PASS

The promoted script ran directly and through the registered FastAPI sidecar job
surface.

## Evidence

| Artifact | Purpose |
|---|---|
| `meta/harness/tools/codebase-context-agent.py` | Promoted LATTICE-owned uv single-file harness agent |
| `meta/harness/docs/sessions/2026-05-12-codebase-context-proof-run.json` | Direct script proof-run artifact |
| `meta/harness/docs/sessions/2026-05-12-codebase-context-sidecar-run.json` | Sidecar-executed proof-run artifact |
| `meta/harness/docs/sessions/2026-05-12-codebase-context-benchmark.json` | Benchy-compatible benchmark report |
| `analysis/capabilities/single-file-agents-capability-manifest.yaml` | Manifest row citing proof evidence |

## Commands

```bash
uv run meta/harness/tools/codebase-context-agent.py --task "Identify files relevant to adding or changing a FastAPI sidecar route for single-file harness agents and benchmark reports." --repo-root . --output meta/harness/docs/sessions/2026-05-12-codebase-context-proof-run.json --expect-path pixeltable/service/routes/harness.py --expect-path meta/harness/single-file-harness-agents.md

uv run meta/harness/tools/codebase-context-agent.py --verify meta/harness/docs/sessions/2026-05-12-codebase-context-proof-run.json --repo-root .

PYTHONPATH=pixeltable uv run --project pixeltable python <FastAPI TestClient harness>
```

## Sidecar Endpoint Result

```text
catalog 200 codebase-context-ripgrep active
run 200
ok True
artifact meta/harness/docs/sessions/2026-05-12-codebase-context-sidecar-run.json
verify_returncode 0
```

## Promotion Decision

`codebase-context-ripgrep` is now eligible for `ACTIVE` registry state because:

- source provenance is recorded
- the LATTICE-owned script runs with `uv run`
- the FastAPI sidecar catalog lists the registered job
- the FastAPI sidecar run endpoint executed the job
- verifier returned 0
- benchmark evidence exists
