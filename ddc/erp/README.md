# OpenConstructionERP Integration

LATTICE talks to OpenConstructionERP (https://github.com/datadrivenconstruction/OpenConstructionERP, v2.7.0) over its REST API. We never run a fork — we install the upstream package and point our adapter at it.

## Runtime base URL resolution

The ERP adapters and live verifier scripts now resolve their upstream base in this order:

1. `OPENCONSTRUCTIONERP_URL` when it is explicitly set.
2. A matching portless alias from `~/.portless/routes.json`, preferring `OPENCONSTRUCTIONERP_PORTLESS_HOST` when provided and otherwise checking the canonical ERP hostnames (`openconstructionerp*.localhost`, `erp*.localhost`).

If neither exists, the ERP stack stays blocked instead of silently falling through to `http://localhost:8080`. On this workstation that raw port is already claimed by `mlx.marpa.localhost`, so `localhost:8080` is not treated as a safe ERP default.

When the resolved ERP URL is `https://*.localhost`, the adapter/verifier HTTP client disables TLS certificate verification by default so Portless local HTTPS can be reached without a workstation-specific CA install. Set `OPENCONSTRUCTIONERP_VERIFY_TLS=1` to force certificate verification back on.

## Authentication bootstrap

The live BOQ endpoints at `/api/v1/boq/boqs/` are protected by `HTTPBearer`, not by an anonymous session cookie. The ERP adapters and BOQ verifier scripts authenticate in this order:

1. `OPENCONSTRUCTIONERP_ACCESS_TOKEN` — use an already-issued bearer token directly.
2. `OPENCONSTRUCTIONERP_AUTH_EMAIL` + `OPENCONSTRUCTIONERP_AUTH_PASSWORD` — log in through `POST /api/v1/users/auth/login/` and attach the returned JWT automatically.
3. `OPENCONSTRUCTIONERP_AUTH_DEMO_EMAIL` — use `POST /api/v1/users/auth/demo-login/` when the local runtime exposes a seeded demo account.
4. When the resolved ERP runtime is `localhost` / `*.localhost` and no explicit auth env is set, LATTICE automatically tries the upstream seeded demo accounts (`demo@openestimator.io`, then `estimator@openestimator.io`, then `manager@openestimator.io`) through `POST /api/v1/users/auth/demo-login/`.

For a fresh local runtime with no existing account, the honest bootstrap path is:

1. `POST /api/v1/users/auth/register/` to create a local user.
2. `POST /api/v1/users/auth/login/` to obtain the JWT pair.
3. Reuse the same credentials through the env vars above so read/export/sync verifiers can attach `Authorization: Bearer <access_token>`.

When BOQ verifier scripts are authenticated but no explicit verifier project UUID is configured, they now reuse `ERP_BOQ_*_PROJECT_ID` when present or create/find a dedicated `LATTICE BOQ Verifier Project` through `/api/v1/projects/` so the live ERP sees a valid UUID-backed project context.

## What goes where

| Adapter file | What it does |
|---|---|
| [`boq-adapter.py`](boq-adapter.py) | For each `ifc_elements` row → `POST /api/v1/boq/boqs/` → write `erp_item_id` + `unit_cost` back to Pixeltable |
| [`cost-export.py`](cost-export.py) | Resolve a project BOQ via `GET /api/v1/boq/boqs/?project_id=...` and export it through the ERP export API |
| [`phase-adapter.py`](phase-adapter.py) | Verify the smallest honest 4D/5D seam (project-addressable IFC + per-phase schedule_id/task_id) and fail closed until the bounded ERP write path lands |

## LATTICE endpoints these adapters power

These FastAPI routes live in `pixeltable/service/routes/erp.py`.

| Sidecar endpoint | Adapter called | Purpose |
|---|---|---|
| `POST /v1/erp/boq` | `boq-adapter.py` | Create / refresh a BOQ from current Pixeltable element rows |
| `POST /v1/erp/cost-search` | `../cwicr/cost-search.py` | Semantic cost lookup (CWICR, not ERP) |
| `GET  /v1/erp/boq/{project_id}` | `boq-adapter.py` | Return current BOQ for a project |
| `GET  /v1/erp/export/{project_id}` | `cost-export.py` | Download Excel/CSV BOQ |
| `POST /v1/erp/phases` | `phase-adapter.py` | Verify the local 4D/5D seam and return the exact bounded blocker until the schedule write path is implemented |

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
