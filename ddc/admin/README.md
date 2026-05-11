# Admin Dashboard — Data Contracts

The `/admin` route consolidates DDC + LATTICE state into one operator surface. This directory holds the **SQL queries** the dashboard runs against the DuckDB WASM view of the Pixeltable Parquet exports.

| File | What |
|---|---|
| [`project-summary.sql`](project-summary.sql) | Total cost, element count, BOQ completion per project |
| [`element-counts.sql`](element-counts.sql) | Grouped count by BIS class / subclass |
| [`boq-status.sql`](boq-status.sql) | BOQ phase completion percentages |

## Architecture

```
Pixeltable (lattice/bridge/*)
       │
       │  scripts/export-parquet.py
       ▼
public/data/lattice_bridge_*.parquet
       │
       │  DuckDB WASM (in-browser, no server)
       ▼
.sql query  ──►  React component  ──►  /admin route
```

All seven admin panels (per [`../../meta/DDC_MAPPING.md`](../../meta/DDC_MAPPING.md) § ADMIN DASHBOARD) source from:

1. DuckDB WASM SQL (5 panels) — these `.sql` files
2. OpenConstructionERP REST API proxy (2 panels — BOQ line items, phase schedule) — `pixeltable/service/routes/erp.py`

Tracked in [`../../meta/FEATURE_BACKLOG.md`](../../meta/FEATURE_BACKLOG.md) § DDC INTEGRATION → "Admin dashboard route".
