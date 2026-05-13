# Repo Census 001 — iTwin, BIS, DDC, and Construction Intelligence Corpus

Date: 2026-05-12
Status: seed corpus, not verified complete

This document defines the next research/mapping track for Meta-Harness. The goal
is to build the source corpus first, then harvest capabilities and schema
vocabulary into the matrix. Do not install all dependencies, promote rows, or
write migration `0017` during this census.

## Purpose

The capability matrix should map external repositories to the eventual LATTICE
operator workflow:

```text
select or group an element
-> resolve identity, geometry, material, quantity, and schema vocabulary
-> call a proven cost, BOQ, schedule, LCA, reporting, or action capability
-> render the result in an iTwin/TanStack panel
-> preserve evidence and verifier output for replay
```

This census is the research input for that matrix. Each repository should be
classified by what it contributes to the workflow and what Pixeltable schema or
vocabulary it implies.

## Seed Corpus

### iTwin, BIS, and Viewer Surface

- `https://github.com/iTwin/viewer-components-react`
- `https://github.com/iTwin/iTwinUI`
- `https://github.com/iTwin/bis-schemas`

Harvest focus:

- viewer widgets, property panels, reporting UI, grouping UI, and selection
  surfaces
- iTwin UI naming and component conventions
- BIS schema names, classes, properties, relationships, and documentation
  generation patterns
- fields that should become Pixeltable vocabulary/reference rows before runtime
  data tables are designed

### Adjacent iTwin / AI / Knowledge Repos

- `https://github.com/interTwin-eu/itwinai`
- `https://github.com/shahzamansurani/ITWingSDK`
- `https://github.com/Mayer123/HyKAS-CSKG`

Harvest focus:

- AI workflow patterns around digital-twin data
- SDK examples or naming conventions that can inform adapters
- construction knowledge graph patterns that may help material, regulation, or
  ontology mapping

### DataDrivenConstruction Runtime And Knowledge Corpus

- `https://github.com/datadrivenconstruction/OpenConstructionERP`
- `https://github.com/datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR`
- `https://github.com/datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction`

Harvest focus:

- BOQ, 4D/5D schedule, estimate, and cost item schemas
- CWICR/Qdrant cost-search fields, units, regions, resource types, and match
  confidence fields
- DDC skill names, inputs, outputs, acceptance criteria, and reusable process
  patterns
- future Pixeltable tables/columns for price source, quantity, BOQ line,
  schedule phase, and DDC skill evidence

### DataDrivenConstruction Index / Reference Repos

- `https://github.com/datadrivenconstruction/awesome-civil-engineering`
- `https://github.com/datadrivenconstruction/awesome-bim`
- `https://github.com/datadrivenconstruction/awesome-fastapi`
- `https://github.com/datadrivenconstruction/awesome-selfhosted-data`

Harvest focus:

- additional candidate repositories to add to later census batches
- FastAPI and self-hosted data patterns that are useful only when they map to a
  bounded LATTICE capability
- avoid treating curated lists as proven capabilities; they are discovery
  sources until a concrete repo/tool is harvested

## Census Output Contract

For each repository, produce one contract-only capability record or a documented
skip decision. Minimum fields:

- repo URL
- owner/org and repository name
- license and license risk
- primary languages and package managers
- dependency/install shape
- exposed APIs, CLIs, schemas, examples, or workflows
- workflow layer served:
  - viewer selection
  - element identity
  - BIS/ECSchema vocabulary
  - geometry/quantity
  - material normalization
  - price source
  - CWICR/cost lookup
  - BOQ
  - schedule/EVM
  - LCA/carbon
  - reporting/UI
  - evidence
  - actuation/write-back
- implied Pixeltable table or column candidates
- smallest deterministic proof fixture
- not-now dependencies or blockers
- proof evidence path, initially empty

## Matrix Rules

- A repo can create many capability rows, but each row must have one narrow
  behavior.
- A row can be useful while still contract-only.
- `proof_evidence` remains empty until browser/sidecar/verifier evidence exists.
- A dependency is not installed just because the repo is in the census.
- Schema ideas become a design note first; migration `0017` waits until the
  pre-flight evidence shape and harvested schema vocabulary settle.

## Immediate Census Steps

1. Verify the seed URLs and discover whether additional `iTwin/*` and
   `datadrivenconstruction/*` repositories belong in this batch.
2. Create or update registry files under `analysis/capabilities/` for the
   verified corpus.
3. Extract BIS/ECSchema and DDC naming conventions into a schema-vocabulary
   design note.
4. For each repo, add contract-only rows with `serves` mapped to the operator
   workflow layer.
5. Pick one deterministic proof fixture only after the row exists and the proof
   can run locally through the Golden Path 002 pattern.

## Live Census 001 Top 10

Live GitHub metadata was checked on 2026-05-13. The first contract-only mapping
registry is:

```text
analysis/capabilities/repo-census-001-capability-registry.yaml
```

Top-10 rows selected for first-pass mapping:

