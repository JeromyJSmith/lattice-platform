# DataDrivenConstruction (DDC) — LATTICE Integration Map
# Source: github.com/datadrivenconstruction (verified May 2026)
# 6 public repos mapped to LATTICE usage tiers

---

Structured harvest output for this map lives at `/home/runner/work/lattice-platform/lattice-platform/ddc/capability-matrix.yaml`.

---

## THE DDC PHILOSOPHY FOR LATTICE

DDC's value to LATTICE is NOT the file converters.
The value is:
1. The 221 SKILL.md patterns — proven agent workflows for construction tasks
2. The CWICR cost database — 55,719 cost items across 30 regions, semantic search via Qdrant
3. The n8n workflow process logic — visual patterns to convert into LATTICE FastAPI pipelines
4. OpenConstructionERP — the BOQ, 4D/5D, and cost estimation engine LATTICE connects to

LATTICE handles IFC/DXF natively via IfcOpenShell + ezdxf on Mac.
DDC converters (ddc-ifcconverter, ddc-dwgconverter) are Linux-only fallbacks for edge cases.
ddc-rvtconverter and ddc-dgnconverter are NEVER used — no Revit, no DGN in LATTICE.

---

## REPO 1: DDC_Skills_for_AI_Agents_in_Construction
URL: github.com/datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction
Stars: 124 | Language: Python | License: open

What it contains:
- 221 SKILL.md files covering: BIM analysis, cost estimation, scheduling, document control,
  quantity takeoff, clash detection, specification writing, procurement, site logistics
- Each skill has: description, inputs, outputs, example Claude Code prompt, acceptance criteria
- Structured exactly like LATTICE .cursor/skills/ format

How LATTICE uses it:
- Copy relevant skills into ddc/skills/ and adapt for LATTICE context
- Index all 221 skills in Pixeltable lattice/bridge/semantic (semantic_sidecars table)
  with embeddings so agents can search "find skill for quantity takeoff" via pgvector
- The skills become agent-callable tools: lattice agent reads skill → executes pattern

Priority skills for LATTICE landscape architecture:
- Quantity takeoff from IFC
- Cost estimation from element properties
- Schedule phase extraction
- Element classification and validation
- Report generation from BIM data
- Specification writing from element properties

LATTICE home: ddc/skills/

---

## REPO 2: OpenConstructionERP
URL: github.com/datadrivenconstruction/OpenConstructionERP
Stars: 209 | Language: TypeScript | License: open | Version: 2.7.0

What it contains:
- Full construction ERP: BOQ (Bill of Quantities), 4D scheduling, 5D cost linking
- 55,000+ cost items across 21 languages and 20 regional standards
- REST API for programmatic access
- AI-powered cost estimation
- CAD/BIM takeoff integration
- pip install / Docker — cross-platform, Mac-native

How LATTICE uses it:
- POST ifc_elements rows → OpenConstructionERP → get BOQ line items back
- Link every ifc_elements.source_element_id to a BOQ item via erp_item_id FK
- Pull cost estimates into Pixeltable for deck.gl cost overlay (Context B)
- 4D phase data → project schedule timeline in /globe MARPA view
- Export BOQ to Excel/CSV for client deliverables

Endpoints LATTICE calls:
- POST /api/boq/create — create BOQ from element list
- GET /api/boq/{project_id} — get full BOQ
- POST /api/estimate — AI cost estimate for element
- GET /api/cost-items/search — search 55K cost items

LATTICE home: ddc/erp/ + pixeltable/service/routes/erp.py

---

## REPO 3: OpenConstructionEstimate-DDC-CWICR
URL: github.com/datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR
Stars: 145 | Language: HTML | License: open

What it contains:
- 55,719 construction work items across 30 regions
- 27,000+ resources (labor, materials, equipment)
- Multilingual (27 languages)
- Qdrant vector database for semantic search
- Docker compose for local deployment

How LATTICE uses it:
- Run in OrbStack Ubuntu VM (shares Mac filesystem)
- Local no-key lookup uses Qdrant payload text indices plus exact CWICR rate codes to get unit costs back from the restored snapshot
- Results written to Pixeltable ifc_elements.unit_cost column
- Powers the deck.gl cost overlay in Context B
- Powers the BOQ cost lookup in admin dashboard

Setup: ddc/cwicr/seed-qdrant.sh + ddc/cwicr/cost-search.py
Runtime: OrbStack VM at ubuntu@orb, Qdrant at localhost:6333
LATTICE sidecar endpoint: POST /v1/erp/cost-search

LATTICE home: ddc/cwicr/

---

## REPO 4: CAD-BIM-to-Code-Automation-Pipeline
URL: github.com/datadrivenconstruction/CAD-BIM-to-Code-Automation-Pipeline-DDC-Workflow-with-LLM-ChatGPT
Stars: 29 | Language: Jupyter Notebook | License: open

What it contains:
- n8n workflow JSON files for automated CAD/BIM data extraction
- Pattern: IFC/DWG input → LLM → Python code generation → structured output
- Volume grouping, chart generation, QC report automation patterns
- AI_AGENTS_INSTRUCTIONS/CLAUDE.md and INSTRUCTIONS.md (already read)

