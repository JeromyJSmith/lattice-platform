# VW + iTwin Bridge Harness — Session Memory

## Open Decisions

1. **Symbol instance geometry**: should each VW symbol instance carry its own shape data, or always reference Plant Style Manager? Current: always Style Manager (no per-instance geometry). Locks us into plant-scale workflows, which is desired, but constrains manual overrides.
2. **BIS class hierarchy depth**: how deep should we go? Plant → Landscape:PlantElement → Landscape:TreeElement → Species (too deep?). Current: 2 levels (class + subclass). May simplify to 1 level if downstream tools don't need the detail.
3. **Revit interop**: should we accept `.rvt` files + auto-export-to-IFC, or reject them outright? Current: reject. Deferred to Phase 2 if customer demand arises.

## Failed Experiments

- (placeholder — no failed experiments logged yet for this section)

## Session Handoff Notes

**Current state (2026-05-13)**: C++ VW plugin scaffolded, MCP bridge live. Python bridge (`vw-python/bridge.py`) fully functional. BIS schema reference loaded from `itwin/bis-schemas/BisCore.ecschema.xml`. Element enrichment logic in `vw-python/enrich.py` (90% complete, needs BIS taxonomy mapping table).

**Known issues**:
- Plant symbol naming convention not yet enforced by VW UI (placeholder check in enrich.py, needs VW validation)
- BIS class mapping table incomplete (~30% of common IFC classes mapped to BIS; rest fallback to base class)
- Plugin logging minimal (needs improve for troubleshooting; add syslog integration)
- Multi-user concurrent exports not yet tested

**Ready for next agent**: MCP bridge stable. Export pipeline ready for load testing. Element enrichment ready for taxonomy completion + bulk mapping. Symbol naming enforcement ready for VW plugin UI enhancement. Next: complete BIS taxonomy map, test multi-user export concurrency, profile plugin performance.
