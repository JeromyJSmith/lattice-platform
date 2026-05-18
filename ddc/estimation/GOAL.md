# Governed Estimation Goal — DDC Planning Capability

## Capability Mission

Promote `ddc-estimation-contract` from planning-only to governed operational readiness by proving that `MARPA — 918 Juniper Avenue` can move through the real dependency chain for cost estimation without fake-green shortcuts.

## Fitness Function

The capability is healthy only when all of these remain true:

1. **Operational target is explicit**: Juniper Avenue is the run target for promotion
2. **Lineage is explicit**: ROSE Residence is proof lineage only and never substitutes for Juniper execution
3. **Dependency governance is explicit**: estimation is framed as a dependent capability, not an isolated worksheet or standalone app
4. **Reuse is explicit**: `cwicr-seed`, `cwicr-qdrant-cost-search`, `ifc-cost-enrichment`, `boq-sync`, `boq-read`, `boq-export`, `phases-sync`, and `quantity-takeoff-agent` are reused as dependencies, not re-described as independent wins
5. **Blockers are explicit**: if any promoted dependency regresses, the contract falls out of green immediately instead of narrating around the break
6. **Evidence is explicit**: green requires recorded proof for dependency reuse, Juniper-scoped cost matching, writeback/enrichment, BOQ linkage, and blocker handling
7. **Dual-contract traceability is explicit**: workbook-faithful evidence rows and estimate capability entities stay linked through workbook row refs, formula refs, and source artifact refs

The operational scorer for this capability is the DDC foundation-path score in
`scripts/score-ddc.sh --json`. That score is only useful if it reflects real
state changes in this chain:

- continued green for `ifc-cost-enrichment`
- continued green for `boq-sync`
- continued green for `quantity-takeoff-agent`
- and continued green for the already promoted helper capabilities

## What Counts as Green

Green means:

1. Juniper runs through the governed estimation path end to end
2. dependency reuse is visible and attributable
3. enrichment/writeback and BOQ linkage are evidenced for the same project scope
4. phase context stays attached to the same estimating surface
5. no blocking prerequisite is hand-waved, skipped, or silently substituted

The capability score should rise because one of the blocking or partial links
actually moved forward, not because the repo gained more descriptive text.

## What Counts as Blocked

Blocked means any of the following is true:

- `ifc-cost-enrichment` is not promotable for Juniper-scoped rows
- `quantity-takeoff-agent` cannot orchestrate quantities, evidence, and blocker capture
- any dependency helper is assumed rather than demonstrated
- the run produces exports or search hits without governed writeback and linkage

## Proof Lineage vs Operational Target

- **Operational target:** `MARPA — 918 Juniper Avenue`
- **Pilot proof lineage only:** `ROSE Residence`

ROSE can justify the shape of the contract, validation rules, and vocabulary. It cannot satisfy the operational proof requirement for green.

## Required Dependency Chain

### Reused helpers already helping

- `cwicr-seed`
- `cwicr-qdrant-cost-search`
- `ifc-cost-enrichment`
- `boq-sync`
- `boq-read`
- `boq-export`
- `phases-sync`
- `quantity-takeoff-agent`

### Blocking prerequisites

Green requires the full chain to be either reusable now or honestly blocking. There is no middle state that counts as operational success.

## No-Fake-Green Rule

Do not turn this capability green because of:

- a successful ROSE artifact
- a standalone worksheet or workbook exercise
- a single cost lookup
- a BOQ export with no governed writeback
- a narrative claim that dependencies "would" connect later

If the Juniper run cannot clear the dependency-governed path with evidence, the capability stays red or blocked.
