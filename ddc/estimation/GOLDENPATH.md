# Juniper Governed Estimation Golden Path

This is the exact repo-local promotion path for turning `ddc-estimation-contract` green. The only operational target is `MARPA — 918 Juniper Avenue`.

## Inputs

- Juniper project scope and identifiers
- project-scoped IFC element rows for the Juniper surface
- CWICR seed data and Qdrant cost-search readiness
- BOQ read/export surfaces for the same project scope
- phase context for the same project scope
- explicit blocker state for `ifc-cost-enrichment`, `boq-sync`, and `quantity-takeoff-agent`

## Dependency Reuse

The golden path must reuse these capabilities as dependencies:

1. `cwicr-seed`
2. `cwicr-qdrant-cost-search`
3. `boq-read`
4. `boq-export`
5. `phases-sync`

It must also confront these blocked prerequisites directly:

1. `ifc-cost-enrichment`
2. `boq-sync`
3. `quantity-takeoff-agent`

No implementation run may present estimation as standalone.

## Exact Execution Path

1. Confirm the run target is Juniper, not ROSE
2. Confirm Juniper-scoped IFC rows exist for the intended estimating surface
3. Reuse `cwicr-seed` and `cwicr-qdrant-cost-search` to obtain bounded, verifier-backed unit-cost matches for Juniper quantities
4. Route those matches through `ifc-cost-enrichment` so cost attribution is written back to owned Juniper-scoped rows
5. Route the enriched scope through `boq-sync` so ERP-linked BOQ state is created or refreshed for the same Juniper scope
6. Reuse `boq-read` and `boq-export` to prove the BOQ state can round-trip without dropping scope or linkage
7. Reuse `phases-sync` so schedule/phase context remains attached to the same estimating surface
8. Use `quantity-takeoff-agent` to orchestrate quantities, evidence collection, and blocker capture across the whole run
9. Turn green only after the full chain completes with evidence for the same Juniper scope

## Validation Gates

The run fails the golden path unless every gate passes:

1. **Target gate**: all evidence references Juniper as the operational project
2. **Dependency gate**: helper capabilities are visibly reused, not implied
3. **Enrichment gate**: cost matches are written back to governed Juniper-scoped rows
4. **BOQ gate**: ERP-linked BOQ state is created or refreshed for the same scope
5. **Round-trip gate**: BOQ read/export returns the same governed scope coherently
6. **Phase gate**: phase context survives on the same estimating surface
7. **Orchestration gate**: quantity takeoff captures evidence and blockers instead of skipping gaps

## Evidence Requirements

Green requires durable evidence for all of the following:

- Juniper project identity and scope
- reused dependency chain
- CWICR cost-match results tied to Juniper quantities
- enrichment/writeback on governed rows
- BOQ linkage and round-trip output
- preserved phase context
- blocker disposition for every blocked prerequisite

Absent evidence is a failed gate, not a warning.

## Blocker Capture Rules

- If `ifc-cost-enrichment` is unavailable or incomplete, record it as a blocking prerequisite and stop before green
- If `boq-sync` cannot establish ERP-linked state, record it as a blocking prerequisite and stop before green
- If `quantity-takeoff-agent` cannot orchestrate the governed run, record it as a blocking prerequisite and stop before green
- Never replace a blocked prerequisite with a manual narrative, isolated worksheet, or ROSE-era artifact

## Required End State Before Green

The capability is green only when Juniper completes the entire governed path, every dependency and prerequisite has an honest status, and the evidence set proves that the same project scope survived search, enrichment, BOQ sync, BOQ round-trip, and phase sync.
