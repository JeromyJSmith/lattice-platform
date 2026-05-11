<!-- spec-verified: code.claude.com/docs 2026-05-11 -->
# Phase 0 Amendment — MARPA + Meta-Harness Research Integration

**Status:** binding amendment. Phase 1 execution is BLOCKED until this amendment is committed and the four prior PLAN docs (`00`–`04`) are updated to reference it.

**Why this exists:** the original Phase 0 plan was written without consulting the MARPA DevStack research at `/Volumes/PixelTable/VW_iTWIN_Bridge/Vectorworks_Bentley_iTwin_MARPA_Research_20260508/MARPA_DevStack_Research_20260508/`. That research is the canonical source for both the Meta-Harness artifact contracts (DesireRecord, ImprovementGoal, gold_goals.md, AGORA, InfraNodus integration) and the MARPA-specific platform context (landscape semantic sidecar, CityGML 3.0 Vegetation ADE alignment, DDC Skills adaptation, deck.gl 9.3 + Cesium acquisition implications).

## Research files consumed

| File | Lines | Relevance to LATTICE/Meta-Harness |
|---|---|---|
| `meta-harness-artifacts.md` | 251 | **CANONICAL.** Source-of-truth for DesireRecord schema, ImprovementGoal schema, gold_goals.md template, AGORA 3-layer model, InfraNodus operating modes (`gaps` / `develop` / `reinforce` / `latent`), GORE-style `weighted_contribution` heuristic, layered architecture (Desire → Goal → Golden → Graph-intelligence → Meta-harness → Ratchet QA) |
| `github meta-harness (1).md` | 3265 | Stanford IRIS Lab repo references (`stanford-iris-lab/meta-harness`, `meta-harness-tbench2-artifact`, `SuperagenticAI/metaharness`), QA technique catalog (deterministic benchmarks, multi-metric objectives, trace QA, failure-mode classification, invariant checks, harness-structure QA, robustness/adversarial QA, human-in-the-loop), InfraNodus API patterns (`graphAndStatements`, `graphAndAdvice`, `compareGraphs`, `dotGraph`), InfraNodus input checklist, pitfalls catalog |
| `research_report_20260508_marpa_devstack.md` | 572 | **MARPA-specific.** 10 findings: deck.gl 9.3 validation, nebula.gl → @deck.gl-community/editable-layers risk + DrawAPI mitigation, iTwin Synchronization API constraints (no VWX native path), Bentley/Cesium acquisition (Sept 2024) + Tile3DLayer/TerrainExtension, IFC4.3 vegetation poverty (2 properties only) + CityGML 3.0 Vegetation ADE alignment, DDC Skills (221 skills, 12 directly adaptable + 3 new modules: LA-ETL/LA-ECO/LA-IRR), OpenSite+ no public API, landscape DT case studies, agentic coding tool patterns |
| `Bentley iTwin Developer sdk other repos and how to (1).md` | 623 | iTwin repo landscape, integration patterns, access-control, Node.js setup, role assignment. Defers to existing `meta/ITWIN_MAPPING.md` for the LATTICE-relevant subset |
| `vectorworks-2026-sdk-print-guide.md` | 75 | VS 2022 v17.12 + Xcode 16.2; SDK satellite credentials requirement; `ObjectExample` as starting template. Folds into vw-plugin section CLAUDE.md authoring (Phase 5/6) |
| `itwin_repo_matrix (1).xlsx`, `itwin-repo-explorer.html`, `vectorworks-dashboard.html`, `research_report_*.html` | n/a | Binary / HTML — referenced but not parsed during this pass |

## Conflicts with the prior plan (and resolutions)

