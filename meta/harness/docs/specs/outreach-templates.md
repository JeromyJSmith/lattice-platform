---
title: "Outreach Templates — Phase A Stub"
type: spec
status: draft
historical_only: false
source: "Stub created in Phase 1 Amendment §3.2; awaiting user-sourced templates"
---
# Outreach Templates

**Status:** draft stub. Phase A artifact. Will be populated with the user's content.

## Purpose

Standardize the outbound messaging the MARPA team uses for the four primary audiences. Templates here are reference scaffolding — the human owns the actual sends; the harness uses these as canonical voice / framing references when proposing copy.

## Templates to author

### 1. Bentley Partner Program inquiry
- [ ] Subject line conventions (issue-tracker-ready)
- [ ] Standard opening — who MARPA is, what LATTICE is
- [ ] iTwin OSS positioning (open-source self-hosted only; no Bentley cloud dependency)
- [ ] Specific asks: which iTwin OSS repos we're consuming (Tier 1 from `meta/ITWIN_MAPPING.md`)
- [ ] Cesium acquisition context — what we're building on top of (deck.gl Tile3DLayer + TerrainExtension)
- [ ] Sign-off + contact block

### 2. Vectorworks Partner Program inquiry
- [ ] VW 2026 SDK status (VS2022 v17.12, Xcode 16.2, satellite credentials)
- [ ] vwx-mcp + custom C++ plugin architecture
- [ ] Plant Style Manager as the canonical control surface
- [ ] What we need from VW: SDK clarifications, satellite-credentials workflow doc

### 3. Municipal parks-department pilot inquiry
- [ ] CityGML 3.0 Vegetation ADE forward-compatibility story
- [ ] Sofia / Tallinn / OneTree as prior-art references
- [ ] Pilot project scope template (one project, one season, one report)
- [ ] Data ownership + handoff terms

### 4. Landscape-architecture firm partnership inquiry
- [ ] AECOM BioInstinct positioning (what they don't do)
- [ ] Pilot scope template (one client project per quarter)
- [ ] IP ownership clarity (LATTICE is platform; client owns their data)

## Voice and tone constraints

- Direct, technical, no marketing fluff
- Never positions iTwin as deprecated or replaced — iTwin is active OSS infrastructure
- Never positions deck.gl as a 3D scene renderer — analytical layer only
- Always names the open-source ground (vis.gl, Three.js, ThatOpen, Pixeltable, Cesium 3D Tiles standard)

## Cross-references

- `meta/harness/docs/research/marpa-business-intelligence.md` — strategy that drives the messaging
- `meta/harness/docs/research/itwin-pricing.md` — pricing-side framing for partner conversations
- `meta/ITWIN_MAPPING.md` — canonical iTwin Tier 1/2/3/4 split (what we use vs. what we don't)
