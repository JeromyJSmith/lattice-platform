# VW Universe Extraction + DDC Enrichment Plan
**Status: IN PROGRESS**
**Created: 2026-05-13**
**Owner: LATTICE / vwx-mcp + ddc pipeline**

> This file is the authoritative task list for the full extraction-to-enrichment pipeline: VW → Pixeltable → DDC verification → cost estimation → BOQ. If the conversation is lost, pick up from the first unchecked task.

---

## What This Plan Covers

Two parallel tracks that converge after extraction:

```
VW 2026 (GUI open)
  └─ extract_all.py        ← Python 3.9.2 inside VW
       └─ produces: IFC, DXF, JSON, CSV files
            │
            ▼
  ingest_exports.py        ← Python 3.12 sidecar (uv)
       └─ writes: lattice/bridge/ifc_elements rows
            │
            ├─ CWICR cost search  ← Qdrant semantic lookup (55,719 items)
            │    └─ writes: unit_cost, unit_cost_region per element
            │
            └─ BOQ adapter        ← OpenConstructionERP API
                 └─ writes: erp_item_id, boq_phase, quantity per element
                      │
                      ▼
            DDC verification skills  ← AI agent BIM validation
                 └─ writes: QC reports to lattice/execution/evidence
```

**DDC layer is NOT optional.** Extracted rows without cost data, BOQ IDs, and verification are incomplete. Extraction without enrichment is half the job.

---

## Readiness Status

| Component | File | State |
|-----------|------|-------|
| VectorScript preflight | `vw-plugin/scripts/preflight_probe.vs` | READY |
| Python extraction | `vw-plugin/scripts/extract_all.py` | READY |
| Sidecar ingest | `pixeltable/service/ingest/ingest_exports.py` | READY |
| CWICR cost search | `ddc/cwicr/cost-search.py` | STUB — needs Qdrant setup |
| BOQ adapter | `ddc/erp/boq-adapter.py` | STUB — needs ERP running + implementation |
| DDC skills index | `ddc/skills/` | STUB — skills not yet synced from upstream |
| Admin SQL reports | `ddc/admin/*.sql` | READY (queries only, no data yet) |

---

## Pre-Flight Rules (apply to every VWX file before extract_all.py)

1. Open in VW 2026. Dismiss migration dialogs. `Cmd+S`. Wait for save to complete.
2. `File > Document Settings > IFC Settings` → schema must show **IFC4X3**. Fix and re-save if wrong.
3. One file at a time. `ForEachObject` only iterates the active document.
4. Do not interrupt VW while the script runs. No timeout exists — VW freezes but does not crash.

---

## The Five Files

| # | Project ID | Path | Size | Extracted | Ingested | Enriched |
|---|-----------|------|------|-----------|---------|---------|
| 1 | `institutional` | `.../institutional/institutional-project-gallery-196.vwx` | 266 MB | `[ ]` | `[ ]` | `[ ]` |
| 2 | `riverwood` | `.../riverwood/2025-riverwood-townhomes.vwx` | 327 MB | `[ ]` | `[ ]` | `[ ]` |
| 3 | `cube-landscape` | `.../cube-landscape/2025-the-cube-landscape.vwx` | 883 MB | `[ ]` | `[ ]` | `[ ]` |
| 4 | `urban-park` | `.../urban-park/urban-park-2025.vwx` | 1.0 GB | `[ ]` | `[ ]` | `[ ]` |
| 5 | `lakehouse` | `.../lakehouse/lakehouse-landscape-project-2026.vwx` | 1.5 GB | `[ ]` | `[ ]` | `[ ]` |

Base path for all: `/Volumes/PixelTable/vw-samples/`

---

## Task List

### Phase 0 — LATTICE environment check (one-time)

- [ ] **T0.1** Confirm vwx-mcp bridge alive: ping via vwx-mcp tool or `curl -s http://localhost:9878/health`. If not running, start it per `CLAUDE.md > USEFUL COMMANDS`.
- [ ] **T0.2** Confirm FastAPI sidecar alive: `curl -s http://localhost:8001/health`. If not: `cd pixeltable/service && PIXELTABLE_HOME=/Volumes/PixelTable/.pixeltable PYTHONPATH=/Volumes/PixelTable/schemas uv run python main.py`
- [ ] **T0.3** Confirm Pixeltable tables exist: `lattice/bridge/ifc_elements` and `lattice/bridge/dwg_entities`. If missing, run migration 0014 first.

---

### Phase 0B — DDC environment setup (one-time, can run in parallel with Phase 1)

These steps set up the enrichment infrastructure. Run them while extraction is happening — they don't block the extraction phases.