How LATTICE uses it:
- Extract n8n workflow JSON → convert to LATTICE FastAPI pipeline equivalents
- The LLM-generates-Python pattern maps directly to LATTICE worker.py + claude-cli
- QC report patterns → LATTICE evidence artifacts in lattice/execution/evidence
- Volume grouping patterns → Pixeltable computed columns on ifc_elements

LATTICE home: ddc/n8n/workflows/ + ddc/n8n/pipeline-templates/

---

## REPO 5: Project-management-n8n-with-task-management-and-photo-reports
URL: github.com/datadrivenconstruction/Project-management-n8n-with-task-management-and-photo-reports
Stars: 25 | Language: n8n JSON

What it contains:
- Complete n8n project management system
- Telegram bot for field worker interaction
- Google Sheets for data storage
- Photo report workflows
- Task assignment and completion tracking

How LATTICE uses it:
- Field status update patterns → LATTICE /globe/field mobile view
- Photo report workflow → evidence artifact capture in lattice/execution/evidence
- Task tracking patterns → Linear sync for MARPA project tasks
- Telegram bot patterns → future LATTICE field agent (Telegram → dispatch agent run)

LATTICE home: ddc/n8n/workflows/ (adapt JSON for LATTICE context)

---

## REPO 6: cad2data-Revit-IFC-DWG-DGN
URL: github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN
Stars: 359 | Language: Jupyter Notebook

What it contains:
- Linux .deb CLI converters: ddc-ifcconverter, ddc-dwgconverter
- AI_AGENTS_INSTRUCTIONS/CLAUDE.md and INSTRUCTIONS.md (already read by LATTICE)
- Jupyter notebooks for IFC/DWG data extraction workflows

What LATTICE uses:
- ddc-ifcconverter (Linux .deb) → fallback only for edge-case IFC files IfcOpenShell struggles with
- ddc-dwgconverter (Linux .deb) → fallback only for binary DWG from collaborators (not VW DXF)
- The Jupyter notebook patterns → reference for Marimo notebook templates in LATTICE

What LATTICE DOES NOT use:
- ddc-rvtconverter → NO REVIT
- ddc-dgnconverter → NO DGN/MICROSTATION
- Wine → NO (OrbStack Ubuntu VM ARM64 instead)

Deployment when needed:
- OrbStack Ubuntu VM (arm64, Apple Silicon native)
- Mac filesystem mounted inside VM at /Users
- SSH: ssh ubuntu@orb

LATTICE home: ddc/converters/INSTALL.md (instructions only, no binaries committed)

---

## DDC ADMIN DASHBOARD — WHAT IT SHOWS

The /admin route in LATTICE consolidates all DDC data into one view:

| Panel | Data source | Update frequency |
|---|---|---|
| Project cost summary | OpenConstructionERP BOQ + CWICR unit costs | On IFC ingest |
| Element count by type | Pixeltable ifc_elements GROUP BY bis_subclass | Real-time |
| BOQ line items | OpenConstructionERP /api/boq/{project_id} | On demand |
| Cost per zone | DuckDB WASM ST_Within spatial join | On demand |
| Skill execution log | lattice/execution/evidence WHERE tool LIKE 'ddc.%' | Real-time |
| CWICR search history | lattice/execution/evidence WHERE tool='erp.cost-search' | Real-time |
| Phase schedule | OpenConstructionERP 4D data | On IFC ingest |

---

## GOVERNED ESTIMATION CONTRACT

LATTICE treats estimation as a **dependency-governed capability**, not as an isolated worksheet or one-off app.

- **Operational target:** `MARPA — 918 Juniper Avenue`
- **Pilot proof lineage only:** `ROSE Residence` workbook contract
- **Repo-local source lineage feeding Juniper:** `Farber-Haines [2521]` IFC fixture attached to the Juniper project registry entry

The contract depends on:

- already helping now: `cwicr-seed`, `cwicr-qdrant-cost-search`, `boq-sync`, `boq-read`, `boq-export`, `phases-sync`
- still blocking promotion: `ifc-cost-enrichment`, `quantity-takeoff-agent`
- useful later but not the first gate: `admin-sql`, `admin-route`, `cost-per-zone`, `cost-overlay`, `skills-search-api`

This capability turns green only when Juniper Avenue runs end to end through the governed estimation path with explicit evidence, BOQ linkage, and blocker capture. Until then, estimation remains a planning slice with honest blockers surfaced.

---

## DDC PIXELTABLE SCHEMA ADDITIONS

Add these columns to lattice/bridge/ifc_elements:
- erp_item_id        — FK to OpenConstructionERP BOQ line item
- unit_cost          — CWICR unit cost in USD (from semantic search)
- unit_cost_region   — CWICR region code used for cost lookup
- quantity           — Computed from IFC geometry (area/volume/count)
- quantity_unit      — m², m³, ea, lm
- boq_phase          — Construction phase from OpenConstructionERP 4D
- cost_last_updated  — Timestamp of last CWICR lookup

Add these to lattice/execution/evidence:
- ddc_skill_id       — Which DDC skill was executed
- erp_project_id     — OpenConstructionERP project reference
