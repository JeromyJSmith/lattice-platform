# Local Harness AGENTS

This local harness scopes runtime behavior for the `VW_iTwin_Bridge` TanStack app body cell.

## Owned Pixeltable namespaces
- `lattice/execution/*` — runtime ledger (events, prompts, outcomes, evidence manifests, harness run refs).
- `lattice/bridge/*` — VW → IFC → iTwin alignment surfaces, MARPA parse runs, semantic sidecars, evidence promotion events, bridge health/gap matrix.

## Foreign namespaces (read-only)
- `marpa/*` — owned by `MARPA_PLATFORM`. The bridge consumes grammars and seed PSETs from the local `pixeltable/grammars/` mirror and writes parse outcomes to `lattice/bridge/marpa/*`, never to `marpa/*` directly.

## Sub-projects
- `pixeltable/` — uv-managed Python sub-project. Pinned `pixeltable==0.6.0`. FastAPI sidecar over UNIX socket (`/tmp/vwbridge-pxt.sock`); TS harness writes via `src/runtime/pixeltable/sidecar-client.ts`.

## Authoritative config
See `meta/config.yaml::pixeltable_bridge` for the full ownership manifest, sidecar transport, contract paths, and drift-gate locations.
