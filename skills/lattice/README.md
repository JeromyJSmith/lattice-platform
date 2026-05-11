# LATTICE Skills (custom)

LATTICE-specific skills, each one a `SKILL.md` file that an AI runtime can load. Examples once populated:

- `ifc-ingest/` — Parse an IFC, normalize coordinates, upsert into `lattice/bridge/ifc/ifc_elements`
- `placeholder-create/` — Generate LOD 100 placeholder geometry via the C++ plugin
- `cost-search/` — Query CWICR cost database via Qdrant for a given plant species
- `plant-style-assign/` — Assign a Plant Style Manager entry to all instances of a species
- `globe-fly-to/` — Trigger `/globe` fly-to animation for a MARPA project

Each skill must declare in its frontmatter: which Pixeltable tables it touches, which sidecar endpoints it calls, and which agent role from [`agents/README.md`](../../agents/README.md) is expected to invoke it.
