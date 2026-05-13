# Phase folders — capability research staging

Each phase is a holding area for research, candidate capabilities, and design notes
that aren't ready to land in a registry yet but shouldn't be forgotten.

| Phase | Folder | Purpose |
|---|---|---|
| 1 | `phase-1-foundation/` | Green-light items: zero-risk wiring, env exports, idempotent re-runs. Things that just need execution. |
| 2 | `phase-2-mapping/` | MAP-step content work: operator-workflow-map, source-acquisition-policy, operator-mapping-fields-template, per-row triage of advisory-stale registry rows. |
| 3 | `phase-3-substrate-upgrades/` | Architectural swaps that change how the harness runs: structured registry schema (wired_at / install_evidence / proof_evidence), Quack/OpenDuck remote DuckDB, schema-0017 candidates. |

## Promotion rules

Research → Capability registry follows the same `capability-harvest-protocol.md`
shape used everywhere else:

1. **Land research here first.** One markdown file per candidate, with claims,
   verification questions, and links to upstream docs/repos.
2. **Prove it.** A `_v1.py` SFA or harness artifact that demonstrates the
   capability end-to-end. Marker JSON + session JSON committed alongside.
3. **Register it.** Add a row to the appropriate `analysis/capabilities/*-capability-registry.yaml`
   with proof_evidence pointing at the session JSON.
4. **Never overwrite the predecessor.** New files only. The local-disk
   `sfa_duckdb_local_v1.py` stays as the baseline forever; the remote
   variant becomes `sfa_duckdb_quack_v1.py` or `sfa_duckdb_openduck_v1.py`.

## What's in here right now

- `phase-1-foundation/` — Phase 1 status notes (mostly complete as of 2026-05-13).
- `phase-2-mapping/` — pointers to the MAP artifacts already landed in `../mapping/`.
- `phase-3-substrate-upgrades/quack-openduck-research.md` — logged 2026-05-13. Not yet wired.
