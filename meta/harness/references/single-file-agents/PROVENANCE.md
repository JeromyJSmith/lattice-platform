# single-file-agents Provenance

LATTICE incorporates the patterns from
`https://github.com/disler/single-file-agents`, not the upstream repository as a
runtime vendor dump.

| Field | Value |
|---|---|
| Source repo | `https://github.com/disler/single-file-agents` |
| Reviewed commit | `ae5826a` |
| First promoted pattern | `sfa_codebase_context_agent_w_ripgrep_v3.py` |
| LATTICE adaptation | `meta/harness/tools/codebase-context-agent.py` |
| Incorporation mode | LATTICE-owned adaptation with source provenance |

Reference source may be mirrored here later after an explicit sync policy strips
`.git`, `.env*`, local caches, demo databases, generated artifacts, and provider
secrets. Runnable scripts must live in LATTICE-owned paths under
`meta/harness/tools/` and pass local docstring and verifier gates.
