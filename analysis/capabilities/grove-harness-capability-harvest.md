<!-- spec-verified: GROVE_HARNESS/juniper2026 2026-05-13 -->
# Capability Harvest — grove-harness

| Field | Value |
|---|---|
| Source repo | `/Volumes/PixelTable/GROVE_HARNESS/juniper2026` (local, prior LATTICE iteration) |
| Reviewed commit | `HEAD` (see TOOL_MANIFEST.yaml §L2-WRAPPED TOOLS) |
| Canonical docs | `juniper2026/SPEC_INDEX.md`, `TOOL_MANIFEST.yaml` |
| Harvest date | `2026-05-13` |
| LATTICE owner | Meta-Harness |
| Harvested by | claude-haiku-4-5 |

## Capability Surfaces

| Capability ID | Surface | Name | Source | Raw capability | Notes |
|---|---|---|---|---|---|
| `grove-sfa-extract-plant-positions` | `cli_command` | `extract_plant_positions` | `vw_plugins/extract_plant_positions.py` | Extract Plant PIO positions from open VWX with geometry, coordinates, species record fields | P-R; requires_vw=true; last_verified=2026-05-03; smoke: 4 plants found in 38 objects |
| `grove-sfa-extract-landscape-area-composition` | `cli_command` | `extract_landscape_area_composition` | `vw_plugins/extract_landscape_area_composition.py` | Read landscape area records from VWX, emit species composition CSV and JSON | P-R; requires_vw=true; last_verified=2026-05-03; smoke: 8 LAs, 33 rows |
| `grove-sfa-diag-pio-inventory` | `cli_command` | `diag_pio_inventory` | `vw_plugins/diag_pio_inventory.py` | Audit all Plant Instance Objects in document, tabulate by PON/layer | P-D; requires_vw=true; last_verified=2026-05-03; smoke: 6563 PIOs |
| `grove-sfa-diag-landscape-area-records` | `cli_command` | `diag_landscape_area_records` | `vw_plugins/diag_landscape_area_records.py` | Enumerate all landscape area records and their field contents | P-D; requires_vw=true; last_verified=null |
| `grove-sfa-apply-document-georef` | `cli_command` | `apply_document_georef` | `vw_plugins/apply_document_georef.py` | Apply document-level georeference (EPSG/TM override); gate: backup required | P-W; requires_vw=true; last_verified=null; gated write |
| `grove-sfa-bootstrap-plant-3d-pins` | `cli_command` | `bootstrap_plant_3d_pins` | `vw_plugins/bootstrap_plant_3d_pins.py` | Place 3D pin symbols at plant positions in live .vwx; gate: backup required | P-W; requires_vw=true; last_verified=null; gated write |
| `grove-sfa-place-survey-stakes` | `cli_command` | `place_survey_stakes` | `vw_plugins/place_survey_stakes.py` | Place BOCO survey corners as symbols in live .vwx; gate: backup required | P-W; requires_vw=true; last_verified=null; gated write |
| `grove-sfa-cleanup-vw-review-layers` | `cli_command` | `cleanup_vw_review_layers` | `vw_plugins/cleanup_vw_review_layers.py` | Remove configured helper/review layers from live .vwx using template-driven lists | P-W; requires_vw=true; last_verified=null; gated write |
| `grove-sfa-normalize-vw-layer-frames` | `cli_command` | `normalize_vw_layer_frames` | `vw_plugins/normalize_vw_layer_frames.py` | Audit layer frames and translate configured helper layers by negative user origin | P-W; requires_vw=true; last_verified=null; gated write |
| `grove-sfa-recover-vw-origin-georef` | `cli_command` | `recover_vw_origin_georef` | `vw_plugins/recover_vw_origin_georef.py` | Combined recovery pass for stale survey layers, helper translation, document georef reapply | P-W; requires_vw=true; last_verified=null; gated write |
| `grove-sfa-probe-file-health-check` | `cli_command` | `probe_file_health_check` | `vw_plugins/probe_file_health_check.py` | Probe whether VW File Health Check web palette can be triggered programmatically | P-W; requires_vw=true; last_verified=null; gated write |
| `grove-sfa-audit-vw-origin-context` | `cli_command` | `audit_vw_origin_context` | `vw_plugins/audit_vw_origin_context.py` | Read-only audit of model drift against internal and user origin with config-driven targeting | P-D; requires_vw=true; last_verified=null |
| `grove-sfa-marpa-programmatic-place-true-plant` | `cli_command` | `marpa_programmatic_place_true_plant` | `vw_plugins/marpa_programmatic_place_true_plant.py` | Place plant using Plant Style Manager programmatically; wrapper pending | P-W; requires_vw=true; last_verified=null; unwrapped |
| `grove-sfa-ingest-landscape-area-composition` | `cli_command` | `ingest_landscape_area_composition` | `ingest/ingest_landscape_area_composition.py` | Ingest landscape area composition CSV into Pixeltable typed rows | H-I; requires_vw=false; last_verified=2026-05-03 |
| `grove-sfa-init-core-pixeltable-schema` | `cli_command` | `init_core_pixeltable_schema` | `schema/sfa_init_core_pixeltable_schema.py` | Initialize live core schema lanes, skip optional DB schema when absent | H-I; requires_vw=false; last_verified=2026-05-04 |
| `grove-sfa-init-cost-schema` | `cli_command` | `init_cost_schema` | `schema/sfa_init_cost_schema.py` | Initialize typed cost-engine Pixeltable schema for budget/QTO/report workflows | H-I; requires_vw=false; last_verified=2026-05-04 |
| `grove-sfa-init-ledger` | `cli_command` | `init_ledger` | `ingest/sfa_init_ledger.py` | Initialize OpenHarness DuckDB ledger and observability tables | H-I; requires_vw=false; last_verified=2026-05-04 |
| `grove-sfa-init-caches` | `cli_command` | `init_caches` | `harness/init_caches.py` | Bootstrap harness DuckDB cache files before refresh and visual QA rebuilds | H-I; requires_vw=false; last_verified=2026-05-04 |
| `grove-sfa-setup-grove` | `cli_command` | `setup_grove` | `harness/setup.py` | Bootstrap local MCP files, env exports, and cache setup for fresh GROVE checkout | H-I; requires_vw=false; last_verified=2026-05-04 |
| `grove-sfa-ingest-plant-supplier-specs` | `cli_command` | `ingest_plant_supplier_specs` | `ingest/ingest_plant_supplier_specs.py` | Ingest plant supplier specifications into schema from external sources | H-I; requires_vw=false; last_verified=null |
| `grove-sfa-budget-ingest` | `cli_command` | `budget_ingest` | `ingest/sfa_budget_ingest.py` | Business-side typed budget ingest for cost engine | H-I; requires_vw=false; last_verified=null |
| `grove-sfa-build-grove-audit-manifest` | `cli_command` | `build_grove_audit_manifest` | `ingest/build_grove_audit_manifest.py` | Host-side deterministic aggregator from audit markers to grove_audit_manifest.json | H-I; requires_vw=false; last_verified=2026-05-04 |
| `grove-sfa-ingest-ifc` | `cli_command` | `ingest_ifc` | `ingest/ingest_ifc.py` | Ingest IFC4.3 geometry and properties into Pixeltable; skip cleanly when absent | H-I; requires_vw=false; last_verified=2026-05-04 |
| `grove-sfa-ingest-dxf` | `cli_command` | `ingest_dxf` | `ingest/ingest_dxf.py` | Ingest DXF or convertible DWG sheets; skip cleanly when inputs absent | H-I; requires_vw=false; last_verified=2026-05-04 |
| `grove-sfa-ingest-database` | `cli_command` | `ingest_database` | `ingest/ingest_database.py` | Ingest typed VW database exports; skip cleanly when source absent | H-I; requires_vw=false; last_verified=2026-05-04 |
| `grove-sfa-ingest-audit-manifest` | `cli_command` | `ingest_audit_manifest` | `ingest/ingest_audit_manifest.py` | Ingest grove_audit_manifest.json into typed source.audit_object_inventory_objects rows | H-I; requires_vw=false; last_verified=2026-05-04 |
| `grove-sfa-ingest-vw-extract` | `cli_command` | `ingest_vw_extract` | `ingest/ingest_vw_extract.py` | Ingest VW extract data into Pixeltable; wrapper pending | H-I; requires_vw=false; last_verified=null; unwrapped |
| `grove-sfa-ingest-vw-safe-extract` | `cli_command` | `ingest_vw_safe_extract` | `ingest/ingest_vw_safe_extract.py` | Ingest VW safe extract data into Pixeltable; wrapper pending | H-I; requires_vw=false; last_verified=null; unwrapped |
| `grove-sfa-build-external-tool-indexes` | `cli_command` | `build_external_tool_indexes` | `harness/openharness/tools/external/build_external_tool_indexes.py` | Refresh external-tool source manifests and catalogs | H-I; requires_vw=false; last_verified=null |
| `grove-sfa-build-visual-qa-views` | `cli_command` | `build_visual_qa_views` | `ingest/build_visual_qa_views.py` | Rebuild read-only visual QA DuckDB mart from audit manifest and ledger | H-D; requires_vw=false; last_verified=2026-05-04 |
| `grove-sfa-build-geojson-export` | `cli_command` | `build_geojson_export` | `ingest/build_geojson_export.py` | Export manifest feature lane into GeoJSON without fabricated geometry | H-D; requires_vw=false; last_verified=2026-05-04 |
| `grove-sfa-reconcile-la-composition` | `cli_command` | `reconcile_la_composition` | `ingest/reconcile_la_composition.py` | Compare landscape area composition against recorded state, report drift | H-D; requires_vw=false; last_verified=2026-05-03 |
| `grove-sfa-refresh-harness-cache` | `cli_command` | `refresh_harness_cache` | `ingest/refresh_harness_cache.py` | Refresh harness DuckDB cache tables | H-D; requires_vw=false; last_verified=null |
| `grove-sfa-budget-validate` | `cli_command` | `budget_validate` | `ingest/sfa_budget_validate.py` | Cost-engine total reconciliation and review-governance validation | H-D; requires_vw=false; last_verified=null |
| `grove-sfa-cost-views` | `cli_command` | `cost_views` | `ingest/sfa_cost_views.py` | DuckDB cost mart and downstream cost views | H-D; requires_vw=false; last_verified=null |
| `grove-sfa-build-qto-views` | `cli_command` | `build_qto_views` | `ingest/sfa_build_qto_views.py` | Budget-side QTO record build and QTO mart refresh | H-D; requires_vw=false; last_verified=null |
| `grove-sfa-qto-reconcile` | `cli_command` | `qto_reconcile` | `ingest/sfa_qto_reconcile.py` | QTO / BOQ reconciliation artifact refresh | H-D; requires_vw=false; last_verified=null |
| `grove-sfa-index-external-tool-repos` | `cli_command` | `index_external_tool_repos` | `harness/openharness/tools/external/sfa_index_repos.py` | Compact SFA/skill catalog refresh for external-tool lane | H-D; requires_vw=false; last_verified=null |
| `grove-sfa-promote-external-tool-skills` | `cli_command` | `promote_external_tool_skills` | `harness/openharness/tools/external/sfa_promote_skills.py` | Promotion candidate generation for external-tool sources | H-D; requires_vw=false; last_verified=null |
| `grove-sfa-derive-scene-plant-locations` | `cli_command` | `derive_scene_plant_locations` | `ingest/derive_scene_plant_locations.py` | Derive scene rows from nested planting DXF inserts; skip cleanly when absent | H-D; requires_vw=false; last_verified=2026-05-04 |
| `grove-sfa-derive-scene-plant-locations-from-dxf` | `cli_command` | `derive_scene_plant_locations_from_dxf` | `ingest/derive_scene_plant_locations_from_dxf.py` | Derive scene rows from typed source.dxf_inserts; skip cleanly when absent | H-D; requires_vw=false; last_verified=2026-05-04 |
| `grove-sfa-derive-plant-tool-exact-payload` | `cli_command` | `derive_plant_tool_exact_payload` | `ingest/derive_plant_tool_exact_payload.py` | Build exact plant tool payload from source species; wrapper pending | H-D; requires_vw=false; last_verified=null; unwrapped |
| `grove-sfa-qa-plant-exactness` | `cli_command` | `qa_plant_exactness` | `ingest/qa_plant_exactness.py` | QA pass/fail report for plant exactness criteria; wrapper pending | H-D; requires_vw=false; last_verified=null; unwrapped |
| `grove-sfa-build-plant-tool-batch-plan` | `cli_command` | `build_plant_tool_batch_plan` | `ingest/build_plant_tool_batch_plan.py` | Build batching plan for plant tool execution; wrapper pending | H-D; requires_vw=false; last_verified=null; unwrapped |
| `grove-sfa-record-plant-sync-tables` | `cli_command` | `record_plant_sync_tables` | `ingest/record_plant_sync_tables.py` | Record plant sync table state snapshots; wrapper pending | H-D; requires_vw=false; last_verified=null; unwrapped |
| `grove-sfa-build-project-report` | `cli_command` | `build_project_report` | `exports/sfa_build_project_report.py` | Static HTML project intelligence report bundle | H-O; requires_vw=false; last_verified=null |
| `grove-sfa-build-tool-catalog` | `cli_command` | `build_tool_catalog` | `harness/sfa_build_tool_catalog.py` | Static HTML harness tool catalog with callable-now and on-deck sections | H-O; requires_vw=false; last_verified=null |
| `grove-sfa-drop-zone-daemon` | `cli_command` | `drop_zone_daemon` | `harness/drop_zone_daemon.py` | Long-running drop-zone watcher with start/stop/status lifecycle actions | H-O; requires_vw=false; last_verified=null; daemon variant |
| `grove-sfa-build-meta-harness-views` | `cli_command` | `build_meta_harness_views` | `harness/build_meta_harness_views.py` | Refresh read-only meta-harness health, closure, and failure views | H-D; requires_vw=false; last_verified=null |
| `grove-sfa-lookup-ifc-class` | `cli_command` | `lookup_ifc_class` | `harness/openharness/tools/browser/sfa_lookup_ifc_class.py` | Scrape buildingsmart.org for IFC class definitions; B-R only, needs Chrome | B-R; requires_vw=false; last_verified=null |
| `grove-sfa-scrape-plant-supplier` | `cli_command` | `scrape_plant_supplier` | `vw_plugins/scrape_plant_supplier.py` | Scrape plant supplier websites for species specs + H-I ingest pipeline | B-R; requires_vw=false; last_verified=null |
| `grove-sfa-audit-georeference` | `cli_command` | `audit_georeference` | `vw_plugins/audit_georeference.py` | Audit document georeference (EPSG/TM); read-only diagnostic | P-D; requires_vw=true; last_verified=null |
| `grove-sfa-audit-ifc-assignment` | `cli_command` | `audit_ifc_assignment` | `vw_plugins/audit_ifc_assignment.py` | Audit IFC class assignments across all objects in document | P-D; requires_vw=true; last_verified=null |
| `grove-sfa-audit-layer-class-inventory` | `cli_command` | `audit_layer_class_inventory` | `vw_plugins/audit_layer_class_inventory.py` | Enumerate all layers and class memberships in document | P-D; requires_vw=true; last_verified=null |
| `grove-sfa-audit-plant-instance-report` | `cli_command` | `audit_plant_instance_report` | `vw_plugins/audit_plant_instance_report.py` | Tabulate all plant instances by species; read-only report | P-D; requires_vw=true; last_verified=null |
| `grove-sfa-audit-plant-style-inventory` | `cli_command` | `audit_plant_style_inventory` | `vw_plugins/audit_plant_style_inventory.py` | Enumerate all plant styles and their counts | P-D; requires_vw=true; last_verified=null |
| `grove-sfa-audit-symbol-inventory` | `cli_command` | `audit_symbol_inventory` | `vw_plugins/audit_symbol_inventory.py` | Enumerate all symbols by folder and count | P-D; requires_vw=true; last_verified=null |
| `grove-sfa-audit-record-field-inventory` | `cli_command` | `audit_record_field_inventory` | `vw_plugins/audit_record_field_inventory.py` | Enumerate all record types and their field definitions | P-D; requires_vw=true; last_verified=null |
| `grove-sfa-audit-object-inventory` | `cli_command` | `audit_object_inventory` | `vw_plugins/audit_object_inventory.py` | Enumerate all objects with type counts | P-D; requires_vw=true; last_verified=null |
| `grove-sfa-audit-record-format-inventory` | `cli_command` | `audit_record_format_inventory` | `vw_plugins/audit_record_format_inventory.py` | Enumerate all record formats and field bindings | P-D; requires_vw=true; last_verified=null |
| `grove-sfa-audit-site-model` | `cli_command` | `audit_site_model` | `vw_plugins/audit_site_model.py` | Enumerate all site model records and their extents | P-D; requires_vw=true; last_verified=null |
| `grove-sfa-audit-worksheet-inventory` | `cli_command` | `audit_worksheet_inventory` | `vw_plugins/audit_worksheet_inventory.py` | Enumerate all worksheets and their dimensions | P-D; requires_vw=true; last_verified=null |
| `grove-sfa-pattern` | `pattern` | SFA Pattern Contract | `SPEC_SFA_PATTERN.md` | PEP 723 + dispatch() + marker JSON L1 SFA contract with 10 variant classes | Architecture contract binding all L1 SFAs; defines forbidden top-level imports, modal dialog rule, marker shape |
| `grove-l2-wrapper-pattern` | `pattern` | L2 Wrapper Pattern Contract | `SPEC_OPENHARNESS_TOOL_WRAPPER.md` + `harness/openharness/tools/_template.py` | 6-slot Pydantic-typed BaseTool wrapper for SFA→MCP exposure (tool card, input, invoke, output, ledger, retry) | Architecture contract; template at _template.py; every concrete wrapper in sfa_*.py subclasses SfaBaseTool |
| `grove-variant-taxonomy` | `doctrine` | SFA Variant Taxonomy | `SPEC_SFA_PATTERN.md` + `TOOL_MANIFEST.yaml` | P-R / P-D / P-W / H-I / H-D / H-O / B-R / B-I / B-D / B-W classification of environment, mutation, timeout, retry defaults | 10 variants with risk classes: P=Polymorphic (VW), H=Host, B=Browser; D=Diagnostic, R=Read, W=Write, I=Ingest, O=Orchestrator |
| `grove-tool-manifest-format` | `pattern` | TOOL_MANIFEST Format | `TOOL_MANIFEST.yaml` | Canonical registry with id / variant / l1_file / l2_wrapper / marker_path / canonical_fields / requires_vw / last_verified per tool | Single source of truth; drives tool_registry.discover(), mcp_server, VW menu, lint baseline |
| `grove-marker-contract` | `pattern` | Marker JSON Handoff Contract | `SPEC_SFA_PATTERN.md` §3 | data/_<tool>.done.json marker as L1→L2 handoff with required ok+timestamp fields plus domain-specific canonical_fields | Marker authority governed by DESIGN_STATE_MODEL.md; markers are non-authoritative ephemeral artifacts |
| `grove-dispatch-helper` | `cli_command` | Dispatch Helper | `vw_plugins/lib/sfa.py` | dispatch(script_path, main_fn, marker_path) helper for dual-path SFA execution (host vs VW) | Canonical for P-* variants; detects environment via is_inside_<env>() guard; enables same SFA file on host or inside bridge |
| `grove-marimo-control-plane` | `pattern` | Marimo Reactive Control Plane | `harness/marimo/grove_control.py` | Reactive Marimo notebook for orchestrating SFAs + viewing DuckDB cache results + ledger events | Operator surface; reads from harness DuckDB caches and OpenHarness ledger |
| `grove-duckdb-cache-substrate` | `pattern` | DuckDB Cache Substrate | `harness/init_caches.py` + `GROVE_ROOT/harness-cache/INDEX.yaml` | 5 DuckDB cache databases under ~/.juniper2026/harness-cache/ as read-only marts for harness tools | Core analytical substrate; initialized by H-I init_caches SFA; refreshed by H-D refresh_harness_cache |
| `grove-marimo-cost-engine` | `pattern` | Marimo Cost Engine Notebook | `harness/marimo/grove_cost_engine.py` | Reactive Marimo notebook for cost calculations, budget validation, QTO reconciliation | Surfaces cost-engine Pixeltable schema and DuckDB cost mart views |

