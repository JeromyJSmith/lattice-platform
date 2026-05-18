# Juniper promotion decision

**Decision:** promotable

## Match coverage
- IFC species matched after bridge: **17 of 17**.
- Confidence breakdown: **15 high**, **2 medium**, **0 low**.
- The governed bridge artifact is `ddc/estimation/kernel/plant-category-bridge.json`.

## Workbook backing status
- Before bridge: **1** IFC-backed line item and **175** budget-only line items overall; **1 of 16** PLANTING line items IFC-backed.
- After bridge: **13** IFC-backed line items and **163** budget-only line items overall; **13 of 16** PLANTING line items IFC-backed.
- PLANTING remains **partial**, not full, because `Delivery - Plants`, `Character Pine Install + Delivery`, and the section subtotal stay budget-only bookkeeping lines.

## Honest remaining gaps
- Thymus praecox ‘Minus’ stays honest: 528 IFC elements are converted to 16.5 flats with the documented 32-elements-per-flat rule in the bridge and workbook traceability.
- Pinus densiflora 'Globosa' remains a real 5 IFC vs 2 budget quantity mismatch on Character Pine by Marpa (6’ H), even though the category unit cost is now defensibly backed.
- The bounded verifier surface remains the governed Juniper proof seam; it does not convert this run into live project-addressable Pixeltable bridge rows.

## Verifier and scoring evidence
- `ddc/estimation/evaluation/juniper/schema-validation.json`
- `ddc/estimation/evaluation/juniper/quantity-takeoff-verifier.json`
- `ddc/estimation/evaluation/juniper/ddc-estimation-contract-verifier.json`
- `ddc/estimation/evaluation/juniper/ifc-cost-enrichment-verifier.json`
- `ddc/estimation/evaluation/juniper/score-after-bridge.json`

## Decision rationale
The single prior promotion blocker is resolved: the Juniper IFC takeoff no longer has unmatched species, and every mapped unit cost comes from the existing Juniper workbook or pricebook fixtures without rewriting the budget categories. The remaining Pinus quantity mismatch is real and explicitly documented, but it does not invalidate the governed category-cost backing, so this run is promotable.
