# Phase 3 — substrate upgrades

Architectural moves that expand what the harness can do. Each one lands as
a new file alongside the working baseline — additive, never overwrites.

## Candidates logged

| Candidate | File | What it unlocks |
|---|---|---|
| Quack + OpenDuck (async remote DuckDB) | `quack-openduck-research.md` | Concurrent multi-agent access, browser/WASM reach, cross-source JOINs, differential storage |
| Registry schema upgrade (`wired_at` / `install_evidence` / `proof_evidence` as separate keys) | (to write) | Explicit evidence-kind in YAML — same semantics as the current path-pattern classifier, more legible |
| `schema-0017-candidates.md` | (to write) | New Pixeltable columns once multiple curated gap analyses run end-to-end |

## Rule

**Never overwrite a working file.** Every Phase 3 upgrade ships as a new
artifact next to the existing one. The local-disk `sfa_duckdb_local_v1.py`
stays as the baseline; remote variants ship as `sfa_duckdb_quack_v1.py` and
`sfa_duckdb_openduck_v1.py`. All three registry rows ACTIVE, A/B comparable
on the same prompt, all honest.
