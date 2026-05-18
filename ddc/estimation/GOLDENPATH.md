# Juniper Governed Estimation Golden Path

This is the exact repo-local promotion path for turning `ddc-estimation-contract` green. The only operational target is `MARPA — 918 Juniper Avenue`.

## Inputs

- Juniper project scope and identifiers
- project-scoped IFC element rows for the Juniper surface
- CWICR seed data and Qdrant cost-search readiness
- BOQ read/export surfaces for the same project scope
- phase context for the same project scope
- explicit blocker state for `ifc-cost-enrichment` and `quantity-takeoff-agent`

## Dependency Reuse

The golden path must reuse these capabilities as dependencies:

1. `cwicr-seed`
2. `cwicr-qdrant-cost-search`
3. `ifc-cost-enrichment`
4. `boq-sync`
5. `boq-read`
6. `boq-export`
7. `phases-sync`
8. `quantity-takeoff-agent`

It must also confront these blocked prerequisites directly:

No implementation run may present estimation as standalone.

## Exact Execution Path

0. Capture the current foundation score with `bash scripts/score-ddc.sh --json`
1. Confirm the run target is Juniper, not ROSE
2. Confirm Juniper-scoped IFC rows exist for the intended estimating surface
3. Use `quantity-takeoff-agent` to extract governed Juniper quantities and collect the evidence contract for the run
4. Reuse `cwicr-seed` and `cwicr-qdrant-cost-search` to obtain bounded, verifier-backed unit-cost matches for those Juniper quantities
5. Route those matches through `ifc-cost-enrichment` so cost attribution is written back to owned Juniper-scoped rows
6. Route the enriched scope through `boq-sync` so ERP-linked BOQ state is created or refreshed for the same Juniper scope
7. Reuse `boq-read` and `boq-export` to prove the BOQ state can round-trip without dropping scope or linkage
8. Reuse `phases-sync` so schedule/phase context remains attached to the same estimating surface
9. Keep the capability green only while the full chain continues to complete with evidence for the same Juniper scope

## Loop Rule

The bounded improvement loop should select the next target by asking:

1. Which red or amber capability on this path is closest to becoming green?
2. Which one most directly unlocks the Vectorworks plugin MVP chain?
3. Does the change improve the DDC foundation score honestly?

The loop must not optimize documentation-only wins once the DDC docs substrate is
already saturated.

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

- If `ifc-cost-enrichment` stops writing back governed Juniper rows, record it as a blocking prerequisite and stop before green
- If `quantity-takeoff-agent` stops orchestrating the governed run, record it as a blocking prerequisite and stop before green
- Never replace a blocked prerequisite with a manual narrative, isolated worksheet, or ROSE-era artifact

## Required End State Before Green

The capability is green only when Juniper completes the entire governed path, every dependency and prerequisite has an honest status, and the evidence set proves that the same project scope survived search, enrichment, BOQ sync, BOQ round-trip, and phase sync.
