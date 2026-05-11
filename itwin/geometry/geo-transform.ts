/**
 * Coordinate-system bridge for LATTICE.
 *
 *   WGS84 (lon/lat, deg + elev m)
 *      ⇅ ifcSiteToCesium
 *   Cesium Cartesian3 (ECEF, m)
 *      ⇅ siteTransform (4×4)
 *   iTwin local (Point3d, m, IfcSite origin)
 *
 * Always normalize to WGS84 + height-in-metres at the Pixeltable boundary.
 * The `marpa_projects` table stores (lat, lon, elevation_m) plus a JSON
 * site_transform column carrying the 4×4 matrix for any time we need to
 * project iTwin-local geometry back to world coordinates.
 *
 * Tracked in meta/FEATURE_BACKLOG.md § CESIUM GLOBE → "Coordinate system bridge".
 */

import { Point3d, Transform } from '@itwin/core-geometry'
// Cesium is loaded lazily to avoid pulling 5 MB into routes that don't need it.
// Callers import { Cartesian3 } where they need it.
type Cartesian3Like = { x: number; y: number; z: number }

/**
 * WGS84 (degrees + elevation in m) → Cesium ECEF Cartesian3.
 *
 * Caller is responsible for passing in the Cesium namespace so this module
 * stays import-free of cesium at the static-analysis layer.
 */
export function ifcSiteToCesium(
  refLatDeg: number,
  refLonDeg: number,
  refElevationM: number,
  Cartesian3: { fromDegrees(lon: number, lat: number, h: number): Cartesian3Like },
): Cartesian3Like {
  return Cartesian3.fromDegrees(refLonDeg, refLatDeg, refElevationM)
}

/**
 * iTwin-local point → world (still iTwin-local but with site offset applied).
 *
 * `siteTransform` is the 4×4 matrix derived from
 * `ifcopenshell.util.placement.get_local_placement(ifc_site)` on the
 * sidecar side, persisted in `marpa_projects.site_transform`.
 */
export function localToWorld(ifcLocalPoint: Point3d, siteTransform: Transform): Point3d {
  return siteTransform.multiplyPoint3d(ifcLocalPoint)
}

/**
 * Inverse — world point back to iTwin-local. Useful when picking on the
 * Cesium globe and resolving which IFC element you hit.
 */
export function worldToLocal(worldPoint: Point3d, siteTransform: Transform): Point3d {
  const inv = siteTransform.inverse()
  if (!inv) throw new Error('siteTransform is not invertible')
  return inv.multiplyPoint3d(worldPoint)
}

/**
 * Convenience: read a serialized 4×4 matrix from Pixeltable (stored as a
 * 16-number JSON array, row-major) and rebuild the iTwin Transform.
 */
export function siteTransformFromRowMajor(m: readonly number[]): Transform {
  if (m.length !== 16) {
    throw new Error(`siteTransform must be a 16-number row-major 4x4, got length ${m.length}`)
  }
  // iTwin's Transform.fromJSON wants origin + 3x3 matrix; rebuild from row-major.
  const origin = { x: m[3], y: m[7], z: m[11] }
  const matrix = [
    [m[0], m[1], m[2]],
    [m[4], m[5], m[6]],
    [m[8], m[9], m[10]],
  ]
  return Transform.fromJSON({ origin, matrix })
}

/**
 * Inverse — serialize an iTwin Transform back to row-major for storage in
 * `marpa_projects.site_transform`.
 */
export function siteTransformToRowMajor(t: Transform): number[] {
  const j = t.toJSON()
  const m = j.matrix
  const o = j.origin
  return [
    m[0][0], m[0][1], m[0][2], o.x,
    m[1][0], m[1][1], m[1][2], o.y,
    m[2][0], m[2][1], m[2][2], o.z,
    0,       0,       0,       1,
  ]
}
