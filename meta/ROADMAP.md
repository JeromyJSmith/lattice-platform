# LATTICE Roadmap

Phased build order with milestones. Each phase has a definition of done; phases are gated, not parallel — Phase N+1 starts when Phase N's DoD is green on `main`.

The current state of the world: **Phase 0 complete, Phase 1 in progress.**

For every phase, the linked GitHub Issues are the canonical work units. The numbers reference issues in the [LATTICE Roadmap](https://github.com/users/JeromyJSmith/projects/4) project board.

---

## Phase 0 — Foundation (DONE 2026-05-11)

The platform exists end-to-end as a working operator console.

**Definition of done — all met:**

- [x] Runtime console at `/runtime` — TanStack Start + SSR loader + clickable rows + SSE-pushed token streaming
- [x] Real agent loop — `claude -p --output-format stream-json --include-partial-messages` subprocess in `pixeltable/service/worker.py`
- [x] Pixeltable schema — 19 tables across `lattice/execution/*` + `lattice/bridge/*`, snapshot-verified
- [x] CI/CD — 6 workflows on GitHub Actions; ci + release green; test-pxt waits on self-hosted Mac runner; linear-sync no-ops cleanly without the secret
- [x] GitHub infrastructure — 167 issues, 23 labels, 5-column project board, PR/issue templates, CODEOWNERS
- [x] Multi-agent handoff scaffolding — `CONTRIBUTING.md`, `meta/AGENT_ONBOARDING.md`, `.github/copilot-instructions.md`, `codex.md`, `cloudflare-agent.md`, `meta/LINEAR_SETUP.md`
- [x] Repo folder structure — `agents/`, `skills/`, `scripts/`, `vw-plugin/`, `vw-python/`, `itwin/`, `ddc/`, `meta/` all populated
- [x] iTwin + DDC + Cesium integration maps — `meta/ITWIN_MAPPING.md`, `meta/DDC_MAPPING.md`, `meta/CESIUM_SETUP.md`
- [x] Extended Pixeltable schema (migration 0012) — PostGIS WKT, BIS classification, DDC admin, 3D asset linking, MARPA project registry, GenAI namespace
- [x] genai/ + assets/ folder scaffold

**What runs today:** dispatch a task in the operator console → it streams Claude's real response token-by-token into the EventTimeline → row appears in the table with `agent_kind=claude-cli` and `status=completed`. The data layer is 25 tables + an idempotency store + an embedding index.

---

## Phase 1 — Spatial foundation + VW bridge (NOW)

The platform learns *where things are* and *what they are in BIM terms*.

**Active issues:** [#173 (migration backfill)](https://github.com/JeromyJSmith/lattice-platform/issues/173), [#175 (spatial joins)](https://github.com/JeromyJSmith/lattice-platform/issues/175), [#185 (PostGIS extension)](https://github.com/JeromyJSmith/lattice-platform/issues/185), [#106 (VW plugin scaffold)](https://github.com/JeromyJSmith/lattice-platform/issues/106), and the rest of the `vw-bridge` + `postgis` labels.

**Definition of done:**

- [ ] PostGIS extension live at the PG layer; `geom_point geometry` computed columns populated for every `ifc_elements` row from its WKT
- [ ] First real `vectorworks_exports` row written from a VW C++ plugin menu command (placeholder generation in VW → IFC export → POST to sidecar → row in Pixeltable)
- [ ] `bis_class` / `bis_subclass` populated for every `ifc_elements` row via IfcOpenShell type mapping ([`itwin/bis-schemas/`](../itwin/bis-schemas/))
- [ ] `lattice/bridge/marpa_projects` seeded with at least one real project (lat/lon, boundary polygon, IFC path)
- [ ] LOD100 placeholder geometry created in VW for one project, exported to IFC, ingested through the pipeline, visible in the operator console runs table
- [ ] All Phase 1 issues closed or explicitly deferred with reason

---

## Phase 2 — Three rendering contexts (3D, analytical, globe)

The platform becomes visual. Three views, three engines, one data layer.

**Active issues:** [#70 ThatOpen viewer route](https://github.com/JeromyJSmith/lattice-platform/issues/70), [#86 Analytical layer route](https://github.com/JeromyJSmith/lattice-platform/issues/86), [#138 CesiumJS route](https://github.com/JeromyJSmith/lattice-platform/issues/138), [#35 Potree viewer](https://github.com/JeromyJSmith/lattice-platform/issues/35), and the `3d-viewer`/`analytics-layer`/`cesium`/`point-cloud` labels.

**Definition of done:**

- [ ] **Context A** at `/viewer` — ThatOpen Fragments rendering an IFC from `lattice/bridge/ifc/ifc_elements`, OrthoPerspectiveCamera + PostproductionRenderer, element selection wired to the property panel
- [ ] **Context B** at `/analysis` — deck.gl ScatterplotLayer over a MapLibre basemap, fed by DuckDB WASM querying Parquet exports of `ifc_elements`; cost overlay layer present
- [ ] **Cesium globe** at `/globe` — Cesium ion (free tier) or self-hosted terrain, MARPA project pins, click-to-fly-to, lazy-load IFC Fragment on zoom-in
- [ ] **Potree integration** — point clouds rendered in the ThatOpen scene (shared canvas), toggleable layer
- [ ] Cross-context selection state — clicking an element in Context A highlights it in Context B and the globe pin

---

## Phase 3 — 3D asset pipeline + Cinema 4D handoff

The platform learns to *make plants look real*.

**Active issues:** [#174 3D plant asset pipeline](https://github.com/JeromyJSmith/lattice-platform/issues/174), the entire `3D PLANT ASSET CREATION PIPELINE` section, [#179 ComfyUI setup](https://github.com/JeromyJSmith/lattice-platform/issues/179), [#196 C4D project skeleton](https://github.com/JeromyJSmith/lattice-platform/issues/196).

**Definition of done:**

- [ ] ComfyUI server running locally with the `plant-2d-to-3d.json` workflow
- [ ] At least one species end-to-end: 3+ geo-tagged photos → ComfyUI job → GLB at `assets/plants/lod-300/` → Cinema 4D project skeleton → VW Plant Style assignment → ThatOpen LOD swap visible in the viewer
- [ ] Quality review gate at `/admin` — generated assets need a `quality_score >= 0.7` before promoting to VW
- [ ] All evidence rows captured: `comfyui.dispatch`, `c4d.export`, `vw.style-import` show up in `/admin`'s skill execution log
- [ ] At least one client-presentation render produced from Cinema 4D + Redshift with the generated asset

---

## Phase 4 — DDC admin + BOQ + cost intelligence

The platform learns *what things cost* and *what's been built*.

**Active issues:** [#168 CWICR Qdrant setup](https://github.com/JeromyJSmith/lattice-platform/issues/168), [#169 BOQ adapter](https://github.com/JeromyJSmith/lattice-platform/issues/169), [#170 /admin route](https://github.com/JeromyJSmith/lattice-platform/issues/170), [#171 n8n translation](https://github.com/JeromyJSmith/lattice-platform/issues/171), [#172 Skill indexing](https://github.com/JeromyJSmith/lattice-platform/issues/172).

**Definition of done:**

- [ ] CWICR Qdrant running locally (OrbStack VM); `POST /v1/erp/cost-search` returns matches for plant-element descriptions
- [ ] OpenConstructionERP BOQ adapter: every `ifc_elements` row gets an `erp_item_id` + `unit_cost` after `POST /v1/erp/boq`
- [ ] `/admin` route renders all 7 panels with real data (per [`meta/DDC_MAPPING.md`](DDC_MAPPING.md) § ADMIN DASHBOARD)
- [ ] BOQ Excel export works end-to-end via `GET /v1/erp/export/{project_id}`
- [ ] DDC cost overlay live in Context B's deck.gl analytical view (ColumnLayer driven by `unit_cost`)
- [ ] 221 DDC skills indexed in `lattice/bridge/semantic/semantic_sidecars` with embeddings; agent can search "find skill for quantity takeoff"

---

## Phase 5 — Local AI / GeoAI / Marimo browser agent

The platform learns to *reason locally* and *understand site reality*.

**Active issues:** [#178 Ollama setup](https://github.com/JeromyJSmith/lattice-platform/issues/178), [#181 Model registry](https://github.com/JeromyJSmith/lattice-platform/issues/181), [#180 / #210 GeoAI tree detection](https://github.com/JeromyJSmith/lattice-platform/issues/210), and the whole `LOCAL AI / GENAI / GEOAI / ML` section.

**Definition of done:**

- [ ] Ollama installed on Apple Silicon with 4 models; `model-router.py` routing by task type
- [ ] `lattice/genai/model_registry` live with availability status per model
- [ ] GeoAI tree-detection model trained on at least one MARPA project's LiDAR + orthophoto; results written to a `lattice/bridge/existing_trees` table
- [ ] GeoAI species classifier fills in `reference_images.species_tag` automatically for site photos
- [ ] Marimo notebook embedded in LATTICE at `/notebooks`, with DuckDB WASM cells querying Parquet exports
- [ ] Browser agent in a Marimo cell — `@tanstack/ai` against local Ollama, no API key

---

## Phase 6 — Production hardening + C++ plugin polish

The platform becomes shippable to other operators.

**Active issues:** all of the C++ VW plugin section, [#54 Better Auth](https://github.com/JeromyJSmith/lattice-platform/issues/54), [#106 Plugin scaffold](https://github.com/JeromyJSmith/lattice-platform/issues/106), [#107 PlaceholderCmd](https://github.com/JeromyJSmith/lattice-platform/issues/107), [#58 CI hardening](https://github.com/JeromyJSmith/lattice-platform/issues/58).

**Definition of done:**

- [ ] C++ VW plugin builds clean on Mac + Windows from `vw-plugin/CMakeLists.txt`
- [ ] All three menu commands work in VW: "Generate LATTICE Placeholders", "Export IFC", "Sync to LATTICE", "Load Plant Assets"
- [ ] Plant Style Manager fully wired — swapping a style updates all instances globally
- [ ] Self-hosted Mac runner registered → `test-pxt` workflow green
- [ ] Better Auth enabled in the operator console
- [ ] CI lint job passes without `|| true` warning escape hatches (currently lint warns rather than fails)
- [ ] Release process documented end-to-end; first tagged release with a CHANGELOG

---

## Cross-phase invariants (never violated)

These hold regardless of phase. If a PR violates one of these, it doesn't merge.

1. **No `@itwin/core-backend`.** Pixeltable owns persistence.
2. **No Anthropic SDK in client code.** Server side or via `claude -p` only.
3. **uv only for Python.** Never pip, conda, poetry.
4. **No Revit / DGN / MicroStation.** IFC4.3 only at the boundary.
5. **Pixeltable is the only database.** No standalone SQLite / Postgres / SQLite-backed `.bim` writes (we read those, never write them).
6. **All coordinates EPSG-normalized before Pixeltable.** Never raw VW internal coordinates.
7. **Plant Style Manager controls all instances.** Never hardcode geometry per instance.

See [`AGENTS.md`](../AGENTS.md) and [`CLAUDE.md`](../CLAUDE.md) for the long-form versions.
