# Repo Census 004 — ODBC And Database-Link Opportunities

Date: 2026-05-13
Status: broad ODBC sweep, live web and GitHub metadata

This census maps ODBC opportunities for the Vectorworks -> Pixeltable data
spine. The search intentionally started broad, then narrowed to surfaces that
could help synchronize Vectorworks records, worksheets, classes, styles, and
external estimating data without making ODBC the durable database.

## Why ODBC Matters

Vectorworks has native database connectivity concepts: record format database
connections, object database connections, update settings, ODBC driver setup,
and database-to-Vectorworks communication. That makes ODBC a credible bridge for
firm price sheets, legacy estimating databases, and bidirectional object record
sync.

LATTICE still treats Pixeltable as the source-of-truth substrate. ODBC is an
ingest/sync bridge, not a replacement database.

## Source Classes

### Vectorworks-Native ODBC And Database Docs

- Vectorworks database setup and ODBC workflow docs.
- Vectorworks ODBC driver information docs.
- Vectorworks worksheet/database docs.
- Vectorworks Data Manager guide.
- Old Vectorworks ODBC connectivity PDF/forum attachment.
- Old community Postgres/MySQL ODBC examples:
  - `https://github.com/rgm/vectorworks-postgres`
  - `https://github.com/rgm/vectorworks-mysql`

Harvest focus:

- record format database connection
- object database connection
- database-to-Vectorworks update flow
- Vectorworks-to-database update flow
- worksheet/database-row semantics
- driver support matrix
- field mapping and update settings

### Driver Managers And Cross-Platform ODBC Substrate

- `https://github.com/lurcher/unixODBC`
- `https://github.com/openlink/iODBC`

Harvest focus:

- macOS/Linux ODBC manager setup
- driver registry files
- DSN configuration shape
- CLI diagnostic patterns
- license/runtime constraints

### Python, Arrow, Parquet, And Fast Export Bridges

- `https://github.com/mkleehammer/pyodbc`
- `https://github.com/blue-yonder/turbodbc`
- `https://github.com/pacman82/arrow-odbc-py`
- `https://github.com/pacman82/odbc2parquet`
- `https://github.com/pacman82/odbc-api`
- `https://github.com/pacman82/odbcsv`

Harvest focus:

- ODBC -> Arrow batches
- ODBC -> Parquet
- ODBC -> CSV
- Python DB-API access
- deterministic export fixtures
- performance and memory caveats

### Current Vendor Driver Surfaces

- Microsoft ODBC Driver 18 for SQL Server.
- PostgreSQL `psqlODBC`.
- MySQL Connector/ODBC.
- Snowflake ODBC.
- AWS Redshift ODBC and AWS Advanced ODBC Wrapper.
- MariaDB Connector/ODBC.

Harvest focus:

- current versions and platform support
- macOS/Apple Silicon viability
- license constraints
- connection-string fields that should be treated as secrets
- failure/logging diagnostics

## First LATTICE ODBC Proof Shape

Do not connect to a live external database first. Use deterministic file-backed
fixtures:

```text
fixture DSN/config manifest
-> fixture table schema for Vectorworks record/class/style data
-> fixture rows representing object record updates and price-sheet entries
-> export to CSV/Parquet/Arrow shape
-> verify field mapping, primary key, direction, and denied secret fields
```

Proof acceptance:

- no real credentials
- no `.env*`
- no live database connection
- all connection-string secret-like fields are redacted
- expected fields are present:
  - `source_element_id`
  - `record_format`
  - `field_name`
  - `field_value`
  - `class_name`
  - `layer_name`
  - `style_name`
  - `price_source`
  - `sync_direction`
  - `updated_at`
- output artifact names the intended Vectorworks update path but does not
  mutate a document

## Candidate Top Rows

The matching registry is:

```text
analysis/capabilities/repo-census-004-odbc-capability-registry.yaml
```

Top rows:

1. Vectorworks native ODBC/database workflow.
2. Vectorworks worksheet database-row semantics.
3. Vectorworks Data Manager field mapping.
4. Vectorworks Postgres/MySQL ODBC community references.
5. unixODBC and iODBC manager setup.
6. `pyodbc` and `turbodbc` Python adapters.
7. `arrow-odbc-py`, `odbc2parquet`, and `odbcsv` export bridges.
8. Microsoft SQL Server ODBC driver.
9. PostgreSQL `psqlODBC`.
10. MySQL/MariaDB/Snowflake/AWS cloud ODBC drivers.

## Not Now

- Do not make ODBC durable storage.
- Do not store connection strings or credentials.
- Do not connect Vectorworks directly to Pixeltable internals.
- Do not replace the Python/SDK/plugin extraction path with ODBC.
- Do not run live database updates until a fixture proves field mapping,
  direction, and rollback expectations.

