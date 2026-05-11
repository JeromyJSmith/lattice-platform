# OpenConstructionERP Integration

LATTICE talks to OpenConstructionERP (https://github.com/datadrivenconstruction/OpenConstructionERP, v2.7.0) over its REST API. We never run a fork — we install the upstream package and point our adapter at it.

## What goes where

| Adapter file | What it does |
|---|---|
| [`boq-adapter.py`](boq-adapter.py) | For each `ifc_elements` row → `POST /api/boq/create` → write `erp_item_id` + `unit_cost` back to Pixeltable |
| [`cost-export.py`](cost-export.py) | Pull full BOQ via `GET /api/boq/{project_id}` and export to Excel/CSV via the ERP's export API |
| [`phase-adapter.py`](phase-adapter.py) | Join `ifc_elements` with the project's Linear schedule, emit 4D/5D phase data into the ERP |

## LATTICE endpoints these adapters power

These FastAPI routes live in `pixeltable/service/routes/erp.py` (not yet created — tracked as backlog item "OpenConstructionERP BOQ").

| Sidecar endpoint | Adapter called | Purpose |
|---|---|---|
| `POST /v1/erp/boq` | `boq-adapter.py` | Create / refresh a BOQ from current Pixeltable element rows |
| `POST /v1/erp/cost-search` | `../cwicr/cost-search.py` | Semantic cost lookup (CWICR, not ERP) |
| `GET  /v1/erp/boq/{project_id}` | `boq-adapter.py` | Return current BOQ for a project |
| `GET  /v1/erp/export/{project_id}` | `cost-export.py` | Download Excel/CSV BOQ |
| `POST /v1/erp/phases` | `phase-adapter.py` | Update 4D/5D phase assignments |

## Pixeltable schema additions

When implementing the BOQ adapter, add these columns to `lattice/bridge/ifc/ifc_elements` via migration:

```python
"erp_item_id":       pxt.String,
"unit_cost":         pxt.Float,
"unit_cost_region":  pxt.String,
"quantity":          pxt.Float,
"quantity_unit":     pxt.String,   # m², m³, ea, lm
"boq_phase":         pxt.String,
"cost_last_updated": pxt.Timestamp,
```

And to `lattice/execution/evidence`:

```python
"ddc_skill_id":      pxt.String,
"erp_project_id":    pxt.String,
```

See [`../../meta/DDC_MAPPING.md`](../../meta/DDC_MAPPING.md) § DDC PIXELTABLE SCHEMA ADDITIONS for the canonical list.
