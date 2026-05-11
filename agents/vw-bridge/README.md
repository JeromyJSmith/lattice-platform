# VW Bridge agent

Owns the Vectorworks → IFC4.3 → Pixeltable path. Triggers `vw-plugin` menu commands, validates exported IFC, calls `POST /v1/vw/sidecars` on the FastAPI sidecar, and reports back via `agent_stream_events`.

Pixeltable tables: `lattice/bridge/vw/vectorworks_exports`, downstream `lattice/bridge/ifc/ifc_elements`.

See [`AGENTS.md`](../../AGENTS.md) and [`vw-plugin/README.md`](../../vw-plugin/README.md).
