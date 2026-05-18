# CWICR — Construction Work Items Cost Resources

55,719 construction cost items across 30 regions, 27 languages. Provided by the OpenConstructionEstimate-DDC-CWICR repo (https://github.com/datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR).

LATTICE uses CWICR as the **unit-cost source** for every `lattice/bridge/ifc/ifc_elements` row. Semantic search via Qdrant: element description → top-k cost items → write `unit_cost` + `unit_cost_region` back to Pixeltable.

## Files in this directory

| File | Purpose |
|---|---|
| [`INSTALL.md`](INSTALL.md) | One-time setup: OrbStack Ubuntu VM, Qdrant, and the live seed contract |
| [`seed-qdrant.sh`](seed-qdrant.sh) | Deterministic seed preflight — proves whether `cwicr` already satisfies the release contract |
| [`cost-search.py`](cost-search.py) | Python wrapper: takes an element description, returns ranked cost items |

## Runtime topology

```
LATTICE sidecar (Mac, port 7770)
  └─ POST /v1/erp/cost-search
       │
       ▼
  ddc/cwicr/cost-search.py (called via subprocess from FastAPI handler)
       │
       ▼
  Qdrant @ localhost:6333  (running inside OrbStack Ubuntu VM)
       │
       ▼
  55,719 cost items as Qdrant points with 3072-d snapshot embeddings
```

OrbStack maps `localhost:6333` from the VM to the Mac host transparently — no port forwarding setup beyond `orb start`.

The verifier-backed seed contract lives at [`../../scripts/verify-cwicr-seed.py`](../../scripts/verify-cwicr-seed.py). Today it proves a collection only when the local `cwicr` collection reaches 55,719 points and exposes the same 3072-dimensional vector contract as the upstream snapshot release. If the collection is still a demo stub or the restore path has not been run yet, the proof artifact stays red with explicit blockers instead of claiming a green seed.

Tracked in [`../../meta/FEATURE_BACKLOG.md`](../../meta/FEATURE_BACKLOG.md) § DDC INTEGRATION → "CWICR cost search".
