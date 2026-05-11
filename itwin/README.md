# iTwin LATTICE Integration Map

LATTICE uses iTwin as a **type system + vocabulary**, not as a viewer or cloud service.

| Subdir | What it owns |
|---|---|
| [`bis-schemas/`](bis-schemas/) | BIS class/subclass vocabulary used in Pixeltable columns; future custom LATTICE landscape ECSchema |
| [`geometry/`](geometry/) | `@itwin/core-geometry` usage patterns + the WGS84 ↔ iTwin-local ↔ Cesium ECEF coordinate bridge |
| [`imodel/`](imodel/) | How LATTICE reads `.bim` files (SQLite, via Pixeltable `@pxt.udf`) — no `@itwin/core-backend` |
| [`etl/`](etl/) | `imodel-transformer` patterns for extracting/merging iModel subsets |

**Cardinal rule:** No `@itwin/core-backend`. No `@itwin/imodels-clients`. No Bentley IMS / iModelHub / Reality Data cloud. LATTICE is self-hosted.

For the complete map of which iTwin GitHub repos LATTICE actually uses (Tier 1) vs reads as reference (Tier 2) vs skips entirely (Tier 4), see [`../meta/ITWIN_MAPPING.md`](../meta/ITWIN_MAPPING.md).

See [`AGENTS.md`](../AGENTS.md) for the iTwin invariants enforced across the platform.