**CWICR / Qdrant:**
- [ ] **T0B.1** Confirm OrbStack installed: `orbctl status`. If not: `brew install orbstack`.
- [ ] **T0B.2** Start Qdrant via OrbStack Docker:
  ```bash
  docker run -d \
    --name lattice-qdrant \
    -p 6333:6333 \
    -p 6334:6334 \
    -v $HOME/.lattice/qdrant:/qdrant/storage \
    qdrant/qdrant:latest
  ```
- [ ] **T0B.3** Verify Qdrant responds: `curl -s http://localhost:6333/collections | jq .`
- [ ] **T0B.4** Seed the 55,719 CWICR cost items (expect ~3 min on Apple Silicon):
  ```bash
  bash ddc/cwicr/seed-qdrant.sh
  ```
- [ ] **T0B.5** Verify CWICR seeded — test a live query:
  ```bash
  uv run python3 ddc/cwicr/cost-search.py "concrete slab 10cm reinforced" --region US --top 3
  ```
  Must return JSON with `unit_cost` fields. If raises `NotImplementedError` → the stub is not yet implemented (see T0B.6).
- [ ] **T0B.6** *(If T0B.5 hits NotImplementedError)* Implement `ddc/cwicr/cost-search.py` per the docstring sketch in that file. The sketch is complete — uncomment it, add `uv add sentence-transformers qdrant-client`.

**OpenConstructionERP:**
- [ ] **T0B.7** Install OpenConstructionERP:
  ```bash
  uv add openconstructionerp  # or: docker pull datadrivenconstruction/openconstructionerp:2.7.0
  ```
- [ ] **T0B.8** Start the ERP service and confirm it responds at `http://localhost:8080/api`.
- [ ] **T0B.9** *(When ERP is running)* Implement `ddc/erp/boq-adapter.py` per the sketch in that file. Uncomment the `sync_boq()` body — `uv add httpx` is the only new dep.

---

### Phase 1 — institutional (266 MB) — EXTRACTION

- [ ] **T1.1** Open `institutional-project-gallery-196.vwx` in VW 2026. Dismiss migration dialogs. `Cmd+S`.
- [ ] **T1.2** Verify IFC scheme → **IFC4X3**. Fix and save if wrong.
- [ ] **T1.3** Run extraction via vwx-mcp `execute_script`:
  ```python
  import os
  os.environ['LATTICE_PROJECT_ID'] = 'institutional'
  exec(open('/Volumes/PixelTable/VW_iTWIN_Bridge/VW_iTwin_Bridge/vw-plugin/scripts/extract_all.py').read())
  ```
- [ ] **T1.4** Validate manifest at `/Volumes/PixelTable/vw-samples/institutional/extract_output/<timestamp>/manifest.json`:
  - `"ok": true`
  - `phases.layers.count > 0`
  - `phases.ifc_export.ok: true`
- [ ] **T1.5** Mark **Extracted** column for `institutional` in the status table above.

### Phase 1B — institutional — INGEST + ENRICHMENT

- [ ] **T1B.1** Run sidecar ingest (replace `<timestamp>`):
  ```bash
  PIXELTABLE_HOME=/Volumes/PixelTable/.pixeltable \
  uv run pixeltable/service/ingest/ingest_exports.py \
    /Volumes/PixelTable/vw-samples/institutional/extract_output/<timestamp> \
    institutional
  ```
- [ ] **T1B.2** Verify Pixeltable rows written:
  ```python
  import pixeltable as pxt
  t = pxt.get_table('lattice/bridge/ifc_elements')
  rows = t.where(t.project_id == 'institutional').collect()
  print(len(rows), 'ifc_elements rows')
  ```
- [ ] **T1B.3** *(Requires T0B.5 complete)* Run CWICR cost search across extracted element types:
  ```bash
  PIXELTABLE_HOME=/Volumes/PixelTable/.pixeltable \
  uv run python3 ddc/cwicr/cost-search.py \
    "$(pxt select bis_subclass from lattice/bridge/ifc_elements where project_id='institutional' limit 1)" \
    --region US --top 5
  ```
  Confirm results return with `unit_cost`. Then run the full enrichment pass (once `erp.py` route exists).
- [ ] **T1B.4** *(Requires T0B.9 complete)* Run BOQ adapter:
  ```bash
  PIXELTABLE_HOME=/Volumes/PixelTable/.pixeltable \
  uv run python3 ddc/erp/boq-adapter.py institutional
  ```
  Confirm `erp_item_id` is populated on `lattice/bridge/ifc_elements` rows.
- [ ] **T1B.5** Run DDC verification skill (AI agent BIM validation):
  ```bash
  claude -p "$(cat ddc/skills/README.md)" \
    "Verify the IFC export at /Volumes/PixelTable/vw-samples/institutional/extract_output/<timestamp>/ifc/export_ifc4x3.ifc.
     Check: element count plausibility, required property sets present, georeferencing set, IFC4X3 schema.
     Write a QC report to lattice/execution/evidence."
  ```
