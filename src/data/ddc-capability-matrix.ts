export type DdcPriority = "high" | "medium" | "low";
export type DdcWave = "wave-1" | "wave-2" | "wave-3" | "wave-4";

export type DdcSurface = {
  id: string;
  name: string;
  localHome: string;
  classification: string;
  adoptionMode: string;
};

export type DdcCapability = {
  id: string;
  capability: string;
  localHome: string;
  targetSurface: string;
  currentState: string;
  gap: string;
  priority: DdcPriority;
  wave: DdcWave;
  validation: string;
};

export type DdcPipelineStage = {
  id: DdcWave;
  name: string;
  capabilityIds: Array<string>;
};

export const ddcSurfaces: Array<DdcSurface> = [
  {
    id: "ddc-skills",
    name: "DDC Skills corpus",
    localHome:
      "/home/runner/work/lattice-platform/lattice-platform/ddc/skills/README.md",
    classification: "direct runtime feature",
    adoptionMode: "adapted to LATTICE",
  },
  {
    id: "cwicr",
    name: "CWICR cost intelligence",
    localHome:
      "/home/runner/work/lattice-platform/lattice-platform/ddc/cwicr/README.md",
    classification: "data enrichment service",
    adoptionMode: "adapted to LATTICE",
  },
  {
    id: "openconstructionerp",
    name: "OpenConstructionERP",
    localHome:
      "/home/runner/work/lattice-platform/lattice-platform/ddc/erp/README.md",
    classification: "direct runtime feature",
    adoptionMode: "adapted to LATTICE",
  },
  {
    id: "n8n-patterns",
    name: "n8n workflow patterns",
    localHome:
      "/home/runner/work/lattice-platform/lattice-platform/ddc/n8n/README.md",
    classification: "pipeline template source",
    adoptionMode: "adapted to LATTICE",
  },
  {
    id: "admin-dashboard",
    name: "DDC admin dashboard",
    localHome:
      "/home/runner/work/lattice-platform/lattice-platform/ddc/admin/README.md",
    classification: "ui/admin feature",
    adoptionMode: "adapted to LATTICE",
  },
  {
    id: "converters",
    name: "Linux fallback converters",
    localHome:
      "/home/runner/work/lattice-platform/lattice-platform/ddc/converters/README.md",
    classification: "fallback operator tool",
    adoptionMode: "intentionally limited",
  },
];