| Capability row | Repo | Primary workflow layer |
|---|---|---|
| `itwinjs-core-platform-substrate` | `iTwin/itwinjs-core` | element identity, BIS concepts, geometry conventions |
| `bis-schemas-vocabulary-harvest` | `iTwin/bis-schemas` | BIS/ECSchema vocabulary |
| `itwin-viewer-operator-shell` | `iTwin/viewer` | viewer shell and operator selection |
| `itwin-viewer-components-react-panels` | `iTwin/viewer-components-react` | panels, widgets, property/report UI |
| `itwinui-design-system` | `iTwin/iTwinUI` | iTwin-native UI conventions |
| `imodel-transformer-extract-import-adapter` | `iTwin/imodel-transformer` | extract/import and synchronization patterns |
| `openconstructionerp-boq-runtime-census` | `datadrivenconstruction/OpenConstructionERP` | BOQ, cost, schedule, ERP adapter |
| `cwicr-cost-corpus-census` | `datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR` | cost corpus and semantic lookup |
| `ddc-skills-agent-pattern-census` | `datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction` | construction-agent skill contracts |
| `cad2data-fallback-and-workflow-census` | `datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN` | fallback parsing and workflow references |

Watchlist for later rows:

- `iTwin/presentation`
- `iTwin/appui`
- `iTwin/grouping-and-mapping-sample-app`
- `iTwin/imodel-reporter`
- `iTwin/bis-schema-validation`
- `iTwin/ecjson2md`
- `iTwin/reality-capture`
- `iTwin/imodels-clients`
- `datadrivenconstruction/CAD-BIM-to-Code-Automation-Pipeline-DDC-Workflow-with-LLM-ChatGPT`
- `datadrivenconstruction/QuantityTakeoff-Python`
- `datadrivenconstruction/4D-5D-Pipeline`
- `datadrivenconstruction/Revit-IFC-Verification`
- `interTwin-eu/itwinai`
- `Mayer123/HyKAS-CSKG`

## Parallel Research Findings

Three read-only research lanes checked the seed corpus and adjacent candidates.
They did not edit files.

### iTwin Lane

Most actionable iTwin additions after the first top-10 seed:

- `iTwin/presentation`: unified selection, hierarchy, and selected-element
  content models. Likely row family: selection bridge, hierarchy provider,
  selected-element panel model.
- `iTwin/appui`: widget registration, layout, toolbar, and panel provider
  patterns. Likely row family: operator widget registry and panel layout.
- `iTwin/grouping-and-mapping-sample-app`: cloud-bound sample but valuable for
  grouping/reporting/cost-overlay shape. Keep as pattern/reference unless a
  local fixture can be isolated.
- `iTwin/imodel-reporter`: report query/result normalization patterns.
- `iTwin/bis-schema-validation`: deterministic schema validation gate for BIS
  or future LATTICE landscape schema extensions.
- `iTwin/ecjson2md`: documentation generation from ECSchema JSON; pair with
  schema validation rather than treating it as a runtime dependency.

Recommended first iTwin proof fixture:

```text
parse iTwin/bis-schemas SchemaInventory.json + BisCore.ecschema.xml
-> emit deterministic class/property/relationship rows
-> verify expected BIS class/property names
```

This fixture moves directly toward Pixeltable schema-vocabulary tables while
staying local and avoiding iTwin cloud/backend dependencies.

### DDC Lane

Most actionable DDC proof chain:

1. `DDC_Skills_for_AI_Agents_in_Construction`: manifest four target skills into
   capability contracts.
2. `OpenConstructionEstimate-DDC-CWICR`: exact-code lookup over a tiny
   cost-data slice before Qdrant.
3. `OpenConstructionERP`: three-element BOQ adapter contract.
4. `CAD-BIM-to-Code-Automation-Pipeline-DDC-Workflow-with-LLM-ChatGPT` or
   `cad2data-Revit-IFC-DWG-DGN`: parse-only n8n/workflow proof, no converter
   execution.

This gives LATTICE one coherent chain:

```text
skill selection -> quantity/cost lookup -> BOQ mapping -> workflow provenance
```

License cautions:

- `OpenConstructionERP` reports AGPL-3.0 in repo metadata/description. Treat as
  service boundary or adapter target, not vendored code.
- Several DDC quantity/ML notebooks are GPL-3.0. Use as pattern references or
  isolated fixtures only after legal review.
- CWICR has separate code/data license surfaces; harvest data dictionary and
  fixture shape first, then decide runtime boundary.

### Standards And Ontology Lane

Useful adjacent candidates for later census batches:

- `IfcOpenShell/IfcOpenShell`: already central for IFC parsing, geometry, IDS,
  ifc4d/ifc5d, and ifcmcp. It belongs in a dedicated IFC capability registry.
- `buildingSMART/bSDD`: classification, property, unit, allowed-value, and
  translation vocabulary for material and product normalization.
- `buildingSMART/IDS`: machine-checkable BIM information requirements for
  deterministic evidence gates.
- `jyrkioraskari/IFCtoLBD`, `w3c-lbd-cg/bot`,
  `buildingsmart-community/ifcOWL`, `digitalconstruction/*`, Brick, REC, and
  BuildingMOTIF: valuable ontology/schema references. Add only after the first
  BIS/DDC rows are harvested, and track licenses carefully.
- `interTwin-eu/itwinai`: AI workflow toolkit for later model-registry and
  material-normalization benchmarks.
- `Mayer123/HyKAS-CSKG`: method-only reference due GPL-2.0 and weak direct
  construction-schema fit.
