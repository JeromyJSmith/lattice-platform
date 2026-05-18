# CLAUDE instructions for the FRE main contract slice

Work only inside `meta/harness/fre/` unless a proof artifact explicitly calls
out a translation dependency elsewhere in the repo.

Hard rules:

1. Keep JSON Schema files on Draft 2020-12.
2. Use lifecycle `gate_id` values only from the governed seven-gate set:
   `harvest`, `registry`, `manifest`, `verification`, `state`, `health`,
   `promotion`.
3. Keep `evaluation` and `promotion` as distinct proof-package parts.
4. Use the proof-package inventory under `source/provenance.json` as the local
   completeness ledger.
5. Use `uv run --project pixeltable ...` for Python validation and tests.
6. No fake green states. If a fixture or schema drifts, fail closed.