- [ ] **T1B.6** Check DDC admin SQL for this project:
  ```bash
  # In a DuckDB session against the Pixeltable Parquet export:
  duckdb -c ".read ddc/admin/project-summary.sql" \
    -c ".read ddc/admin/element-counts.sql"
  ```
- [ ] **T1B.7** Mark **Ingested** and **Enriched** columns for `institutional` in status table.

---

### Phase 2 — riverwood (327 MB) — EXTRACTION + INGEST + ENRICHMENT

- [ ] **T2.1** Close institutional. Open `2025-riverwood-townhomes.vwx`. Dismiss migration dialogs. `Cmd+S`.
- [ ] **T2.2** Verify IFC scheme → **IFC4X3**.
- [ ] **T2.3** Run extraction:
  ```python
  import os
  os.environ['LATTICE_PROJECT_ID'] = 'riverwood'
  exec(open('/Volumes/PixelTable/VW_iTWIN_Bridge/VW_iTwin_Bridge/vw-plugin/scripts/extract_all.py').read())
  ```
- [ ] **T2.4** Validate manifest: `ok: true`, `ifc_export.ok: true`, `layers.count > 0`.
- [ ] **T2.5** Run sidecar ingest → verify rows → CWICR cost search → BOQ adapter → DDC verification. (Same steps as T1B.1–T1B.6, substituting `riverwood` and its output path.)
- [ ] **T2.6** Mark **Extracted**, **Ingested**, **Enriched** for `riverwood`.

---

### Phase 3 — cube-landscape (883 MB) — EXTRACTION + INGEST + ENRICHMENT

- [ ] **T3.1** Close riverwood. Open `2025-the-cube-landscape.vwx`. Dismiss migration. `Cmd+S`.
- [ ] **T3.2** Verify IFC scheme → **IFC4X3**.
- [ ] **T3.3** Run extraction:
  ```python
  import os
  os.environ['LATTICE_PROJECT_ID'] = 'cube-landscape'
  exec(open('/Volumes/PixelTable/VW_iTWIN_Bridge/VW_iTwin_Bridge/vw-plugin/scripts/extract_all.py').read())
  ```
  At 883 MB expect 10–20 min. VW will be unresponsive.
- [ ] **T3.4** Validate manifest.
- [ ] **T3.5** Ingest + enrich. (T1B pattern, substituting `cube-landscape`.)
- [ ] **T3.6** Mark status table.

---

### Phase 4 — urban-park (1.0 GB) — EXTRACTION + INGEST + ENRICHMENT

- [ ] **T4.1** Close cube-landscape. Open `urban-park-2025.vwx`. Dismiss migration. `Cmd+S`.
- [ ] **T4.2** Verify IFC scheme → **IFC4X3**.
- [ ] **T4.3** Run extraction:
  ```python
  import os
  os.environ['LATTICE_PROJECT_ID'] = 'urban-park'
  exec(open('/Volumes/PixelTable/VW_iTWIN_Bridge/VW_iTwin_Bridge/vw-plugin/scripts/extract_all.py').read())
  ```
  At 1.0 GB expect 20–30 min.
- [ ] **T4.4** Validate manifest.
- [ ] **T4.5** Ingest + enrich. (T1B pattern, substituting `urban-park`.)
- [ ] **T4.6** Mark status table.

---

### Phase 5 — lakehouse (1.5 GB) — EXTRACTION + INGEST + ENRICHMENT

- [ ] **T5.1** Close urban-park. Open `lakehouse-landscape-project-2026.vwx`. Dismiss migration. `Cmd+S`.
- [ ] **T5.2** Verify IFC scheme → **IFC4X3**.
- [ ] **T5.3** Run extraction:
  ```python
  import os
  os.environ['LATTICE_PROJECT_ID'] = 'lakehouse'
  exec(open('/Volumes/PixelTable/VW_iTWIN_Bridge/VW_iTwin_Bridge/vw-plugin/scripts/extract_all.py').read())
  ```
  At 1.5 GB expect 30–45 min. Do not interrupt.
- [ ] **T5.4** Validate manifest.
- [ ] **T5.5** Ingest + enrich. (T1B pattern, substituting `lakehouse`.)
- [ ] **T5.6** Mark status table.

---

### Phase 6 — Cross-project validation

- [ ] **T6.1** Confirm all five project IDs present in Pixeltable:
  ```python
  import pixeltable as pxt
  from collections import Counter
  t = pxt.get_table('lattice/bridge/ifc_elements')
  print(Counter(r['project_id'] for r in t.select(t.project_id).collect()))
  # Expected: {'institutional': N, 'riverwood': N, 'cube-landscape': N, 'urban-park': N, 'lakehouse': N}
  ```