| Conflict | Prior plan | Research says | Resolution |
|---|---|---|---|
| GOAL.md improvement-loop ordering | Read GOAL.md → score → pick action → run script | Read gold_goals.md FIRST, then InfraNodus graphs, then ranked gap report, then propose ONE change, then ratchet | Update GOAL.md template in `04-EXECUTION-HANDOFF.md` (this amendment) |
| Section count | 8 sections (Schema, API, Frontend, Georef/Reality, GenAI/Assets, VW Bridge/iTwin, DDC, CI/Infra) | Research strongly suggests **Landscape Semantic Sidecar** is the strategic moat and should not be conflated with GenAI/Assets | Add §"Section count decision" below. Recommend: KEEP at 8 but explicitly carve out a `landscape-semantic` subsection within the GenAI/Assets section's GOAL.md, with its own scoring weights |
| Schema convention | `pxt.String` (WKT/GeoJSON) for geometry | Research adds: sidecar JSON schema must **mirror CityGML 3.0 Vegetation ADE** conceptual model (Crown/Trunk/Root sub-features; SolitaryVegetationObjectGrowth; PlantCover with speciesRichness/relativeAbundance/habitatClassification; VegetationManagement) | Add to Phase 2 migration 0014 specification: when defining `lattice/harness/*` schema, plant-related tables (when added later in 0015+) MUST use ADE-compatible column names |
| Frontend boundary rule | ThatOpen (Context A) ↔ deck.gl (Context B) never cross-import | Research adds: deck.gl `Tile3DLayer` + `TerrainExtension` is the production-grade Cesium 3D Tiles compositing path; `@deck.gl-community/editable-layers` is "semi-maintained" — DrawAPI abstraction is **mandatory mitigation** not optional | Add to Frontend section CLAUDE.md (Phase 5): require `DrawAPI` adapter pattern; `@deck.gl-community/editable-layers` may appear in exactly ONE adapter file |
| DDC integration scope | Index 221 DDC skills via semantic_sidecars | Research: 12 skills are directly adaptable (zero/minor adaptation); 3 modules must be built from scratch (LA-ETL, LA-ECO, LA-IRR) | Update DDC section GOAL.md action catalog to enumerate the 12+3 split; add baseline "build LA-ETL" as +12pt action |
| iTwin section scope | BIS vocabulary + `@itwin/core-geometry` + `@itwin/core-common` | Research confirms (Tier 1 from `ITWIN_MAPPING.md`). Adds: web-ifc for Prototype 1 (alternative ingestion path) AND that the Bentley/Cesium acquisition creates renderer-strategy risk that the iTwin section harness must monitor | Add to VW-iTwin section GOAL.md: track `cesium-acquisition-risk` as a tracked signal |

## New artifacts to add to the plan (the canonical 16-item list)

These artifacts come from `meta-harness-artifacts.md`. They are added to Phases 4 / 5 / 6 of `02-PLAN.md`.

### Schema layer (Phase 4)

1. **`schemas/desire-record.schema.yaml`** — DesireRecord intake schema. Captures vague needs / "I wish I could…" statements before formal goal modeling. Source-typed (user / stakeholder / benchmark / incident / observation / strategy). Used as input corpus for InfraNodus.
2. **`schemas/improvement-goal.schema.yaml`** — AGORA/GORE-aligned goal schema with `contribution_model` (contribution_to_parent, confidence, preference_weight, risk_penalty), `fit_criterion` (metric_name, target_direction, baseline_value, target_value), and `governance` (owner, acceptance_rule, rollback_rule).
3. **`analysis/desires/.gitkeep`** — directory for individual DesireRecord YAML files.

### Graph-intelligence layer (Phase 4)

4. **`analysis/infranodus/desires.graph.json`** — InfraNodus graph of the DesireRecord corpus (empty `{}` initially).
5. **`analysis/infranodus/goals.graph.json`** — InfraNodus graph of the ImprovementGoal corpus.
6. **`analysis/infranodus/failures.graph.json`** — InfraNodus graph of the failure/incident corpus.
7. **`analysis/infranodus/goal-vs-implementation.diff.json`** — `compareGraphs` output between accepted goals and live codebase docs.
8. **`analysis/infranodus/README.md`** — documents the four operating modes:
   - `optimize=gaps` — when reducing blind spots (default starting mode)
   - `optimize=develop` — balanced expansion when coverage is uneven
   - `optimize=reinforce` — when harness stuck in narrow local optimum
   - `optimize=latent` — when harness overfocuses on a single area
9. **`analysis/gaps/README.md`** — explains the ranked gap-report format.
10. **`analysis/gaps/<section>-gap-report.md`** × 8 — one ranked gap report per section (generated, initially empty).

### Golden layer (Phases 4 + 5)

11. **`gold_goals.md` (repo root)** — global ratchet target. Compact (≤20 lines effective body), durable across multiple autoresearch iterations.
12. **`<section-root>/gold_goals.md`** × 8 — per-section ratchet target. Distinct from `GOAL.md` (which is the full fitness function); `gold_goals.md` is the stable contract.

### Gap-analysis tool (Phase 4)