export const ddcCapabilities: Array<DdcCapability> = [
  {
    id: "skills-harvest",
    capability: "Skill corpus harvest",
    localHome:
      "/home/runner/work/lattice-platform/lattice-platform/ddc/skills/",
    targetSurface:
      "/home/runner/work/lattice-platform/lattice-platform/skills/ddc/",
    currentState: "Docs only; sync pending",
    gap: "Pull the upstream skill corpus into the local skill tree.",
    priority: "high",
    wave: "wave-1",
    validation:
      "Skill count and metadata completeness match the harvested inventory.",
  },
  {
    id: "skills-semantic-index",
    capability: "Skill semantic indexing",
    localHome:
      "/home/runner/work/lattice-platform/lattice-platform/pixeltable/contracts/bridge-semantic.v1.yaml",
    targetSurface: "lattice/bridge/semantic/semantic_sidecars",
    currentState: "Semantic infra exists; DDC seed missing",
    gap: "Ingest skill documents into semantic_sidecars with embeddings.",
    priority: "high",
    wave: "wave-1",
    validation:
      "Semantic search returns DDC skill matches for construction intents.",
  },
  {
    id: "skills-search-api",
    capability: "Skill search API",
    localHome:
      "/home/runner/work/lattice-platform/lattice-platform/pixeltable/service/routes/semantic.py",
    targetSurface: "POST /v1/semantic/search",
    currentState: "Live generic semantic search",
    gap: "Add DDC-aware query presets and filters.",
    priority: "medium",
    wave: "wave-3",
    validation:
      "DDC skill queries resolve against semantic_sidecars with usable rankings.",
  },
  {
    id: "cwicr-seed",
    capability: "CWICR dataset seeding",
    localHome:
      "/home/runner/work/lattice-platform/lattice-platform/ddc/cwicr/seed-qdrant.sh",
    targetSurface: "Qdrant collection cwicr",
    currentState: "Verifier-backed seed preflight; live proof failing",
    gap: "Local cwicr collection is only 5 points at 64 dimensions; the release contract expects a 55,719-point 3072-d snapshot-backed collection.",
    priority: "high",
    wave: "wave-1",
    validation:
      "Qdrant point count is 55,719 and the collection vector size matches the release snapshot contract (3072).",
  },
  {
    id: "cwicr-cost-search",
    capability: "CWICR semantic cost lookup",
    localHome:
      "/home/runner/work/lattice-platform/lattice-platform/ddc/cwicr/cost-search.py",
    targetSurface: "POST /v1/erp/cost-search",
    currentState: "Verifier-backed route; live proof currently failing",
    gap: "localhost:6333 is not serving the expected Qdrant /health contract for live proof.",
    priority: "high",
    wave: "wave-1",
    validation:
      "Element descriptions return region-filtered ranked CWICR matches with passed verification.",
  },
  {
    id: "ifc-cost-enrichment",
    capability: "IFC cost enrichment",
    localHome:
      "/home/runner/work/lattice-platform/lattice-platform/pixeltable/migrations/0012_extended_schema.py",
    targetSurface:
      "lattice/bridge/ifc/ifc_elements.{unit_cost,unit_cost_region,cost_last_updated}",
    currentState: "Schema columns exist",
    gap: "Write search results back into owned Pixeltable rows.",
    priority: "high",
    wave: "wave-2",
    validation:
      "ifc_elements rows show unit cost, region, and freshness timestamps.",
  },
  {
    id: "boq-sync",
    capability: "BOQ creation and sync",
    localHome:
      "/home/runner/work/lattice-platform/lattice-platform/ddc/erp/boq-adapter.py",
    targetSurface: "POST /v1/erp/boq",
    currentState: "Adapter stub",
    gap: "Project IFC rows into ERP payloads and persist returned ERP identifiers.",
    priority: "high",
    wave: "wave-2",
    validation: "Every BOQ-attached element has erp_item_id and unit_cost.",
  },
  {
    id: "boq-read",
    capability: "BOQ retrieval",
    localHome:
      "/home/runner/work/lattice-platform/lattice-platform/ddc/erp/boq-adapter.py",
    targetSurface: "GET /v1/erp/boq/{project_id}",
    currentState: "Verifier-backed route; live proof currently failing",
    gap: "localhost:8080 returns 404 for GET /api/boq/{project_id}; live ERP BOQ contract or verifier project data is not ready.",
    priority: "high",
    wave: "wave-2",
    validation: "Project BOQ round-trips cleanly through the sidecar endpoint.",
  },
  {
    id: "boq-export",
    capability: "BOQ export",
    localHome:
      "/home/runner/work/lattice-platform/lattice-platform/ddc/erp/cost-export.py",
    targetSurface: "GET /v1/erp/export/{project_id}",
    currentState: "Verifier-backed route; live proof currently failing",
    gap: "localhost:8080 returns 404 for GET /api/boq/export; live ERP export contract or verifier project data is not ready.",
    priority: "medium",
    wave: "wave-2",
    validation: "Export endpoint streams a valid BOQ artifact.",
  },
  {
    id: "phases-sync",
    capability: "4D/5D phase sync",
    localHome:
      "/home/runner/work/lattice-platform/lattice-platform/ddc/erp/phase-adapter.py",
    targetSurface: "POST /v1/erp/phases",
    currentState: "Adapter stub",
    gap: "Join schedule phases to IFC rows and push ERP phase assignments.",
    priority: "high",
    wave: "wave-2",
    validation:
      "Project phase records in the ERP align with local schedule metadata.",
  },
  {
    id: "admin-sql",
    capability: "DDC admin SQL layer",
    localHome: "/home/runner/work/lattice-platform/lattice-platform/ddc/admin/",
    targetSurface: "DuckDB WASM parquet queries",
    currentState: "3 of 7 panel queries present",
    gap: "Expand the SQL contract to cover all admin panels.",
    priority: "high",
    wave: "wave-3",
    validation:
      "Admin panels resolve against parquet exports without ad-hoc SQL.",
  },
  {
    id: "admin-route",
    capability: "Admin dashboard route",
    localHome:
      "/home/runner/work/lattice-platform/lattice-platform/src/routes/admin/index.tsx",
    targetSurface: "/admin",
    currentState: "Mapped in UI",
    gap: "Replace capability-only rendering with live parquet and ERP data panels.",
    priority: "high",
    wave: "wave-3",
    validation: "The operator UI renders the mapped DDC surface in one place.",
  },
  {
    id: "cost-per-zone",
    capability: "Cost per zone analysis",
    localHome:
      "/home/runner/work/lattice-platform/lattice-platform/ddc/admin/README.md",
    targetSurface: "/analysis and /admin",
    currentState: "Planned only",
    gap: "Join IFC elements to site zones and expose spatial cost totals.",
    priority: "medium",
    wave: "wave-3",
    validation: "Zone-level cost totals can be queried from parquet exports.",
  },
  {
    id: "cost-overlay",
    capability: "deck.gl cost overlay",
    localHome:
      "/home/runner/work/lattice-platform/lattice-platform/meta/FEATURE_BACKLOG.md",
    targetSurface: "Context B /analysis",
    currentState: "Planned only",
    gap: "Drive deck.gl analytical layers from enriched unit cost data.",
    priority: "medium",
    wave: "wave-3",
    validation: "Cost overlay renders from unit_cost-backed analytics data.",
  },
  {
    id: "quantity-takeoff-agent",
    capability: "Quantity takeoff agent",
    localHome:
      "/home/runner/work/lattice-platform/lattice-platform/meta/FEATURE_BACKLOG.md",
    targetSurface: "runtime agent + evidence ledger",
    currentState: "Planned only",
    gap: "Orchestrate quantities, cost search, BOQ writeback, and evidence capture.",
    priority: "high",
    wave: "wave-2",
    validation: "Agent runs produce BOQ-linked evidence rows end to end.",
  },
  {
    id: "n8n-harvest",
    capability: "n8n workflow harvest",
    localHome:
      "/home/runner/work/lattice-platform/lattice-platform/ddc/n8n/workflows/",
    targetSurface: "upstream workflow JSON mirrors",
    currentState: "Docs only",
    gap: "Pull priority DDC workflow exports into the local workspace.",
    priority: "medium",
    wave: "wave-1",
    validation: "Expected workflow templates exist under ddc/n8n/workflows.",
  },
  {
    id: "n8n-translation",
    capability: "n8n to FastAPI translation",
    localHome:
      "/home/runner/work/lattice-platform/lattice-platform/ddc/n8n/pipeline-templates/",
    targetSurface: "pixeltable/service/routes/*",
    currentState: "Planned only",
    gap: "Convert priority DAGs into native route handlers and templates.",
    priority: "high",
    wave: "wave-2",
    validation: "Priority workflow templates are callable without n8n.",
  },
  {
    id: "fallback-ifc",
    capability: "Fallback IFC converter",
    localHome:
      "/home/runner/work/lattice-platform/lattice-platform/ddc/converters/INSTALL.md",
    targetSurface: "OrbStack operator path",
    currentState: "Docs only",
    gap: "Install only when real IFC parse failures justify it.",
    priority: "low",
    wave: "wave-4",
    validation: "Operators can invoke the fallback parse path on demand.",
  },
  {
    id: "fallback-dwg",
    capability: "Fallback DWG converter",
    localHome:
      "/home/runner/work/lattice-platform/lattice-platform/ddc/converters/INSTALL.md",
    targetSurface: "OrbStack operator path",
    currentState: "Docs only",
    gap: "Install only when binary DWG edge cases appear.",
    priority: "low",
    wave: "wave-4",
    validation: "Operators can invoke the fallback DWG parse path on demand.",
  },
  {
    id: "mirror-ddc-health",
    capability: "Mirror-state ERP sync health",
    localHome:
      "/home/runner/work/lattice-platform/lattice-platform/reality/mirror/README.md",
    targetSurface: "lattice/reality/mirror_state",
    currentState: "Mirror concept exists",
    gap: "Feed ERP and DDC freshness into mirror-state checks.",
    priority: "medium",
    wave: "wave-4",
    validation:
      "Mirror state reflects DDC freshness alongside the other platform layers.",
  },
  {
    id: "ddc-evidence",
    capability: "DDC evidence and logging",
    localHome:
      "/home/runner/work/lattice-platform/lattice-platform/pixeltable/migrations/0012_extended_schema.py",
    targetSurface: "lattice/execution/evidence and runtime ledger",
    currentState: "Schema support exists; events not emitted",
    gap: "Emit DDC skill, ERP, and CWICR audit events.",
    priority: "high",
    wave: "wave-1",
    validation:
      "DDC actions are queryable in evidence and stream-event tables.",
  },
];

