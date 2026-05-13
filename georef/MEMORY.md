# Georeferencing + Reality Capture Harness — Session Memory

## Open Decisions

1. **Coordinate reference authority**: who is the source of truth for project CRS? Should be VW export + IfcSite georeferencing, but fallback to survey data. Need to decide precedence order: IFC > Survey > Inferred from bounds.
2. **Mirror reconciliation strategy**: when drone reality capture drifts from design IFC, how many mm tolerance before flagging sync_warning? Current: 50mm. May tighten to 25mm if precision permits.
3. **Reality capture tile format**: potree-core JSON vs tiled LAZ for point cloud distribution? Current: JSON (smaller, web-friendly). May switch to LAZ + proxy if performance requires.

## Failed Experiments

- (placeholder — no failed experiments logged yet for this section)

## Session Handoff Notes

**Current state (2026-05-13)**: 7 converter stubs scaffolded in `georef/converters/`. EPSG normalization logic drafted in `georef/utils/normalize.py`. Reality capture pipeline stubs live in `georef/reality/` (drone, splat, pointcloud, mirror). PostGIS spatial index creation deferred to migration 0014.

**Known issues**:
- Shapefile converter needs fiona/pyproj integration (not yet added to `pyproject.toml`)
- OSM converter needs Overpass API client (stub only)
- Drone frame extraction not yet wired to PDAL (uses ffmpeg placeholder)
- Mirror state reconciliation logic exists but untested under real drift scenarios

**Ready for next agent**: Converter templates ready for implementation. EPSG + PostGIS patterns established. Reality capture skeleton ready for Laspy/PDAL integration. Next: implement converters one-by-one, add Pixeltable migration 0014 for spatial indexes.
