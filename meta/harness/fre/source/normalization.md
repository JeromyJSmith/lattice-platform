# Source normalization

## Rules

1. Treat the lifecycle gates contract as the sole authority for governance
   `gate_id` values.
2. Treat the proof-package parts inventory under `parts.*` as the sole evidence
   completeness ledger for this local slice.
3. Keep evaluation and promotion as separate proof-package parts.
4. Treat the prompt-contract artifact set as mandatory for every heavy or bounded
   execution prompt that touches this lane.
5. Fail closed on unresolved drift between schemas, examples, tests, and part
   inventories.
6. Record the scoped InfraNodus lifecycle rows and proof-part dependencies in
   `provenance.json` rather than inferring them from prose.

## Worktree translation

The sibling FRE worktree supplies the bounded patterns for:

- provenance discipline
- expected-failure discipline
- lattice translation mapping

This lane translates those patterns onto `main` without merging the three
authoritative contracts together.
