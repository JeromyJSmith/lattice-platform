# DDC Skills — Adapted for LATTICE

The DDC_Skills repo (https://github.com/datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction) ships 221 `SKILL.md` files covering construction-domain agent workflows: BIM analysis, cost estimation, scheduling, document control, quantity takeoff, clash detection, spec writing, procurement, site logistics.

LATTICE re-uses them in two ways:

1. **Copy the relevant subset here**, lightly adapted: paths rewritten to LATTICE conventions, DDC tool references replaced with LATTICE equivalents (Pixeltable, FastAPI sidecar, MCP).
2. **Index all 221 in Pixeltable** at `lattice/bridge/semantic/semantic_sidecars` with sentence-transformers embeddings, so any LATTICE agent can semantic-search "find skill for quantity takeoff" via pgvector similarity.

The clone/sync is intentionally not committed — `.gitkeep` only. The first agent task that picks this up runs the sync (see the matching GitHub issue).

## Priority skills for landscape architecture

When seeding the local copy, start with these (most relevant to LATTICE's site/landscape scope):

- Quantity takeoff from IFC
- Cost estimation from element properties
- Schedule phase extraction
- Element classification and validation
- Report generation from BIM data
- Specification writing from element properties

See [`../../meta/DDC_MAPPING.md`](../../meta/DDC_MAPPING.md) § Repo 1 for full background.
