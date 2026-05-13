---
description: Develop the VW C++ plugin (MCPBridge.cpp), Python bridge enrichment, and iTwin BIS class mapping for LATTICE; enforce no-Revit/no-DGN rules and symbol naming conventions. # allow-forbidden
---

# LATTICE VW Plugin and iTwin BIS Bridge

The vw-itwin section owns the Vectorworks C++ plugin source under `vw-plugin/src/`,
the Python bridge under `vw-python/`, BIS schema references under `itwin/bis-schemas/`,
and IFC element enrichment logic in `vw-python/enrich.py`. MCP IPC flows through
`MCPBridge.cpp` to the Python subprocess. The scoring script `scripts/score-vw-itwin.sh`
checks element catalog size, BIS class coverage, plugin health, and forbidden strings.

## When this skill applies

- Implementing or debugging `MCPBridge.cpp` IPC communication
- Enriching IFC elements with BIS class and subclass assignments
- Validating that all VW plant symbols follow `Genus_species_cultivar` naming
- Running the vw-itwin section cycle: `bash meta/harness/bootstrap/run-autoresearch.sh vw-itwin`
- `bis_class` or `bis_subclass` is null for rows in `lattice/bridge/ifc_elements`
- Plugin responds to `vw.ping` but not `vw.list_layers`

## How it works

1. Ping plugin health:
   ```bash
   python vw-python/bridge.py ping
   ```
   Expected: `{"status": "ok"}`. If offline, restart the VW Python plugin from
   the Vectorworks menu.

2. Audit element BIS coverage:
   ```python
   import pixeltable as pxt
   t = pxt.get_table("lattice/bridge/ifc_elements")
   unmapped = t.select(t.ifc_class, t.bis_class).where(t.bis_class == None).collect()
   print(f"{len(unmapped)} elements missing BIS class")
   ```

3. Enrich unmapped elements using `vw-python/enrich.py`:
   - `enrich.py` reads `ifc_class` from each row.
   - Looks up BIS equivalent in `itwin/bis-schemas/BisCore.ecschema.xml`.
   - Writes `bis_class` + `bis_subclass` back to Pixeltable.
   - Fallback: `bis_class='IfcBuildingElement'` for unknown IFC classes.

4. MCP tool call sequence for drawing read:
   ```
   vw.ping → vw.get_drawing_info → vw.list_layers →
   vw.list_objects_on_layer(<layer>) → vw.get_record_data(<obj_id>)
   ```
   All calls route through TCP `:9878` → vicquick/vwx-mcp → VW Python plugin.

5. Check for forbidden strings:
   ```bash
   git grep -i "revit\|microstation\|dgn\|bentley\|@itwin/core-backend\|pxt.Geometry" \ # allow-forbidden
     -- vw-plugin/ vw-python/ itwin/
   ```
   Must return empty (outside allow-listed docs files).

6. Validate plant symbol naming:
   ```bash
   git ls-files vw-plugin/resources/plant-symbols/ | grep -v "_" | wc -l
   ```
   Must be 0 — all symbols must follow `Genus_species_cultivar` convention.

7. Build VW C++ plugin (Mac):
   ```bash
   cd vw-plugin && cmake -B build/mac -G Xcode
   xcodebuild -project build/mac/*.xcodeproj
   ```
   Build output: `vw-plugin/build/mac/`.

8. IFC element enrichment — bulk update pattern:
   ```python
   rows_to_update = [
       {"source_element_id": row["source_element_id"],
        "bis_class": map_ifc_to_bis(row["ifc_class"]),
        "bis_subclass": map_ifc_to_bis_sub(row["ifc_class"])}
       for row in unmapped
   ]
   t.update(rows_to_update, where=t.source_element_id.isin([r["source_element_id"] for r in rows_to_update]))
   ```

## Files used

- `vw-plugin/src/MCPBridge.cpp` — C++ IPC entry point to Python bridge
- `vw-plugin/src/` — full plugin source tree
- `vw-plugin/build/mac/`, `vw-plugin/build/win/` — build outputs
- `vw-python/bridge.py` — Python bridge (ping, MCP dispatch, Pixeltable write)
- `vw-python/enrich.py` — BIS class enrichment logic
- `itwin/bis-schemas/BisCore.ecschema.xml` — authoritative BIS class reference
- `vw-plugin/GOAL.md` — vw-itwin section fitness function
- `pixeltable/service/routes/vw.py` — FastAPI routes for VW bridge operations
- `lattice/bridge/ifc_elements` — IFC element table (bis_class, bis_subclass required)
- `scripts/score-vw-itwin.sh` — section scoring script

## Constraints

- No Revit, MicroStation, DGN, or Bentley cloud workflows. IFC4.3 from Vectorworks 2026 # allow-forbidden
  is the only authoring input.
- Never use `@itwin/core-backend`, `SnapshotDb`, `BriefcaseDb`, or `IModelHost`. # allow-forbidden
  Use `@itwin/core-geometry`, `@itwin/core-common`, `@itwin/core-quantity` only.
- All VW plant symbols must follow `Genus_species_cultivar` naming. Per-instance
  geometry edits are prohibited; Plant Style Manager governs geometry.
- Collaborator Revit files must be exported to IFC4.3 before ingestion. # allow-forbidden
  Never accept `.rvt` as pipeline input.
- Coordinates must be EPSG-normalized through `ifcopenshell.util.placement`
  before any Pixeltable write. Never store raw VW internal coordinates.
- Always use IfcOpenShell for IFC parsing. Never parse IFC files manually.
- `vw.ping` must succeed before any other MCP call. If ping fails, the bridge
  is offline — restart and do not attempt other calls.
- Plugin crash logs are at `~/Library/Logs/Vectorworks/*.log`. Review before
  reporting crash-free status.
