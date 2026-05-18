# Governed Estimation Contract

This directory holds the **DDC estimation planning slice** for LATTICE. Estimation is **not** a standalone worksheet app and it is **not** green just because one cost lookup or one BOQ export works. It is a governed, project-agnostic capability that depends on multiple DDC surfaces turning usable together.

- Goal surface: [`GOAL.md`](GOAL.md)
- Execution contract: [`GOLDENPATH.md`](GOLDENPATH.md)
- Source packet: [`source/README.md`](source/README.md)
- Dual contract package: `contract/`, `fixtures/`, `kernel/`, `reports/`

## Operational framing

- **Operational target project:** `MARPA — 918 Juniper Avenue`
- **Repo-local source lineage:** `Farber-Haines [2521]` IFC fixture attached to the Juniper project surface
- **Pilot proof lineage only:** `ROSE Residence` workbook contract shaped the estimation rules, but it is not the operational fixture in this repository

Juniper Avenue is the proving ground for future promotion. ROSE Residence stays proof lineage only.

## Dual contract package

This slice now keeps two contract families side by side:

1. **Workbook faithful evidence contract**
   - `contract/worksheet.schema.json`
   - `contract/worksheet.normalized.schema.json`
2. **Estimate capability operational contract**
   - `contract/estimate-project.schema.json`
   - `contract/estimate-pricebook-item.schema.json`
   - `contract/estimate-line-item.schema.json`
   - `contract/estimate-audit-run.schema.json`

They stay synchronized through:

- `source/provenance.json`
- `fixtures/rose_residence/`
- `fixtures/juniper_avenue/`
- `fixtures/expected-failures.yaml`
- `kernel/formulas.yaml`
- `kernel/estimation_rules.yaml`

## What this capability means in LATTICE

The governed estimation path is:

1. project-scoped IFC rows exist in `lattice/bridge/ifc/ifc_elements`
2. CWICR returns bounded, verifier-backed unit-cost matches
3. cost enrichment writes those results back into owned Pixeltable rows
4. BOQ sync creates or refreshes ERP line items
5. BOQ read/export can round-trip the resulting project state
6. phase sync preserves schedule context for the same project
7. quantity takeoff orchestration captures evidence and blocker state instead of silently skipping gaps

If one of those steps is missing, the estimation capability is still blocked.

## Dependency chain

### Already helping now

- `cwicr-seed`
- `cwicr-qdrant-cost-search`
- `ifc-cost-enrichment`
- `boq-sync`
- `boq-read`
- `boq-export`
- `phases-sync`
- `quantity-takeoff-agent`

### Still blocking promotion

### Useful later, but not the first gate

- `admin-sql`
- `admin-route`
- `cost-per-zone`
- `cost-overlay`
- `skills-search-api`

## Current state

Current state is **governed and verifier-backed**. Juniper Avenue now completes the bounded end-to-end governed run with explicit dependency reuse, writeback, BOQ linkage, BOQ round-trip, and evidence capture.

The green claim is now additionally backed by the contract package:

- schemas validate as Draft 2020-12
- valid ROSE and Juniper fixtures validate
- invalid fixtures fail for exact traceability and verifier-evidence reasons
- line items carry explicit traceability back to workbook rows, formulas, and source artifacts

## Green-state rule

This capability turns green only when:

- Juniper Avenue runs end to end through the governed estimation path
- dependent green capabilities are explicitly reused, not assumed
- blocked prerequisites are either promoted or surfaced as honest blockers
- evidence exists for the project-scoped run, BOQ linkage, and cost writeback path

Anything less reopens the contract and drops it out of green.
