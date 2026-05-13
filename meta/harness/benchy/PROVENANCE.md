# Benchy Provenance

LATTICE incorporates Benchy as the visible model-fit benchmarking reference
corpus.

| Field | Value |
|---|---|
| Source repo | `https://github.com/disler/benchy` |
| Mirrored commit | `31e83770263ceee244718201567ab6d5d46b9569` |
| Mirror date | `2026-05-12` |
| Local mirror | `meta/harness/references/benchy/` |
| LATTICE console | `src/routes/harness/benchmarks.tsx` |
| LATTICE sidecar | `pixeltable/service/routes/harness.py` |

## Mirror Policy

This mirror keeps the Benchy source visible inside LATTICE while preserving
LATTICE's hard security rules.

Copied:

- client source, config, and styles
- Python server source and modules
- benchmark YAML fixtures
- saved JSON reports
- specs, docs, images, and Claude command references

Excluded:

- `.git/`
- `.env*`
- dependency directories
- generated build output
- virtual environments
- Python caches
- worktree directories
- local OS metadata

Runnable LATTICE code should still live in LATTICE-owned paths. Benchy source is
the visibility/reference corpus; promoted behavior is adapted into the FastAPI
sidecar, TanStack console, and harness scripts with provenance back to this
mirror.
