# LATTICE Agents — Role Index

Each agent is a `SKILL.md` + supporting prompts/templates that an AI runtime (Claude CLI, Codex, etc.) loads to perform a specific job in LATTICE.

| Role | Path | Responsibility |
|---|---|---|
| Orchestrator | [`orchestrator/`](orchestrator/) | Routes tasks to specialized agents, owns the dispatch loop |
| VW Bridge | [`vw-bridge/`](vw-bridge/) | Vectorworks ↔ IFC ↔ Pixeltable ingestion |
| IFC Enrichment | [`ifc-enrichment/`](ifc-enrichment/) | BIS classification, geo-normalization, property cleanup |
| Geometry | [`geometry/`](geometry/) | Plant geometry generation, LOD swaps, mesh ops |
| Reality Capture | [`reality-capture/`](reality-capture/) | LiDAR / point cloud / drone capture pipelines |
| Research | [`research/`](research/) | Knowledge graph + literature retrieval for design decisions |
| Analytics | [`analytics/`](analytics/) | Cost, schedule, BOQ, deck.gl layer generation |

See [`AGENTS.md`](../AGENTS.md) (project root) and [`meta/AGENT_ONBOARDING.md`](../meta/AGENT_ONBOARDING.md) for the platform-level rules every agent must respect.
