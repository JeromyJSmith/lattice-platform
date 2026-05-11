# Reading `.bim` files in LATTICE

`.bim` is the iModel file format — a SQLite database with a specific schema (ECDb).

**LATTICE reads `.bim` files directly as SQLite via Pixeltable `@pxt.udf`.** We never use `@itwin/core-backend`, `SnapshotDb`, `BriefcaseDb`, or `IModelHost`.

## Why

- Pixeltable owns persistence. `core-backend` would create a second SQLite store, fight for the lock, and require IPC just to read.
- `.bim` is well-documented SQLite — the schema is published.
- A `@pxt.udf` SQLite reader is ~50 lines, runs inside the Pixeltable session, joins cleanly with `lattice/bridge/ifc/ifc_elements`.

## Implementation

[`bim-reader.py`](bim-reader.py) defines `bim_to_ifc_elements(bim_path) -> list[dict]` — a Pixeltable UDF that opens the `.bim` SQLite file, queries the `bis_GeometricElement3d` and adjacent tables, and yields rows ready to upsert into `lattice/bridge/ifc/ifc_elements`.

Backed by issue ".bim source ingestion" in the iTwin section of the backlog.