13. **`meta/harness/bootstrap/build-gap-analysis.py`** — stub implementation. Ingests DesireRecords, ImprovementGoals, dependency nodes (from Graphify output), ADRs, benchmark specs, and incidents into a single graph store. Computes structural gaps (uncovered dependencies, unbenchmarked goals, high-centrality components with no quality checks). Ranks by `composite_score = preference_weight × dependency_centrality × uncertainty × risk_penalty`. Stub exits 0 with valid empty report; full impl tracked as follow-up issue #16.

### Rules + agent layer (Phase 6)

14. **`.claude/rules/infranodus-corpus.md`** (path-scoped to `analysis/infranodus/**`, `analysis/gaps/**`) — InfraNodus input checklist that catches 90% of graph failures before they happen:
    - **Define purpose** — each corpus serves ONE graph purpose (desires vs. goals vs. failures — never mix)
    - **Validate source quality** — minimum 30 statements per corpus; no raw log dumps
    - **Normalize language** — strip implementation jargon; normalize entity names; one statement per line
    - **Shape the corpus** — 150-500 word documents per entry; group related entries; remove duplicates
    - **Preflight pass** — check for `modularity < 0.3` (undifferentiated blob) or `betweenness > 0.8` (single bottleneck node)
    - **InfraNodus-ready packaging** — UTF-8, no binary content, no embedded code blocks

15. **AGORA 3-layer frontmatter in `.claude/agents/<section>-harness.md`** — each section harness agent's YAML frontmatter MUST declare its three AGORA layers (product / workflow / orchestration) plus section, scoring_script, gold_goals path, desire_corpus path, goal_corpus path. Example (verified against spec from `01-RESEARCH.md` §B — `name` + `description` required; arbitrary additional keys preserved by Claude Code):

```yaml
---
name: schema-harness
description: >
  Section harness agent for the LATTICE Pixeltable schema subsystem.
  AGORA-product: schema correctness + migration safety + table coverage
  AGORA-workflow: migration dryrun→apply→verify; owned-parents; write-once
  AGORA-orchestration: reads infranodus/goals.graph.json + gold_goals.md
                       before proposing; writes section_events
section: schema
scoring_script: scripts/score-schema.sh
gold_goals: pixeltable/gold_goals.md
desire_corpus: analysis/infranodus/desires.graph.json
goal_corpus: analysis/infranodus/goals.graph.json
---
```

### Bootstrap (Phase 4 — extends existing entry)

16. **`meta/harness/bootstrap/run-autoresearch.sh`** must read `analysis/infranodus/desires.graph.json` and `goals.graph.json` BEFORE constructing each proposer brief. `contentGaps` and `conceptualGateways` from InfraNodus output become RAG prompt hints for the proposer. (This refines the existing Phase-4 entry; not a new file.)

## MARPA-specific findings (non-Meta-Harness)

These are LATTICE-platform decisions the research forces. They are NOT new sections of the plan, but they materially constrain Phase 2 (migration 0014 column conventions), Phase 5 (per-section CLAUDE.md content), and Phase 6 (skill content).

### F1. Landscape Semantic Sidecar is the strategic core

> "Of all the technical decisions in the architecture, the landscape semantic schema is the one that creates durable competitive advantage… No competitor building on iTwin or any other digital twin platform has this alignment today."

**Action:** when the GenAI/Assets section CLAUDE.md is written in Phase 5, its `gold_goals.md` must list "Landscape Semantic Sidecar coverage" as a top-3 weighted goal. Concretely: `lattice/bridge/plant_assets` (already exists from migration 0012) needs columns aligned with CityGML 3.0 Vegetation ADE — `speciesScientificName`, `speciesCommonName`, `expectedHeight`, `canopySpread`, `healthStatus`, `plantingYear`, `protectionStatus`, `habitatClassification`, `maintenanceScheduleRef`, `ecologicalFunctionTags`, `telemetryBindings`. (This will land as migration 0015 in a follow-up, not in this PR.)

### F2. CityGML 3.0 Vegetation ADE alignment

ADE is at conceptual stage (no XSD as of 2026-05); ISPRS 2024 paper by Petrova-Antonova et al. is the reference. Sofia + Tallinn + OneTree are the first pilot implementations.

