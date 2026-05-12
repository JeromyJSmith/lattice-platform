---
title: "Phase 1 Addendum — MARPA Research Trove Integration"
type: session
status: reference
historical_only: true
source: "Follow-up to §4 verification report after user pointed to canonical external research folder"
---

# Phase 1 Addendum — MARPA Research Trove Integration

Follow-up to the initial Phase 1 verification (`2026-05-12-phase-1-verification.md`).
User pointed to `/Volumes/PixelTable/VW_iTWIN_Bridge/Vectorworks_Bentley_iTwin_MARPA_Research_20260508/`
as the canonical source for the Phase A stubs. Commit `24c29b1` pulled 5 source files
into the repo's research/specs tree and rewrote the 4 stub files (`marpa-business-intelligence.md`,
`outreach-templates.md`, `itwin-pricing.md`, `vw-2026-toolchain.md`) with real extracted content.

## Commit

```
24c29b1 docs(meta-harness): import MARPA research trove + rewrite 4 Phase A stubs with verified content
```

## Diff stat

```
 meta/harness/docs/_INVENTORY.md                    |  21 +
 .../bentley-ecosystem-deep-dive-20260508.md        | 453 ++++++++++++
 meta/harness/docs/research/itwin-pricing.md        | 134 +++-
 .../docs/research/marpa-business-intelligence.md   |  87 ++-
 .../research/marpa-research-report-v1-20260508.md  | 485 +++++++++++++
 .../marpa-research-report-v2-20260508-verified.md  | 760 +++++++++++++++++++++
 meta/harness/docs/research/vw-2026-toolchain.md    |  86 ++-
 .../docs/specs/amended-research-proposal.md        |  92 +++
 .../docs/specs/itwin-visgl-slide-bullets.md        | 249 +++++++
 meta/harness/docs/specs/outreach-templates.md      | 246 ++++++-
 10 files changed, 2506 insertions(+), 107 deletions(-)
```

## CI

`docs-sync-check` ✅ green on `24c29b1` per push-event run `25708169603` (9s).

## Verified facts now in the repo

- iTwin Platform pricing tiers (Community free / Standard $199 / Premium $499 / Enterprise custom) verified against developer.bentley.com/pricing/
- iTwin Activate: $250K SAFE, $100M iTwin Ventures fund, $250K-$5M check range, 20-week themed cohorts, 5 cohorts completed since 2023
- Key contacts: James Kress (Director, Digital Acceleration, iTwin Ventures) + Clive Hackforth
- VW Landmark 2026: Plant Style Manager + Copy External Data + Maxon Plant + Sustainability Dashboard + One Click LCA + Esri ArcGIS
- IFC certification status: IFC2x3 CV2.0 + IFC4 RV1.2 certified (2019/2023); IFC4.3 in-software but not formally certified as of 2026-05
- Nemetschek dTwin gap (no vegetation / landscape semantics — LATTICE fills a gap inside VW's own parent ecosystem)
- US landscape design industry: $9.3B, ~47,000 businesses (IBISWorld); DT market in construction growing at 36.9% CAGR
- ASLA 2024 Digital Tech Survey: drones 66% / BIM 40% / AI 40% / DT not yet tracked = uncontested whitespace

## Branch state

```
current HEAD: 24c29b1112a6cd4a35a895a69aca0a1542505129
commits ahead of main: 15
```
