---
description: Manage DDC skill index, Qdrant cost database, OpenConstructionERP BOQ adapter, and BOQ coverage in lattice/bridge/ifc_elements and lattice/execution/boq_items.
---

# LATTICE DDC Integration, Qdrant, and BOQ

The ddc section owns the DDC skill mapping in `meta/DDC_MAPPING.md` (221 skills),
the Qdrant vector database at `localhost:6333` (`ddc-skills` and `cost-items`
collections), the OpenConstructionERP BOQ adapter, and `lattice/execution/boq_items`.
The scoring script `scripts/score-ddc.sh` checks CI pass rate, DDC skill count,
BOQ coverage, and Qdrant health. This skill is distinct from `lattice-ci` which
owns the CI workflow files themselves.

## When this skill applies

- Verifying or re-indexing the DDC skill index in Qdrant
- Running the BOQ ingest pass to assign `erp_item_id` to IFC elements
- Checking Qdrant health and cost database completeness
- Querying DDC skills by semantic similarity
- Running the ddc section cycle: `bash meta/harness/bootstrap/run-autoresearch.sh ddc`
- `boq_items` table is empty or IFC elements have null `erp_item_id`

## How it works

1. Check Qdrant health:
   ```bash
   curl -s http://localhost:6333/health | jq .
   ```
   Expected: `{"status":"ok"}`. If Qdrant is offline, the BOQ adapter stalls
   and financial reporting breaks — restart Qdrant before proceeding.

2. Verify DDC skill count matches the index:
   ```bash
   grep -c "^- id:" meta/DDC_MAPPING.md
   ```
   Must equal the Qdrant points count:
   ```bash
   curl -s http://localhost:6333/collections/ddc-skills/points/count | jq .result.count
   ```
   If counts differ, reindex from `meta/DDC_MAPPING.md`.

3. Query DDC skills by semantic similarity:
   ```python
   import httpx, json
   query_vector = embed("landscape irrigation system")  # your embedding fn
   resp = httpx.post("http://localhost:6333/collections/ddc-skills/points/search",
       json={"vector": query_vector, "limit": 5, "with_payload": True})
   print(resp.json())
   ```

4. Run BOQ ingest pass:
   - Call OpenConstructionERP API to fetch BOQ items for the active project.
   - Match each item to `lattice/bridge/ifc_elements` rows by `ifc_class` + classification.
   - Write `erp_item_id`, `unit_cost`, `quantity` to the element row.
   - Insert aggregated rows into `lattice/execution/boq_items` with cost rollup.

5. Verify BOQ coverage:
   ```python
   import pixeltable as pxt
   t = pxt.get_table("lattice/bridge/ifc_elements")
   null_erp = t.select(t.source_element_id).where(t.erp_item_id == None).collect()
   print(f"{len(null_erp)} elements missing erp_item_id")
   ```
   Must be 0 after a complete BOQ pass.

6. Cost database query pattern (via Qdrant `cost-items` collection):
   ```bash
   curl -s -X POST http://localhost:6333/collections/cost-items/points/search \
     -H "Content-Type: application/json" \
     -d '{"vector": [...], "limit": 10, "with_payload": true}'
   ```

7. Reindex DDC skills if count drifts:
   ```python
   # Parse meta/DDC_MAPPING.md, embed each skill description, upsert to Qdrant
   # ddc-skills collection with id=skill_id, vector=embedding, payload=skill_dict
   ```

## Files used

- `meta/DDC_MAPPING.md` — 221 DDC skill definitions (canonical source)
- `ddc/GOAL.md` — ddc section fitness function
- `pixeltable/service/routes/ddc.py` — FastAPI routes for DDC and BOQ
- `lattice/bridge/ifc_elements` — erp_item_id assigned by BOQ pass
- `lattice/execution/boq_items` — cost + schedule items per project
- `scripts/score-ddc.sh` — section scoring script
- `runtime-runs/<run-id>/ddc-ci-audit.md` — CI audit scratch output

## Constraints

- Qdrant must be healthy before any BOQ pass. Never attempt BOQ ingest when
  `curl -s http://localhost:6333/health` returns non-ok.
- DDC skill count in `meta/DDC_MAPPING.md` (line count of `^- id:` entries) must
  equal the Qdrant `ddc-skills` collection point count at all times. Drift triggers
  an automatic reindex.
- BOQ ingest is single-writer: acquire `/tmp/vwbridge-ddc.lock` before starting.
  Max 1 BOQ ingest job at a time.
- `erp_item_id` must be populated for every `lattice/bridge/ifc_elements` row after
  a BOQ pass. Null `erp_item_id` rows block financial reporting.
- Never hardcode Qdrant API keys or OpenConstructionERP credentials in source files.
  Use environment variables only.
- This skill owns data integration and semantic search. CI workflow file authoring
  lives in the `lattice-ci` skill.
