# DDC Governed Planning Surface — LATTICE Control Goal

DDC in LATTICE is healthy only when the repo can promote governed planning capabilities without pretending partial coverage is complete. That still includes the broader DDC estate — skill mapping, CWICR cost search, BOQ adapter surfaces, and CI enforcement — but estimation promotion is now a first-class part of DDC health instead of a side note.

## Fitness Function

Score DDC health against **governed estimation promotion**, **dependency readiness**, **DDC surface integrity**, and **evidence honesty**.

The primary numeric loop is now the Juniper plugin-foundation scorer at
`scripts/score-ddc.sh`. It is not a docs-presence score anymore. It measures
the actual capability path that must turn green for a Vectorworks cost
estimation plugin MVP:

- `cwicr-seed`
- `cwicr-qdrant-cost-search`
- `ifc-cost-enrichment`
- `boq-sync`
- `boq-read`
- `boq-export`
- `phases-sync`
- `quantity-takeoff-agent`
- `ddc-estimation-contract`

Green contributes full weight, amber contributes partial weight, and red
contributes zero. The loop should improve this score by turning capability
states green, not by adding more DDC references to docs.

Score DDC health against these conditions:

1. **Governed estimation promotion**: `ddc-estimation-contract` has an explicit goal surface and golden path, and the operational target is `MARPA — 918 Juniper Avenue`
2. **Dependency-chain truthfulness**: dependent helpers already in play (`cwicr-seed`, `cwicr-qdrant-cost-search`, `boq-sync`, `boq-read`, `boq-export`, `phases-sync`) are named as reused dependencies, while blocking prerequisites (`ifc-cost-enrichment`, `quantity-takeoff-agent`) stay explicit until promoted
3. **DDC surface integrity**: DDC mapping, CWICR cost search, ERP adapter, and repo-local docs stay aligned with the governed estimation contract instead of drifting into isolated worksheet language
4. **Evidence-backed green state**: DDC cannot claim estimation green unless Juniper completes the governed promotion path with evidence for dependency reuse, cost writeback, BOQ linkage, and blocker handling
5. **No fake green**: ROSE Residence may justify lineage and rules, but it never counts as the operational target and never upgrades Juniper readiness by analogy

## Estimation Objective

The immediate DDC objective is to make governed estimation promotion a measurable repo-local target:

- **Operational target:** `MARPA — 918 Juniper Avenue`
- **Lineage only:** `ROSE Residence`
- **Mode:** dependency-governed, never standalone
- **Promotion rule:** estimation stays red or blocked until Juniper advances through the full dependency chain with real evidence

## Green-State Rule

DDC turns green for estimation only when all of the following are true:

1. Juniper is the project used for the governed estimation run
2. the helper capabilities already marked as available are actually reused in the run
3. blocked prerequisites are either promoted or recorded as honest blockers that stop the run from turning green
4. evidence exists for cost-search reuse, enrichment/writeback, BOQ state linkage, export/read round-trip, and phase context
5. the estimation goal and golden path remain current and do not regress to worksheet-only framing

If any link in that chain is missing, DDC health for estimation remains non-green.

## Improvement Loop

1. Re-read `ddc/GOAL.md`, `ddc/estimation/GOAL.md`, and `ddc/estimation/GOLDENPATH.md`
2. Verify the operational target is still Juniper and ROSE is still lineage only
3. Run `bash scripts/score-ddc.sh --json` and rank the remaining red and amber capabilities by plugin value-path impact
4. Check that dependency helpers and blocked prerequisites match current reality
5. Refuse to mark green on the strength of a partial demo, isolated export, or worksheet-shaped artifact
6. Update the goal surfaces before implementation runs when the dependency chain or proof requirements change

## Action Catalog

- **Goal surface review**: keep `ddc/GOAL.md` aligned with estimation promotion as a first-class DDC health signal
- **Capability contract**: keep `ddc/estimation/GOAL.md` explicit about green, blocked, evidence, and no-fake-green rules
- **Execution path**: keep `ddc/estimation/GOLDENPATH.md` aligned to the exact Juniper promotion sequence
- **Foundation score**: `bash scripts/score-ddc.sh --json`
- **Docs sync**: `bash scripts/pre-commit-docs-check.sh`
- **Diff hygiene**: `git --no-pager diff --check`

## Operating Mode

- Treat DDC as a governed planning surface, not a loose collection of demos
- Use Juniper as the operational estimation target for promotion work
- Keep ROSE confined to proof lineage and vocabulary inheritance
- Optimize the loop for capability-state promotion, not documentation saturation
- Reuse available dependencies explicitly and stop on blocked prerequisites instead of narrating around them
- Refuse any green-state claim that is not supported by a full Juniper evidence trail
