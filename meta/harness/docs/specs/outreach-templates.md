---
title: "Outreach Templates — Partner & Pilot Conversations"
type: spec
status: reference
historical_only: false
source: "Synthesized from bentley-ecosystem-deep-dive-20260508.md, marpa-research-report-v2-20260508-verified.md (meta/harness/docs/research/)"
---
# Outreach Templates

> **Gated context note.** This file references content under `meta/harness/docs/research/_gated/bentley-commercial/`. That content is dormant under default doctrine (OSS self-hosted only). Use the references here only for drafting Bentley-facing outreach; **do NOT propagate commercial assumptions into platform documents or PRDs**. See `meta/harness/docs/research/_gated/README.md` for the five-gate dormancy policy and activation procedure.

Canonical voice + framing for the four primary outbound audiences. The human owns every send — the harness uses these as canonical references when proposing copy.

## Voice and tone constraints (binding for every send)

- Direct, technical, no marketing fluff.
- Never positions iTwin as deprecated, replaced, or competitive — iTwin is **active OSS infrastructure** that LATTICE builds on top of. (Cardinal rule.)
- Never positions deck.gl as a 3D scene renderer — analytical layer only. ThatOpen owns 3D scene. Both work together; do not pit them.
- Always names the open-source ground: vis.gl, Three.js, ThatOpen, Pixeltable, Cesium 3D Tiles standard (OGC community standard, not proprietary).
- Position MARPA's value as **gap-filling, not competitive**. Use this phrase pattern: "fills a gap in [X]'s platform by bringing [Y use case] into the ecosystem for the first time."

## 1. Bentley iTwin Partner Program — initial inquiry

**Pre-flight:** Standard tier is the appropriate entry. The application form lives at `bentley.com/software/itwin-partner-program/`. Free; no waitlist; year-round acceptance. Application collects org info + use case + integration intent. Identify as **iTwin integration partner**, NOT as a Channel Partner candidate.

**Body skeleton:**

```
Subject: iTwin Partner Program application — landscape BIM bridge (Vectorworks Landmark → iTwin)

Hello Bentley iTwin Partner team,

I'm Jeromy Smith, applying to the iTwin Partner Program on behalf of MARPA
Landscape Architecture. We are building a landscape-native operational layer
on top of iTwin for the landscape architecture vertical.

Use case (Envision-phase framing):
  Vectorworks Landmark is the industry-standard landscape BIM authoring tool.
  Its IFC4.3 export uses IfcGeographicElement VEGETATION as a coordinate stub
  — none of the species taxonomy, canopy spread, lifecycle, or maintenance
  schedule survives the export. iTwin's Engage AI treats vegetation as 3D
  decoration, not as living asset data.

  MARPA fills this gap by building a normalization layer between
  Vectorworks Landmark and iTwin: sidecar JSON enrichment of the IFC export
  with rich landscape semantics (species, canopy, ecological function,
  irrigation zones, maintenance schedules), forward-compatible with the
  emerging CityGML 3.0 Vegetation ADE standard.

  We are also building a complementary visualization layer on the public
  iTwin APIs using ThatOpen + deck.gl + Cesium 3D Tiles, so landscape
  architects can review their twin in any browser without a desktop install.

What we're using from the iTwin ecosystem:
  - @itwin/core-geometry, @itwin/core-common, @itwin/core-quantity (MIT)
  - BIS schema vocabulary
  - iTwin Synchronization API (IFC2x3 / IFC4 / IFC4.3 connectors)
  - Cesium ion + 3D Tiles (post-acquisition platform alignment)
  - Future: Sensor Data API for irrigation IoT, Changed Elements API for
    audit, Issues + Forms APIs for punch list

What we are NOT doing:
  - No @itwin/core-backend / SnapshotDb / BriefcaseDb usage
  - No Channel Partner reseller relationship — this is an ISV / digital
    integrator track per the Partner Program documentation

Pilot context:
  We have a Boulder, CO landscape architecture firm with an active
  Vectorworks Landmark workflow and a civic/campus project whose
  institutional owner would value a landscape digital twin deliverable.
  The pilot is the proof-of-concept; we absorb all software cost in Phase 1.

Next step we'd value:
  An Envision-phase conversation to validate the integration fit and discuss
  which Synchronization API connectors best serve the IFC normalization path.

Best,
Jeromy Smith
[contact block]
```