**Action:** add to GenAI section CLAUDE.md: "All plant-related schema additions must mirror the CityGML 3.0 Vegetation ADE conceptual model. Reference: `meta-harness-artifacts.md` synthesis — Crown/Trunk/Root sub-features; SolitaryVegetationObjectGrowth via Dynamizer; PlantCover with speciesRichness/relativeAbundance/habitatClassification; VegetationManagement records."

### F3. nebula.gl risk — DrawAPI abstraction is mandatory

> "`@deck.gl-community/editable-layers` should appear in exactly one file — the DrawAPI adapter implementation."

**Action:** add to Frontend section CLAUDE.md: "DrawArtifact lifecycle (polygon/line/point/lasso/buffer/validation/promotion) defined entirely in LATTICE-internal types. `@deck.gl-community/editable-layers` import allowed in exactly one file: `src/draw-api/adapter-deckgl-community.ts`. Graphify policy rule `no-editable-layers-leak` enforces."

### F4. Bentley/Cesium acquisition — renderer-strategy risk

Cesium acquired Sept 2024. iTwin now auto-converts design data to 3D Tiles. iTwin Platform APIs for Cesium released. Patrick Cozzi (Cesium CEO) is now Bentley CPO.

**Action:** add to VW-iTwin section CLAUDE.md: "Renderer strategy is a moving target. CameraSyncAPI must be defined against a generic `CameraState` (position, target, frustum) — never against iTwin.js or Cesium-specific camera types. deck.gl `Tile3DLayer` provides an independent rendering path for Cesium ion 3D Tiles — preferred over iTwin.js viewport for analytical overlays."

### F5. DDC Skills landscape adaptation — 12 + 3 split

12 skills directly adaptable: `ifc-qto-extraction`, `drone-site-survey`, `cwicr-takeoff-helper`, `specification-extractor`, `environmental-monitoring`, `carbon-calculator`, `weather-impact-analysis`, `dwg-to-excel`, `ifc-to-excel`, `cwicr-work-breakdown`, `bim-validation-pipeline`, `schedule-compression`.

3 modules to build from scratch: **LA-ETL** (VW Landmark IFC → sidecar JSON), **LA-ECO** (canopy/impervious/species-richness/bioretention/runoff/embodied-carbon), **LA-IRR** (ET₀ via ASCE Penman-Monteith + Kc + NOAA + WUCOLS).

**Action:** DDC section GOAL.md action catalog explicitly lists the 12 + 3 — each adaptable skill = `+3pt`; each new module = `+12pt`.

### F6. cad2data is the immediate VW-to-data extraction path

Mac-native Linux .deb + Windows .exe. Handles IFC2x3/IFC4/IFC4.3/IFCXML/IFCZIP/HDF5 → XLSX/DAE/IFC. No Autodesk/Bentley license required. Already ships `CLAUDE.md` with full CLI syntax — perfect template reference for our `vw-plugin/CLAUDE.md`.

**Action:** Phase 6 vw-plugin SKILL.md should mirror `cad2data`'s CLAUDE.md structure (full CLI syntax + best-practice prompts + example prompt table).

### F7. web-ifc as Prototype-1 ingestion path

`@thatopen/engine_web-ifc` (WASM, compiled from C++ via Emscripten) reads IFC files in-browser. Supports IFC2x3 + IFC4. Suitable for single-project models (Prototype 1); not large global models.

**Action:** add to Frontend section gold_goals.md: "Phase-1 viewer ingestion may use web-ifc client-side; Phase-2+ production uses iTwin Synchronization API server-side. The Landscape Semantic Core stays consistent across both ingestion paths."

### F8. OpenSite+ is inspiration, not integration

No public API. Desktop application, North America early access only. The architecture pattern (multi-scenario generative optimization + LLM-assisted constraints + real-time cost feedback) is the correct model for LATTICE's future site-analysis layer — built on public iTwin APIs + Python ML.

**Action:** add as a Phase-5-deferred deliverable. Not in this PR.

### F9. Stanford Meta-Harness reference implementations (for the proposer)

- `stanford-iris-lab/meta-harness` — official framework
- `stanford-iris-lab/meta-harness-tbench2-artifact` — ready-made TerminalBench 2 harness
- `SuperagenticAI/metaharness` — open-source Python library (preserves environment bootstrap snapshot pattern)

**Action:** add to `meta/harness/GLOBAL_HARNESS.md` (Phase 4): "Reference implementations — when designing the proposer loop, consult these repos. Do NOT vendor any of them; treat as design references."