export const ddcPipelineStages: Array<DdcPipelineStage> = [
  {
    id: "wave-1",
    name: "Foundation",
    capabilityIds: [
      "skills-harvest",
      "skills-semantic-index",
      "cwicr-seed",
      "cwicr-cost-search",
      "n8n-harvest",
      "ddc-evidence",
    ],
  },
  {
    id: "wave-2",
    name: "Core value path",
    capabilityIds: [
      "ifc-cost-enrichment",
      "boq-sync",
      "boq-read",
      "boq-export",
      "phases-sync",
      "quantity-takeoff-agent",
      "n8n-translation",
    ],
  },
  {
    id: "wave-3",
    name: "Operator surface",
    capabilityIds: [
      "admin-sql",
      "admin-route",
      "cost-per-zone",
      "cost-overlay",
      "skills-search-api",
    ],
  },
  {
    id: "wave-4",
    name: "Resilience",
    capabilityIds: ["fallback-ifc", "fallback-dwg", "mirror-ddc-health"],
  },
];

export const ddcExclusions = [
  "ddc-rvtconverter is excluded because LATTICE does not accept Revit at the boundary.",
  "ddc-dgnconverter is excluded because LATTICE does not accept DGN or MicroStation.",
  "n8n runtime import is excluded because workflows must be translated to native FastAPI handlers.",
  "converter-first ingest is excluded because IfcOpenShell plus ezdxf remains the primary path.",
];

export const ddcCapabilityArtifactPath = "ddc/capability-matrix.yaml";

export const ddcSummary = {
  capabilityCount: ddcCapabilities.length,
  surfaceCount: ddcSurfaces.length,
  highPriorityCount: ddcCapabilities.filter(
    (capability) => capability.priority === "high",
  ).length,
  mediumPriorityCount: ddcCapabilities.filter(
    (capability) => capability.priority === "medium",
  ).length,
  lowPriorityCount: ddcCapabilities.filter(
    (capability) => capability.priority === "low",
  ).length,
};