**Action target after Envision:** secure access to the Design phase (the most technically valuable part of the Partner Program) before beginning serious development.

## 2. iTwin Activate cohort — application framing (when 2026 cohort opens)

**Pre-flight:** Activate is the corporate VC accelerator — $250K SAFE note entry; $100M iTwin Ventures fund with $250K–$5M check range; 20-week themed cohorts. Five cohorts run since 2023; **every Cohort 1/4/5 participant was an integration play** converting external-domain data into iTwin-consumable operational assets. MARPA is a textbook structural fit. Apply the moment the 2026 cohort theme is announced. Key contact: **James Kress, Director of Digital Acceleration, iTwin Ventures**.

**Body skeleton:**

```
Subject: iTwin Activate 2026 application — MARPA Vectorworks-to-iTwin landscape bridge

Dear James, Clive, and the iTwin Activate team,

Following on from our Partner Program enrollment [reference internal
relationship], we are applying to iTwin Activate 2026 with the MARPA
Vectorworks Landmark → iTwin landscape architecture bridge.

Why MARPA fits the Activate selection pattern:
  Every confirmed Cohort 1, 4, and 5 participant was an integration play
  converting data from an external domain — LiDAR, drone imagery, railway
  sensor data, urban 3D mapping — into iTwin-consumable operational assets.
  MARPA does the same for landscape architecture: VW Landmark's industry-
  leading authoring data, normalized into iTwin's operational layer.

What we fill (Cohort-5 alignment language):
  "Filling a gap in Bentley's platform by bringing a $9.3B industry segment
  — US landscape architecture — into the iTwin ecosystem for the first time."

Eliminated risk vs. typical Activate applicant:
  MARPA is itself the named pilot customer. The "find a customer" risk that
  challenges most accelerator applicants does not apply here. Our Boulder
  pilot uses the firm's active VW Landmark workflow on a real civic/campus
  project with an institutional owner who values the digital twin deliverable.

Stack we're building on (all public iTwin APIs + OSS):
  - iTwin Synchronization API (IFC connectors)
  - Cesium ion 3D Tiles (post-acquisition alignment)
  - Sensor Data API (irrigation IoT)
  - Mesh Export API (Cesium 3D Tiles pipeline)
  - Open-source frontend: ThatOpen + deck.gl + Three.js / R3F

Outputs from a successful cohort:
  - Production-grade Vectorworks → IFC + sidecar JSON ingestion path
  - Live landscape digital twin deployed for the Boulder pilot project
  - CityGML 3.0 Vegetation ADE-compatible export — positioning MARPA as
    early implementer of an emerging municipal-handoff standard
  - A case study Bentley can promote at Year in Infrastructure 2026

Looking forward to the Design phase conversations.

Best,
Jeromy Smith
[contact block]
```

## 3. Municipal parks-department pilot inquiry

**Pre-flight:** Lead with the CityGML 3.0 Vegetation ADE forward-compatibility story. Sofia (Bulgaria) and Tallinn (Estonia) are prior-art municipal pilots — both planned implementations of the same ADE conceptual model MARPA targets. OneTree is the citizen-science platform variant. No US municipality has yet implemented landscape DT at the parks-department level — first-mover whitespace.

**Body skeleton:**

