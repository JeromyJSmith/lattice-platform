# LATTICE Skills

LATTICE composes two skill sources:

1. **DDC skills** ([`ddc/`](ddc/)) — the 221 `SKILL.md` patterns from the DDC_Skills repo, adapted for LATTICE conventions. Reference, not invention.
2. **LATTICE skills** ([`lattice/`](lattice/)) — custom skills written for LATTICE's specific surfaces: `ifc-ingest`, `placeholder-create`, `cost-search`, `plant-style-assign`, etc.

Each subdir contains `SKILL.md` files that an AI runtime can load via the Skill protocol. Skills are tracked in `lattice/bridge/semantic/landscape_entities` for full-text + semantic search.

See [`AGENTS.md`](../AGENTS.md) and the DDC section of [`meta/FEATURE_BACKLOG.md`](../meta/FEATURE_BACKLOG.md).
