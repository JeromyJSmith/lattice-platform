# iTwin Geometry — Usage Patterns

LATTICE uses `@itwin/core-geometry` for **all** non-trivial geometry math: coordinate transforms, placement, arc/spline parameterization, bounding boxes, frustum culling.

**Rule:** never raw float arrays for 3D positions. Always `Point3d`, `Vector3d`, `Transform`, `Range3d`, etc.

## Key types

| iTwin type | Replaces |
|---|---|
| `Point3d` | `{ x, y, z }` object literals, `[x, y, z]` arrays |
| `Vector3d` | direction tuples |
| `Transform` | manual 4×4 matrix multiplication |
| `Range3d` | `{ min, max }` bounding box objects |
| `Arc3d` | parametric curves for paths and arcs |
| `Matrix3d` | rotation matrices |

## Coordinate bridge

[`geo-transform.ts`](geo-transform.ts) is the canonical WGS84 ↔ iTwin-local ↔ Cesium ECEF bridge. Every conversion at the Pixeltable boundary or between the `/globe` and `/viewer` routes must go through it.

See [`meta/CESIUM_SETUP.md`](../../meta/CESIUM_SETUP.md) for the integration contract.