## Evidence

### Help commands

- `uv run /Volumes/PixelTable/GROVE_HARNESS/juniper2026/vw_plugins/extract_plant_positions.py --help` (runs as P-R SFA)
- Each H-I, H-D, H-O, B-R SFA similarly invoked: `uv run <l1_file> --help`
- TOOL_MANIFEST entries validate via `uv run harness/lint/lint_specs.py --strict`

### Docs path

- Canonical registry: `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/TOOL_MANIFEST.yaml` (single source of truth)
- Spec index: `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/SPEC_INDEX.md`
- SFA pattern: `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/SPEC_SFA_PATTERN.md`
- L2 wrapper spec: `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/SPEC_OPENHARNESS_TOOL_WRAPPER.md`
- L2 template: `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/harness/openharness/tools/_template.py`

### Local config path

- Grove root: `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/`
- Cache path: `~/.juniper2026/harness-cache/` (5 DuckDB files + INDEX.yaml)
- Pixeltable home: `$PIXELTABLE_HOME` (configured via env)

### Gaps or unknowns

1. **Unwrapped SFAs** (4 entries in manifest with l2_wrapper=null): marpa_programmatic_place_true_plant, ingest_vw_extract, ingest_vw_safe_extract, derive_plant_tool_exact_payload, qa_plant_exactness, build_plant_tool_batch_plan, record_plant_sync_tables — these have tool cards but wrappers are pending; harvest rows included but integration blocked.
2. **Unverified SFAs** (last_verified=null): 24 SFAs not yet smoke-tested; most H-D and H-O cost-engine tools marked unverified. Marker contracts typed but execution path untested.
3. **File path discrepancy**: TOOL_MANIFEST.yaml references some ingest files (e.g. `ingest_landscape_area_composition.py`) that do not exist in the current file tree; glob shows `sfa_budget_ingest.py`, `sfa_budget_validate.py` instead. Manifest may be stale or files are generated/symbolic. Recommend verifying each l1_file path before promotion.
4. **Marker paths under /tmp**: B-R tools use `/tmp/marker_*.json` instead of `data/` directory; these are ephemeral and not persisted in git, only captured in ledger.
5. **Ledger-only tools**: H-O drop_zone_daemon and other long-running/orchestrator tools use marker JSON but require lifecycle action dispatch; their invocation models differ from oneshot SFAs.