### F10. Vectorworks 2026 SDK build prerequisites

Visual Studio 2022 v17.12 + toolset v143 (Windows); Xcode 16.2 (macOS). Satellite credentials file required for encrypted/obfuscated plugins. Start from `VectorworksDeveloper/SDKExamples/ObjectExample`. Debug | x64 first build.

**Action:** add to `vw-plugin/CLAUDE.md` (Phase 5).

## Section count decision

The original plan has 8 sections. The research raises the question of whether **Landscape Semantic Sidecar** deserves a 9th. Decision:

**KEEP at 8 sections.** Carve "landscape-semantic" as a top-weighted goal inside the GenAI/Assets section's `gold_goals.md` rather than a separate section. Rationale:
- The semantic sidecar lives in `lattice/bridge/plant_assets` + future `lattice/bridge/landscape_semantic/*` tables — already in the Schema section's ownership chain via Pixeltable migrations.
- The 12 DDC adaptable skills + 3 new modules (LA-ETL, LA-ECO, LA-IRR) live in `ddc/` and `skills/` — already in the DDC section's scope.
- Adding a 9th section would split ownership across two harnesses, weakening accountability. Better to weight the semantic core HIGH inside one section.

If the post-Phase-8 retrospective shows this consolidation is failing, the autoresearch loop's proposer can suggest a 9th-section split as a harness improvement.

## What this amendment does NOT change

- The 8-phase execution order (`02-PLAN.md` Phase 1 → Phase 8) stays exactly as written.
- The 8-section topology stays as written.
- The branch contract (`feature/meta-harness` only, draft PR, no main pushes) stays as written.
- The CI gate (`docs-sync-check` + new Jobs 7–9) stays as written.
- The migration 0014 column schema (4 tables: `health_snapshots`, `harness_proposals`, `section_events`, `global_decisions`) stays as written.

This amendment is **additive only**.

## Updated file count

Original Phase 5 estimate: ~93 new + edited files.

With this amendment: **~93 + 16 = ~109 files**. Risk profile and time estimate unchanged — the 16 additions are mostly stubs and templates that follow existing patterns.

## Cross-references for the executing agent

When writing Phase 4 files, the executor MUST reference:
- DesireRecord / ImprovementGoal / gold_goals.md templates → copy verbatim from `meta-harness-artifacts.md` lines 9-153
- AGORA 3-layer model → `meta-harness-artifacts.md` lines 157-169
- InfraNodus operating modes → `meta-harness-artifacts.md` line 236
- GORE `weighted_contribution` heuristic → `meta-harness-artifacts.md` lines 191-199
- Layered system architecture → `meta-harness-artifacts.md` lines 212-220
- QA technique catalog → `github meta-harness (1).md` lines 320-484 (sections 1-6)
- InfraNodus input checklist → `github meta-harness (1).md` lines 1282-1372 (sections "Task list" + "Best practices" + "Debugging structural gaps")

When writing Phase 5 / 6 section files, the executor MUST reference:
- F1–F10 MARPA findings above
- `research_report_20260508_marpa_devstack.md` Finding 6 (DDC skills) for DDC section
- `research_report_20260508_marpa_devstack.md` Finding 3 (IFC + sidecar) for VW-iTwin + Schema sections
- `research_report_20260508_marpa_devstack.md` Finding 5 (CityGML 3.0 Vegetation ADE) for GenAI section
- `research_report_20260508_marpa_devstack.md` Finding 2 (DrawAPI mitigation) for Frontend section
- `vectorworks-2026-sdk-print-guide.md` for vw-plugin section

## Follow-up issues to add to Phase 8

Bringing total from 12 → **16**:

13. Implement DesireRecord intake pipeline — `analysis/desires/` + intake script mining from GitHub issues, MEMORY.md files, session logs — `meta-harness`, `schema`
14. Run InfraNodus gap analysis on initial desire corpus — populate `analysis/infranodus/desires.graph.json` — `meta-harness`, `infranodus`
15. Implement AGORA ImprovementGoal decomposition for schema section — first 3 ImprovementGoals from desires using AGORA 3-layer — `meta-harness`, `schema`
16. Build gap analysis tool (`build-gap-analysis.py`) — full impl of dependency-integrated gap ranking — `meta-harness`

Plus new label: `infranodus` (color `#10B981` — green) for InfraNodus-corpus-related work.
