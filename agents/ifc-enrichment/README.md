# IFC Enrichment agent

Reads `lattice/bridge/ifc/ifc_elements` rows after VW Bridge writes them, fills in: BIS class/subclass (from [`itwin/bis-schemas/`](../../itwin/bis-schemas/)), georeferenced lat/lon (from IfcSite matrix), missing property sets, plant-species canonical names.

Idempotent — re-running over the same `source_element_id` is safe.

See [`AGENTS.md`](../../AGENTS.md) § Pixeltable bridge sub-project.
