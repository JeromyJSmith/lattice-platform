# iTwin GitHub Org — LATTICE Relevance Map
# 84 public repos mapped to LATTICE usage tiers
# Source: github.com/orgs/iTwin/repositories (verified May 2026)
# Rule: Self-hosted open source only. No Bentley cloud. No IMS auth.

---

## TIER 1 — ACTIVELY USED IN LATTICE (install these)

| Repo | npm package | What LATTICE uses it for |
|---|---|---|
| itwinjs-core | @itwin/core-geometry, @itwin/core-common, @itwin/core-quantity, @itwin/core-bentley | BIS vocabulary for Pixeltable columns; Point3d/Transform/Arc3d geometry math; coordinate systems |
| bis-schemas | (XML reference, not npm) | BIS class/subclass vocabulary for ifc_elements table; landscape element classification |
| presentation | @itwin/presentation-common, @itwin/presentation-frontend | Hierarchy and content rules for element property display in viewer |
| iTwinUI | @itwin/itwinui-react | UI components for admin/viewer panels (optional — shadcn is primary) |
| appui | @itwin/appui-react | Toolbar/widget framework for ThatOpen viewer integration (optional) |
| imodel-transformer | @itwin/imodel-transformer | Extract plant-element subsets from large iModels; merge iModels from collaborators |
| changed-elements-react | @itwin/changed-elements-react | Version comparison UI — show what changed between two VW exports |
| saved-views | @itwin/saved-views-react | Save/restore camera positions and element visibility states in LATTICE viewer |
| insights-client | @itwin/insights-client | Carbon calculation and reporting overlays (future sustainability layer) |

---

## TIER 2 — REFERENCE / PATTERNS (read but don't install)

| Repo | What to extract |
|---|---|
| connector-framework | Connector architecture patterns — how to build a VW→iModel connector (future C++ plugin pattern) |
| connector-samples | Sample connector implementations — reference for VW bridge agent |
| pcf (Digital Twin as Code) | Infrastructure-as-code patterns for iModel schema management |
| etl-samples | Export/transform/import patterns for iModel data — maps to LATTICE's IfcOpenShell pipeline |
| imodel-reporter | Query patterns for extracting structured reports from iModel ECDb — maps to Pixeltable query patterns |
| agent-starter | iTwin agent architecture patterns — maps to LATTICE agent roles |
| synchronization-manifest-api-sample | Sync job patterns — reference for itwin_sync_jobs table design |
| iot-demo | Real-time sensor data overlay on iModel — future sensor/environmental layer in LATTICE |
| viewer-components-react | BIM component patterns — ClashReview, GroupingMapping, MeasurementTools reference |
| presentation-rules-editor | How presentation rules work — useful for LATTICE property panel design |
| imodel-native | C++ iModel API — reference for VW C++ plugin's geometry and placement math |
| auth-clients | OAuth2/OIDC patterns — reference only; LATTICE uses Better Auth not Bentley IMS |
| itwin-cli | CLI patterns for iModel automation — reference for LATTICE scripts/ commands |
| insights-api-sample-console-app | Carbon/reporting workflow patterns |
| admin-components-react | Admin UI patterns for iTwin apps — reference for LATTICE /admin route |

---

## TIER 3 — CESIUM INTEGRATION (use for /globe route)

| Repo | What LATTICE uses it for |
|---|---|
| cesium-native | C++ Cesium runtime — powers @itwin/core-frontend's terrain rendering |
| itwin-cesium-tutorial-app | Starter app showing Cesium + iTwin integration — reference for /globe route |
| cesium-curated-content-samples | 3D Tiles from Cesium ion — reference for self-hosted tile serving |
| 3d-tiles-samples | Mesh Export API → 3D Tiles → Cesium — future path for serving LATTICE IFC models as 3D Tiles |

---

## TIER 4 — SKIP (Bentley cloud / IMS auth required)

These repos require Bentley cloud infrastructure, iModelHub, or IMS authentication.
LATTICE is self-hosted. Do not install or depend on these.

| Repo | Why skipped |
|---|---|
| viewer | @itwin/web-viewer-react requires Bentley IMS auth and iModelHub |
| imodels-clients | iModelHub cloud API client — LATTICE uses Pixeltable not iModelHub |
| demo-portal | Bentley cloud portal demo |
| reality-capture | Bentley Reality Data cloud API — LATTICE uses PDAL/Open3D locally |
| itwins-client | iTwin Platform cloud API |
| projects-client | Bentley Projects cloud API |
| access-control-client | Bentley cloud access control |
| reality-data-client | Bentley cloud reality data |
| mobile-sdk-android | Mobile — out of scope |
| mobile-sdk-ios | Mobile — out of scope |
| mobile-samples | Mobile — out of scope |
| mobile-ui-react | Mobile — out of scope |
| mobile-native-android | Mobile — out of scope |
| mobile-native-ios | Mobile — out of scope |
| imodels-api-management-workflow-sample-app | iModelHub cloud workflow |
| project-api-sample-app | Deprecated Bentley cloud projects API |
| synchronization-report-react | Requires Bentley synchronization service |
| transformations-api-sample | Requires Bentley transformation cloud service |
| webhooks-api-samples | Bentley Platform webhooks |
| webhooks-api-polling-sample-app | Bentley Platform webhooks |
| platform-api-samples | Bentley Platform APIs |
| platform-api-documentation | Bentley Platform API docs |
| storage-api-sample-app | Bentley cloud storage |
| grouping-and-mapping-sample-app | Requires Bentley Grouping and Mapping service |
| iTwin-api-sample-app | Bentley Platform API |
| library-api-sample-app | Bentley cloud library API |
| Course_1-Smart-House-Sample | Educational — uses cloud platform |
| Course-Property-Validation-API | Educational — uses cloud platform |
| Course-Intro-iTwin-Platform-APIs | Educational — uses cloud platform |

---

## TIER 5 — TOOLING / INFRASTRUCTURE (use as needed)

| Repo | What it provides |
|---|---|
| bis-schema-validation | Validate custom BIS schema extensions — use when LATTICE adds landscape ECSchema |
| ecjson2md | Generate Markdown from ECSchema — document LATTICE's BIS vocabulary |
| eslint-plugin | iTwin ESLint rules — add to LATTICE biome/eslint config |
| codemods | iTwin API migration codemods — useful when upgrading @itwin/* package versions |
| stratakit | Component toolkit — evaluate for LATTICE UI components |
| react-hooks | Generic React hooks from iTwin team — evaluate for useIModel, usePresentation patterns |

---

## KEY INSIGHT: What iTwin Actually Gives LATTICE

LATTICE does NOT use iTwin as a viewer platform or cloud service.
LATTICE uses iTwin as a TYPE SYSTEM and VOCABULARY:

1. BIS schemas (bis-schemas repo) → column names and values in Pixeltable
2. @itwin/core-geometry → Point3d, Transform, Arc3d for precise geometry math
3. @itwin/core-common → BIS element types, Code specs, Placement3d
4. imodel-transformer → Extract/merge iModel subsets (batch processing, not viewer)
5. Cesium integration → /globe route georeferenced project portfolio

The .bim file format is SQLite. LATTICE reads it directly via Pixeltable @pxt.udf.
No SnapshotDb. No BriefcaseDb. No IModelHost. No Bentley cloud.
