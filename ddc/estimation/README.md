# Governed Estimation Contract

This directory holds the **DDC estimation planning slice** for LATTICE. Estimation is **not** a standalone worksheet app and it is **not** green just because one cost lookup or one BOQ export works. It is a governed, project-agnostic capability that depends on multiple DDC surfaces turning usable together.

## Operational framing

- **Operational target project:** `MARPA — 918 Juniper Avenue`
- **Repo-local source lineage:** `Farber-Haines [2521]` IFC fixture attached to the Juniper project surface
- **Pilot proof lineage only:** `ROSE Residence` workbook contract shaped the estimation rules, but it is not the operational fixture in this repository

Juniper Avenue is the proving ground for future promotion. ROSE Residence stays proof lineage only.

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
- `cwicr-cost-search`
- `boq-read`
- `boq-export`
- `phases-sync`

### Still blocking promotion

- `ifc-cost-enrichment`
- `boq-sync`
- `quantity-takeoff-agent`

### Useful later, but not the first gate

- `admin-sql`
- `admin-route`
- `cost-per-zone`
- `cost-overlay`
- `skills-search-api`

## Current state

Current state is **planning slice only**. The contract is now explicit in the repo, but the capability stays red until Juniper Avenue completes an end-to-end governed run.

## Green-state rule

This capability turns green only when:

- Juniper Avenue runs end to end through the governed estimation path
- dependent green capabilities are explicitly reused, not assumed
- blocked prerequisites are either promoted or surfaced as honest blockers
- evidence exists for the project-scoped run, BOQ linkage, and cost writeback path

Anything less is still amber or red.
