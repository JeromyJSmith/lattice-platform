# Cesium Setup Decision

The `/globe` route is the MARPA project portfolio view: a CesiumJS globe with every project pinned to real terrain, click-to-load IFC models draped at correct lat/lon, and deck.gl analytical layers floating on top as toggleable overlays. Cesium + iTwin is **not an experiment** — Bentley officially ships `@itwin/core-frontend` with Cesium terrain support built in. `IfcSite.RefLatitude/RefLongitude/RefElevation` in every properly-georeferenced IFC file maps directly to `Cesium.Cartesian3.fromDegrees()`. The coordinate-system bridge is the only novel piece.

## Option A — Cesium ion (hosted, easiest)

- Sign up at https://ion.cesium.com (free tier: 5 GB assets).
- Get `CESIUM_ION_ACCESS_TOKEN`, add to `.env.local`.
- World Terrain + Bing imagery + Cesium OSM Buildings all included.
- Best for: quick start, photorealistic imagery.

```bash
# .env.local (server-side, also exposed to client via VITE_ prefix)
CESIUM_ION_ACCESS_TOKEN=eyJhbGciOiJI...
VITE_CESIUM_ION_ACCESS_TOKEN=eyJhbGciOiJI...
```

## Option B — Self-hosted (no vendor dependency)

- `cesium-terrain-builder` to generate quantized-mesh terrain tiles from USGS DEM data.
- Serve tiles from Bun static file server or Cloudflare R2.
- Use OpenStreetMap raster tiles for imagery (no API key).
- Best for: LATTICE's self-hosted philosophy, no token in repo.

```bash
# Generate terrain tiles from a DEM
ctb-tile -f Mesh -o ./public/cesium/terrain ./dem/usgs-3dep.tif
```

## Recommendation

Start with **Option A** (Cesium ion free tier) to prove the integration works. Migrate to **Option B** when token management becomes friction — likely once the platform has more than a handful of users or the asset volume exceeds 5 GB.

The Cesium API is identical either way; only the terrain/imagery URL changes. Code change to migrate is ~3 lines in `src/routes/globe/index.tsx`.

## iTwin + Cesium integration

Bentley's `@itwin/core-frontend` has built-in Cesium terrain support. The key bridge:

```ts
// src/lib/geo-transform.ts
import { Cartesian3 } from 'cesium'
import { Point3d, Transform } from '@itwin/core-geometry'

export function ifcSiteToCesium(
  refLatDeg: number,
  refLonDeg: number,
  refElevationM: number,
): Cartesian3 {
  return Cartesian3.fromDegrees(refLonDeg, refLatDeg, refElevationM)
}

export function localToWorld(
  ifcLocalPoint: Point3d,
  siteTransform: Transform,
): Point3d {
  return siteTransform.multiplyPoint3d(ifcLocalPoint)
}
```

The `siteTransform` comes from the IFC parse — `ifcopenshell.util.placement.get_local_placement(ifc_site)`. We persist its 4×4 matrix on the `marpa_projects` row alongside `lat`, `lon`, `elevation_m` so the frontend never needs to re-parse IFC just to place a model on the globe.

## npm packages needed

| Package         | Version    | Role                                         |
|-----------------|-----------|----------------------------------------------|
| `cesium`        | ^1.125.0   | Core CesiumJS                                |
| `@cesium/engine`| optional   | Lower-level API if we need raw shaders       |
| `resium`        | ^1.19.0    | React wrapper for CesiumJS (R3F-equivalent)  |
| `@deck.gl/cesium` | 9.3.2    | deck.gl ↔ Cesium integration layer          |

Already in stack: `@deck.gl/core`, `@deck.gl/layers`, `@itwin/core-geometry`, `@thatopen/components`, `@thatopen/fragments`.

## Asset / static-file layout (Cesium ion path)

```
public/cesium/
  Workers/                     ← Cesium web workers (vendored from node_modules/cesium/Build/Cesium/Workers)
  Assets/                      ← Cesium static assets (vendored similarly)
  Widgets/                     ← Cesium widget CSS
```

Vite plugin `vite-plugin-cesium` automates the vendoring. Add it to `vite.config.ts` when the globe route lands.

## Coordinate-system contract

| System          | Used by              | Units      | Origin                              |
|-----------------|----------------------|------------|--------------------------------------|
| WGS84 (lon/lat) | Cesium camera, pins  | degrees    | Greenwich / equator                 |
| ECEF Cartesian3 | Cesium internals     | metres     | Earth centre                        |
| Local IFC       | IFC product geometry | metres     | IfcSite                              |
| iTwin BIS       | BIS class queries    | dimensionless | n/a (it's a schema, not a CRS)    |

Always normalise to **WGS84 + WGS84 height in metres** at the Pixeltable boundary. The `marpa_projects` table stores `lat REAL NOT NULL, lon REAL NOT NULL, elevation_m REAL NOT NULL` and never raw IFC coordinates. The `site_transform` JSON column carries the 4×4 matrix for any time we need to project IFC local → world.

## Why this is "executive dashboard AND field operations view"

The same `/globe` route powers both:

- **Executive view** (default) — globe-scale zoom, all projects visible, pins coloured by status, click pin for project info card with cost/schedule snapshot.
- **Field view** (`/globe/field`) — mobile-friendly, single-project focus, large status buttons for on-site updates, today's tasks pulled from Linear.

The data layer is identical. The viewport scale and chrome differ. Both ride on the same `marpa_projects` table and the same SSE-fed project status updates from Linear.