- [ ] **T6.2** Confirm BOQ coverage (zero unlinked rows after enrichment):
  ```python
  nulls = t.where(t.erp_item_id == None).collect()
  print(len(nulls), 'rows without erp_item_id')  # target: 0
  ```
- [ ] **T6.3** Confirm CWICR coverage (unit_cost populated):
  ```python
  no_cost = t.where(t.unit_cost == None).collect()
  print(len(no_cost), 'rows without unit_cost')  # target: 0
  ```
- [ ] **T6.4** Run full DDC admin dashboard queries:
  ```bash
  duckdb -c ".read ddc/admin/project-summary.sql" \
         -c ".read ddc/admin/element-counts.sql" \
         -c ".read ddc/admin/boq-status.sql"
  ```
- [ ] **T6.5** Update this file's top **Status** field to `COMPLETE`.
- [ ] **T6.6** Update `meta/HANDOFF.md` with extraction + enrichment completion note.

---

## Failure Modes and Fixes

### IFC export returns `ok: false`
- IFC scheme not set to IFC4X3 → fix in `File > Document Settings > IFC Settings` → save → re-run.
- Document in bad migration state → close VW, reopen, save manually, retry.

### `phases.layers.count == 0`
Script uses `vs.FLayer()`. If 0, check `extract.log` in output dir for the phase that failed.

### Worksheet cells empty with `worksheets.count > 0`
Known Medium-risk gap (SYNTHESIS). Not a blocker for IFC/layer/plant data. Log and continue.

### VW frozen beyond 2× expected time
Force-quit VW. Reopen file. Check `extract.log` for last completed phase. Re-run — script is idempotent (new timestamp output dir each run).

### `ingest_exports.py` fails: `ifcopenshell not found`
```bash
cd /Volumes/PixelTable/VW_iTWIN_Bridge/VW_iTwin_Bridge
uv add ifcopenshell ezdxf
```

### `cost-search.py` raises `NotImplementedError`
The CWICR stub needs implementing. See docstring sketch in `ddc/cwicr/cost-search.py` — uncomment the body, then:
```bash
uv add sentence-transformers qdrant-client
```
Requires T0B.1–T0B.4 complete first (Qdrant running + seeded).

### `boq-adapter.py` raises `NotImplementedError`
Same pattern — uncomment the `sync_boq()` sketch in `ddc/erp/boq-adapter.py`:
```bash
uv add httpx
```
Requires OpenConstructionERP running at `localhost:8080`.

### `lattice/bridge/ifc_elements` missing `erp_item_id` column
The DDC schema columns aren't in migration 0014. Need a migration 0017 that adds:
`erp_item_id`, `unit_cost`, `unit_cost_region`, `quantity`, `quantity_unit`, `boq_phase`, `cost_last_updated`
Per `ddc/erp/README.md § Pixeltable schema additions`. Create `pixeltable/migrations/0017_ddc_enrichment_columns.py`.

---

## Key File Locations

| File | Purpose |
|------|---------|
| `vw-plugin/scripts/extract_all.py` | VW-side extraction (Python 3.9.2 inside VW) |
| `vw-plugin/scripts/preflight_probe.vs` | VectorScript pre-flight check |
| `pixeltable/service/ingest/ingest_exports.py` | Sidecar ingest (Python 3.12) |
| `ddc/cwicr/cost-search.py` | CWICR unit cost lookup (stub → implement) |
| `ddc/cwicr/seed-qdrant.sh` | One-time: seed 55,719 items into Qdrant |
| `ddc/cwicr/INSTALL.md` | Full Qdrant + OrbStack setup instructions |
| `ddc/erp/boq-adapter.py` | OpenConstructionERP BOQ sync (stub → implement) |
| `ddc/admin/*.sql` | DDC reporting queries |
| `meta/DDC_MAPPING.md` | Full DDC integration map (6 repos) |
| `meta/capability-research/census/vw-scripting-extraction-research/SYNTHESIS.md` | All confirmed VW API patterns |
| `projects/registry.yaml` | Project ID ↔ VWX path registry |
| `meta/SCHEMA.md` | Pixeltable table reference |

---

## Related Plans and Research

- `meta/capability-research/RESEARCH_PROPOSAL_VW_SCRIPTING_EXTRACTION.md` — original research proposal
- `meta/capability-research/census/vw-scripting-extraction-research/SYNTHESIS.md` — GO decision + canonical patterns
- `meta/harness/PLAN/00-OVERVIEW.md` — LATTICE meta-harness overview
- `ddc/GOAL.md` — DDC harness fitness function and improvement loop
- DDC upstream: `github.com/datadrivenconstruction` (6 repos, see DDC_MAPPING.md)

---

*Update checkboxes and the status table as tasks complete. Mark `[x]` not delete — the history matters.*
