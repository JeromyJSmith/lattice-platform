# BIS Schemas in LATTICE

BIS = Base Infrastructure Schema, Bentley's class hierarchy for infrastructure. LATTICE uses BIS class names as **column values** in Pixeltable, not as imported types.

## Where BIS appears in LATTICE

| Pixeltable column | Example values |
|---|---|
| `lattice/bridge/ifc/ifc_elements.bis_class` | `BisCore:GeometricElement3d`, `BisCore:PhysicalElement`, `LandscapeElement` (future) |
| `lattice/bridge/ifc/ifc_elements.bis_subclass` | `Plant`, `Boulder`, `Pathway`, `WaterFeature`, `Furniture` (LATTICE-specific) |

## Why columns, not imports

Importing `@itwin/core-common` BIS types into the sidecar would pull `@itwin/core-backend`'s SQLite stack with it. LATTICE keeps BIS class names as plain strings so the contract stays portable and the iTwin dependency stays purely **frontend / geometry**.

## Custom landscape extensions (future)

`landscape/` will hold a custom LATTICE ECSchema (`Landscape.ecschema.xml`) that subclasses BIS `PhysicalElement` for plants, hardscape, water features, etc. Validation: `bis-schema-validation` from the iTwin org (see [`meta/ITWIN_MAPPING.md`](../../meta/ITWIN_MAPPING.md) Tier 5).
