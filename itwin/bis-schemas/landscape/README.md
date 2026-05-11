# Landscape BIS Schema (future)

This directory will hold `Landscape.ecschema.xml` — a custom ECSchema subclassing BIS `PhysicalElement` with LATTICE-specific landscape classes (Plant, Boulder, Pathway, WaterFeature, OutdoorFurniture, etc.).

Tracked in [`meta/FEATURE_BACKLOG.md`](../../../meta/FEATURE_BACKLOG.md) under iTWIN OPEN-SOURCE LAYER → `BIS vocabulary constants`.

Until the schema lands, BIS class strings used in `lattice/bridge/ifc/ifc_elements` are documented in `../README.md` and constrained by lint rules in the upsert path.
