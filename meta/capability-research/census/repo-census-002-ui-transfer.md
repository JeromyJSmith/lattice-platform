# Repo Census 002 — DDC UI Transfer Into iTwin/TanStack Panels

Date: 2026-05-13
Status: second sweep, UI/component and parametric-edit focus

Repo Census 001 identified source repositories. Census 002 changes the search
question: what existing UI, component, data-model, and geometry-edit pieces can
make DDC-style estimating happen inside the iTwin/TanStack element panel?

## Target Interaction

The desired operator loop is:

```text
click or group an element in the viewer
-> show identity, geometry, material, quantity, and linked BOQ/cost data
-> edit a quantity, size, material, or variant in the panel
-> recompute price and derived geometry/quantity
-> preserve the calculation and verifier evidence
-> optionally write the accepted change back through LATTICE-controlled paths
```

DDC's web UI is not the target shell. Its useful parts are the modules,
components, formulas, tests, and API contracts that should be rehosted inside
LATTICE's iTwin/TanStack operator surface.

## Key Findings

### DDC Has The Missing UI Model

Live GitHub tree inspection of `datadrivenconstruction/OpenConstructionERP`
found these highly relevant frontend surfaces:

- `frontend/src/features/bim/AddToBOQModal.tsx`
- `frontend/src/features/bim/BIMLinkedBOQPanel.tsx`
- `frontend/src/features/bim/BIMQuantityRulesPage.tsx`
- `frontend/src/features/bim/BIMRightPanelTabs.tsx`
- `frontend/src/features/bim/BIMToolsPanel.tsx`
- `frontend/src/features/boq/BOQGrid.tsx`
- `frontend/src/features/boq/BOQSummaryPanel.tsx`
- `frontend/src/features/boq/CostBreakdownPanel.tsx`
- `frontend/src/features/boq/PriceReviewPanel.tsx`
- `frontend/src/features/boq/grid/BIMQuantityPicker.tsx`
- `frontend/src/features/boq/grid/formula/engine.ts`
- `frontend/src/features/boq/suggestQuantityFromBIM.ts`
- `frontend/src/features/costs/CwicrMatchPanel.tsx`
- `frontend/src/features/costs/MultiVariantPicker.tsx`
- `frontend/src/features/takeoff/components/MeasurementLedger.tsx`
- `frontend/src/features/takeoff/lib/takeoff-ledger.ts`
- `frontend/src/features/match-elements/MatchDetailPanel.tsx`

The frontend dependency shape is compatible with the LATTICE operator surface:
React, Vite, TanStack React Query, Three.js, AG Grid, Recharts, MapLibre,
Excel/PDF export libraries, Playwright, and Vitest. The license surface remains
important: OpenConstructionERP reports AGPL-3.0 in repository metadata, so treat
this as an adapter/service boundary and pattern source unless legal review
approves direct reuse.

### iTwin Has The Panel And Selection Model

The iTwin-side pieces that matter most for transferring DDC UI into an
element-click workflow:

- `iTwin/presentation`: unified selection, hierarchy, and content models.
- `iTwin/appui`: widget registration, toolbar, layout, and panel provider
  patterns.
- `iTwin/viewer-components-react`: property-grid, quantity-formatting,
  tree-widget, reporting-related widgets, and EC3/LCA widget surfaces.
- `iTwin/iTwinUI`: controls and design tokens for native-feeling panels.

These should shape how LATTICE hosts DDC-derived panels, but they do not remove
the proof gate. Every UI transfer becomes a bounded fixture first.

### IFC Viewer And Interaction References

`ThatOpen/web-ifc-viewer` remains a useful interaction reference even if LATTICE
uses a different primary viewer shell. Live tree inspection showed:

- IFC selection and selector components
- IFC properties utilities
- units utilities
- dimensions and measurement components
- clipping/sectioning components
- DXF, glTF, PDF import/export helpers

This is useful for deterministic selection/properties/measurement fixtures and
for comparing viewer interaction patterns.

### Parametric Geometry Edit Candidates

Changing a panel value should eventually change both price and geometry. That
requires a controlled parametric edit loop:

```text
editable parameter -> derived quantity -> derived price -> geometry update
```

Candidate references:

- `CadQuery/cadquery`: Python parametric CAD framework over OCCT. Strong local
  fixture candidate for deterministic geometry/quantity changes.
- `FreeCAD/FreeCAD`: broad LGPL parametric CAD modeler. Valuable reference, but
  too large for the first proof path.
- `CadQuery/CQ-editor`, `bernhard-42/jupyter-cadquery`, and
  `bernhard-42/vscode-ocp-cad-viewer`: useful UI/viewer patterns around
  parametric scripts.
- `Jelatine/JellyCAD`: MIT programmable CAD candidate, lower priority.

For LATTICE, the first proof should not try to replace Vectorworks geometry.
Use a tiny parametric fixture to prove the calculation contract, then later map
accepted geometry changes back through Pixeltable and the Vectorworks plugin.

## Registry

The contract-only registry for this sweep is:

```text
analysis/capabilities/repo-census-002-ui-transfer-capability-registry.yaml
```

## Recommended First Proofs

1. DDC UI manifest proof: parse OpenConstructionERP frontend tree and assert the
   expected BIM, BOQ, cost, takeoff, and match-elements components exist.
2. DDC formula proof: run or port a tiny fixture equivalent of the BOQ formula
   engine over three line items and assert stable totals.
3. Selected-element panel proof: mock one selected element and render identity,
   quantity, cost, source, and evidence fields in a LATTICE panel contract.
4. Parametric edit proof: edit one numeric dimension in a fixture, recompute
   quantity and price, and write a deterministic evidence artifact.

## Not Now

- Do not copy AGPL OpenConstructionERP frontend code into LATTICE without legal
  review.
- Do not replace the LATTICE/TanStack operator shell with DDC's frontend.
- Do not run live DDC services for this proof.
- Do not attempt Vectorworks write-back until the parameter -> quantity -> price
  proof is deterministic and evidence-backed.
- Do not install FreeCAD or CadQuery as part of the census.

