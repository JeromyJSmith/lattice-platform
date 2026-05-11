// GeometryUtils.h — parametric shape builders used by PlaceholderCmd.

#pragma once

namespace lattice::geometry {

// Each helper creates the primitive in the active VW document at the given
// origin (world XY, world Z elevation) and returns the created object ID,
// or 0 on failure.

unsigned long CreateCone(double cx, double cy, double cz, double radius, double height);
unsigned long CreateHemisphere(double cx, double cy, double cz, double radius);
unsigned long CreateDisc(double cx, double cy, double cz, double radius);
unsigned long CreateBox(double cx, double cy, double cz, double w, double d, double h);
unsigned long CreateEllipsoid(double cx, double cy, double cz, double rx, double ry, double rz);
unsigned long CreateSlab(double cx, double cy, double cz, double w, double d, double thickness);

}  // namespace lattice::geometry
