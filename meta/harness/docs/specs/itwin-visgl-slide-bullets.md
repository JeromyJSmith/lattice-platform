---
title: "iTwin + vis.gl Platform Architecture Spec — 28-Slide Bullet Outline"
type: "spec"
status: "reference"
historical_only: true
source: "Vectorworks_Bentley_iTwin_MARPA_Research_20260508/Dev_Stack/itwin-visgl-slide-bullets.md"
---
# Slide-Oriented Bullet Diagrams: iTwin + vis.gl Merger

## Slide 1 — Title
- iTwin.js + vis.gl
- Converged Landscape Digital Twin Platform
- Authoritative twin core + analytical overlay stack + landscape semantic layer

## Slide 2 — Why Merge
- iTwin solves synchronization, object identity, lifecycle context, and enterprise twin workflows
- vis.gl solves fast overlay rendering, exploratory geospatial layers, and transient drawing
- The missing product layer is landscape semantics: plants, irrigation, ecology, estimating, field ops, maintenance

## Slide 3 — Core Thesis
- Do not replace iTwin
- Do not persist overlay edits directly
- Compose three layers:
  - iTwin = system of record
  - vis.gl = analysis and draw surface
  - Landscape domain core = meaning, workflows, operations

## Slide 4 — Platform Stack Diagram
- L1 Authoritative Twin Core
  - synchronized iModels
  - object identity
  - version/change history
- L2 Landscape Semantic Core
  - plants
  - irrigation
  - terrain
  - ecology
  - maintenance
- L3 Overlay Runtime
  - thematic layers
  - point clouds
  - selection overlays
  - transient draw artifacts
- L4 Workflow Services
  - promotion
  - compare
  - telemetry fusion
  - estimating
- L5 Applications
  - twin viewer
  - field app
  - client portal
  - municipal handoff

## Slide 5 — Boundary Diagram
- iTwin owns:
  - persisted geometry
  - synchronized model state
  - authoritative IDs
  - long-term lifecycle records
- vis.gl owns:
  - GPU overlays
  - transient geometry
  - draw tools
  - compare visualization
- Domain core owns:
  - plant semantics
  - irrigation semantics
  - cost/maintenance/ecology records

## Slide 6 — Draw vs Persist
- Step 1: user draws polygon, line, point, lasso, or buffer
- Step 2: system stores DrawArtifact
- Step 3: validation checks geometry + semantics
- Step 4: user chooses promotion target
- Step 5: service commits scenario, issue, or authoritative request
- Step 6: twin and overlay both refresh

## Slide 7 — Promotion Targets
- overlay-only
- scenario record
- issue annotation
- landscape asset candidate
- maintenance zone candidate
- authoritative edit request

## Slide 8 — Compare Modes
- Temporal compare
  - version A vs version B
- Scenario compare
  - concept A vs concept B
- Source compare
  - model vs GIS vs field vs telemetry

## Slide 9 — Compare Output Diagram
- Left reference
- Right reference
- Diff engine evaluates:
  - geometry delta
  - semantic delta
  - telemetry delta
  - ecological metric delta
- Output:
  - visual highlight layer
  - side panel summary
  - exportable compare report

## Slide 10 — Domain Model
- PlantAsset
- ExistingTreeAsset
- PlantingArea
- IrrigationZone
- TerrainSurface
- HardscapeElement
- EcologicalMetricRecord
- QuantityTakeoffRecord
- CostEstimateRecord
- InstallationTask
- InspectionRecord
- MaintenanceEvent
- SensorObservation

## Slide 11 — Required Plant Fields
- assetId
- sourceElementId
- speciesCommonName
- speciesScientificName
- canopySpread
- expectedHeight
- healthStatus
- maintenanceScheduleRef
- ecologicalFunctionTags
- geometryRef
- telemetryBindings

## Slide 12 — Integration APIs
- CameraSyncAPI
- SelectionAPI
- OverlayRegistryAPI
- DrawAPI
- CompareAPI
- DomainSemanticAPI

## Slide 13 — API Flow Diagram
- camera changed -> publishCameraState -> overlay sync
- feature picked -> SelectionAPI -> unified selection state
- polygon drawn -> DrawAPI.createArtifact -> validation -> promoteArtifact
- compare requested -> CompareAPI.requestCompare -> diff result -> applyCompareView

## Slide 14 — Ingestion Reality Check
- Supported Bentley sync paths include interchange and geospatial formats such as ArcGIS Feature Service, KML, SHP, and LandXML
- No native VWX path is assumed in the first architecture
- IFC + sidecar semantics is the practical landscape bridge

## Slide 15 — Renderer Hardening
- Bentley acquired Cesium in September 2024
- Renderer strategy is now a moving platform target
- Therefore:
  - keep overlay contracts modular
  - avoid hard-coding a single long-term renderer dependency
  - preserve standards-friendly interfaces

## Slide 16 — Editable Layer Hardening
- nebula.gl established the pattern
- community migration indicates maintenance risk
- response:
  - abstract draw contracts internally
  - isolate dependency behind DrawAPI
  - treat editable layer implementation as swappable

## Slide 17 — Formal Phases
- Phase 0: validation and hardening
- Phase 1: dual-surface viewer
- Phase 2: draw and promotion
- Phase 3: semantic landscape core
- Phase 4: compare engine
- Phase 5: operations and telemetry
- Phase 6: standards and municipal handoff

## Slide 18 — Phase 0 Detail
- validate iTwin ingestion constraints
- validate editable-layer dependency risk
- validate Cesium-related renderer implications
- validate landscape semantic schema scope

## Slide 19 — Phase 1 Detail
- stand up iTwin viewport shell
- add vis.gl overlay runtime
- synchronize camera, selection, filters
- ship read-only thematic overlays

## Slide 20 — Phase 2 Detail
- implement DrawArtifact lifecycle
- support polygon/line/point/lasso tools
- add validation rules
- support promotion into scenarios and issue records

## Slide 21 — Phase 3 Detail
- implement canonical landscape schema
- ingest IFC + sidecar semantics
- bind geometry to operations records
- expose semantic panels and search

## Slide 22 — Phase 4 Detail
- build temporal compare
- build scenario compare
- build source compare
- export compare artifacts

## Slide 23 — Phase 5 Detail
- quantity takeoffs
- cost estimation
- installation tracking
- inspections
- irrigation telemetry
- client portal

## Slide 24 — Phase 6 Detail
- municipal handoff packages
- sustainability reporting
- compliance outputs
- interoperability testing

## Slide 25 — Risks
- no native VWX connector
- renderer churn post-Cesium acquisition
- editable-layer maintenance instability
- identity mismatch across geometry systems
- accidental misuse of overlays as system of record

## Slide 26 — Mitigations
- IFC + sidecar enrichment
- modular overlay contracts
- internal API abstraction over draw stack
- explicit identity bridge tables
- persistence only through authoritative workflows

## Slide 27 — Acceptance Criteria
- synchronized selection works across both surfaces
- draft geometry can be promoted and audited
- semantic enrichment survives interchange
- compare works on real project data
- operations workflows link assets to telemetry

## Slide 28 — Closing Diagram
- iTwin = truth
- vis.gl = interaction and analytics
- Landscape semantic core = the product moat
- Result = landscape-native digital twin platform
