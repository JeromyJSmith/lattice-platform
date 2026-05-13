# VW + iTwin Bridge Harness — LATTICE Meta-Harness Control

Owns C++ VW plugin source under `vw-plugin/src/`, Python VW bridge under `vw-python/`, iTwin BIS schemas under `itwin/bis-schemas/`, MCP IPC through `MCPBridge.cpp`, element enrichment (BIS class + subclass assignment).

## Fitness Function

Score VW bridge health against **element catalog completeness**, **BIS class coverage**, **plugin stability**, and **no forbidden strings**:

1. **IFC element catalog**: `SELECT COUNT(*) FROM lattice.bridge.ifc_elements` > 0 for active projects, every row has `bis_class` + `bis_subclass` non-null
2. **BIS schema fidelity**: every `bis_class` value exists in `itwin/bis-schemas/BisCore.ecschema.xml` (or extended schemas); no typos or undefined classes
3. **Plugin MCP health**: `vwx-mcp ping` returns success; plugin responds to `vw.get_drawing_info`, `vw.list_layers`, `vw.list_objects_on_layer`
4. **No forbidden strings**: `git grep -i "revit\|microstation\|dgn\|bentley\|@itwin/core-backend\|pxt.Geometry" -- vw-plugin/ vw-python/ itwin/` returns empty (outside allow-listed docs)
5. **Symbol/style naming**: all VW plant symbols follow `Genus_species_cultivar` convention (e.g., `Acer_palmatum_dissectum`); no hardcoded per-instance geometry
6. **Plugin crash-free**: no segfaults or unhandled exceptions in VW plugin logs for 100 consecutive element creations

**Baseline score**: `scripts/score-vw-itwin.sh` runs in < 5s, outputs JSON with `element_catalog_size`, `bis_class_coverage`, `plugin_health`, `forbidden_strings_count`.

## Improvement Loop

Autoresearch loop (on every VW export or element enrichment):

1. Run `scripts/score-vw-itwin.sh` → baseline snapshot
2. Auto-read `lattice.bridge.ifc_elements` table, identify rows with `bis_class=null` or `bis_subclass=null`
3. Spawn `claude -p` subprocess to map IFC class to BIS class using `itwin/bis-schemas/` and IfcOpenShell type definitions, generate bulk update SQL
4. Write mapping + update suggestions to `runtime-runs/<run-id>/vw-bridge-enrichment.md`
5. If BIS coverage > 95% after update, commit enrichment rows; else flag unmapped classes for manual review
6. Flock concurrency: max 1 enrichment job at a time via `/tmp/vwbridge-vw-itwin.lock`

## Action Catalog

- **Plugin status**: `python vw-python/bridge.py ping` returns OK or error details
- **Element audit**: `pixeltable select ifc_class, bis_class, count(*) from lattice.bridge.ifc_elements group by ifc_class, bis_class` shows mapping coverage
- **BIS schema validation**: `grep -c "bis_class\|bis_subclass" vw-python/enrich.py` should be > 0 (mapping logic present)
- **Symbol check**: `git ls-files vw-plugin/resources/plant-symbols/ | grep -v "_" | wc -l` should be 0 (all follow naming convention)
- **Crash logs**: `tail -100 ~/Library/Logs/Vectorworks/*.log | grep "LATTICE\|MCPBridge\|exception"` for recent errors

## Operating Mode

- **Plugin entry**: VW menu → "Generate LATTICE Placeholders" → C++ plugin calls `MCPBridge.cpp` → Python subprocess (`vw-python/bridge.py`) → Pixeltable write
- **IFC export**: VW export IFC4.3 → detect `IfcSite` + georeferencing → extract coordinate frame → normalize to WGS84 + local frame
- **Element enrichment**: `vw-python/enrich.py` reads IFC class, looks up BIS equivalent in `itwin/bis-schemas/`, assigns `bis_class` + `bis_subclass`, writes to Pixeltable
- **Symbol style control**: Plant Style Manager governs geometry; no per-instance edits. Symbol tree = 2D placeholder (LOD 100) + link to 3D asset (LOD 300 via `asset_id`)
- **Failure mode**: plugin crash → VW recovers, user retries export; BIS class missing → element marked `bis_class='IfcBuildingElement'` (fallback); MCP ping fails → bridge offline, needs restart
