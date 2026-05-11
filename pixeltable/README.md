# Pixeltable Bridge (VW <-> iTwin <-> MARPA)

Python sub-project that owns the `lattice.execution.*` and `lattice.bridge.*`
namespaces of the shared Pixeltable instance at
`PIXELTABLE_HOME=/Volumes/PixelTable/.pixeltable`.

This sub-project is the **only** place that holds an open Pixeltable session.
The TanStack/Bun harness in the parent repo never imports `pixeltable`; it
talks to the FastAPI sidecar in [`service/`](service/) over a UNIX socket
(`/tmp/vwbridge-pxt.sock`).

## Layout

```
pixeltable/
├── pyproject.toml           # uv-managed; pixeltable==0.6.0
├── Makefile                 # bootstrap | migrate-dryrun | migrate | fixture-load | verify | sidecar-up
├── contracts/               # versioned ingestion contracts (yaml/json schema)
├── grammars/                # MARPA grammar bundle (semver in VERSION)
├── migrations/              # idempotent table creators (numbered)
├── service/                 # FastAPI sidecar (the only PXT writer)
├── scripts/                 # bootstrap / verify / doctor entrypoints
└── tests/                   # pytest + fixtures
```

## Quick start

```bash
cd VW_iTwin_Bridge/pixeltable

# 1. Install Python deps into a local venv (managed by uv)
make bootstrap

# 2. Plan what would be created (no writes)
make migrate-dryrun

# 3. Apply migrations (idempotent; safe to re-run)
make migrate

# 4. Bring the sidecar up in the foreground
make sidecar-up
```

## Boundary invariant

- This sub-project **owns** `lattice/execution/*` and `lattice/bridge/*`.
- This sub-project **never touches** `marpa/*` (owned by MARPA_PLATFORM) or
  any other pre-existing `lattice/*` sub-namespace
  (e.g., `lattice/source`, `lattice/qa`).
- Migrations assert this invariant on startup; any overlap is a hard fail.

## Spec

See `.cursor/plans/pixeltable_bridge_alignment_05ebcec0.plan.md` for the
authoritative specification (column-level schemas, endpoint contracts,
acceptance gates).