```
Subject: Landscape digital twin pilot — CityGML 3.0 Vegetation ADE forward-compatible

Hello [parks dept lead],

I lead MARPA's landscape technology initiative. We're seeking one
municipal parks-department pilot for the 2026/2027 season — one civic or
campus project, one growing season, one report deliverable.

The pilot uses the emerging CityGML 3.0 Vegetation ADE conceptual model
(ISPRS 2024 paper, Petrova-Antonova et al.) — the same model Sofia
(Bulgaria), Tallinn (Estonia), and the OneTree citizen-science platform
are implementing. Designing for the ADE today means your data layer is
forward-compatible with the emerging municipal GIS-exchange standard
before any US city has implemented it.

Concrete deliverable for the pilot:
  - One project's planting plan + irrigation zones + maintenance schedule
    expressed as a live operational digital twin (browser-accessible, no
    install)
  - Per-tree health-status tracking with soil-moisture / weather telemetry
    binding (where sensors are present)
  - CityGML handoff package generated directly from the sidecar data —
    suitable for ingestion by any city GIS system implementing the ADE
  - One-season ecological report: canopy cover, impervious-surface ratio,
    species richness, biomass density, stormwater runoff coefficient

Data ownership: the parks department owns 100% of the project data. MARPA
provides the platform; we never claim ownership of the city's vegetation
records.

Cost: zero in Phase 1 (proof-of-concept partnership). Phase 2+ licensing
discussed at season-end review.

Happy to demo the prototype on a screenshare.

Best,
Jeromy Smith
[contact block]
```

## 4. Landscape-architecture firm partnership inquiry

**Pre-flight:** AECOM `BioInstinct` is a measurement tool (remote sensing + AI on existing canopy); it is NOT a competing platform. Sasaki / SWA / EDAW have no published landscape DT capability. Position MARPA as the platform partner for firms that want the DT capability without the build cost.

**Body skeleton:**

```
Subject: Landscape digital twin partnership — one client project per quarter

Hello [firm partner],

MARPA is building a landscape-native operational layer on top of Bentley
iTwin — the digital twin platform you don't have to build yourself.

What this is:
  - Vectorworks Landmark stays your authoring environment (no workflow change)
  - LATTICE / MARPA normalizes the IFC export with rich landscape semantics
    (species, canopy, lifecycle, ecological metrics)
  - The client gets a browser-accessible operational twin — no install,
    no Bentley desktop license requirement
  - You get a deliverable Sasaki, SWA, and EDAW are not currently offering

What this is NOT:
  - Not a replacement for your VW Landmark workflow
  - Not Bentley iModelHub or Bentley cloud — open-source self-hosted stack
  - Not AECOM BioInstinct — that's measurement, this is operational

Partnership shape:
  - One client project per quarter for the first year
  - IP ownership clarity: MARPA is the platform; your client owns their
    data; you retain client relationship
  - Pricing model TBD at end of Q1 pilot (see `meta/harness/docs/research/_gated/bentley-commercial/itwin-pricing.md` — gated; outreach use only)

Looking for one civic / campus / institutional project from your current
backlog where the owner would value a landscape DT deliverable.

Best,
Jeromy Smith
[contact block]
```

## Cross-references

- `meta/harness/docs/research/marpa-business-intelligence.md` — strategic frame driving every send above
- `meta/harness/docs/research/bentley-ecosystem-deep-dive-20260508.md` — full Partner Program + Activate detail (cite when prepping for a Design-phase or Sprint-phase conversation)
- `meta/harness/docs/research/_gated/bentley-commercial/itwin-pricing.md` — pricing-side framing for partner / pilot conversations (gated commercial content; this outreach file is the **one permitted use** of direct pointing into `_gated/` — do NOT propagate commercial assumptions into platform docs or PRDs)
- `meta/harness/docs/research/_gated/bentley-commercial/activate-program.md` — iTwin Activate SAFE / cohort / Ventures pipeline (gated; outreach use only)
- `meta/harness/docs/research/_gated/bentley-commercial/partner-program.md` — Partner Program tier specifics + engagement phases (gated; outreach use only)
- `meta/harness/docs/research/_gated/README.md` — dormancy policy + five-gate activation procedure
- `meta/ITWIN_MAPPING.md` — canonical iTwin Tier 1/2/3/4 split (what we use vs. what we don't); cite when the conversation drifts to which Bentley products we are or are not adopting
