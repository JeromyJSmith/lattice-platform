---
title: "MARPA Business Intelligence — Strategic Synthesis"
type: research
status: reference
historical_only: false
source: "Synthesized from marpa-research-report-v2-20260508-verified.md, marpa-research-report-v1-20260508.md, bentley-ecosystem-deep-dive-20260508.md (all in meta/harness/docs/research/)"
---
# MARPA Business Intelligence

Compact synthesis of the verified May-2026 research trove. Source documents in the same folder carry the full citation chains; this file is the executive-summary layer.

## The strategic frame

LATTICE + MARPA pilot is positioned as a **landscape-native operational layer on top of the iTwin platform**. Three structural facts make the opportunity defensible:

1. **iTwin has no landscape-native semantics.** Bentley's `IfcGeographicElement VEGETATION` ingestion is a coordinate stub — no species taxonomy, canopy spread, lifecycle, ecological metrics, or maintenance schedule. iTwin's `Engage Copilot` treats vegetation as 3D *decoration*, not as living asset data. (See `marpa-research-report-v2-20260508-verified.md` Platform Capability Matrix.)
2. **Vectorworks Landmark has industry-leading landscape BIM authoring.** Plant Style Manager (VW 2026) with batch editing, live nursery pricing pull, rebuilt Existing Tree tool with 8-directional canopy from Maxon Plant, real-time Sustainability Dashboard (Embodied Carbon / Urban Greening Factor / Biomass Density / Biodiversity Net Gain). No competitor matches this authoring depth for landscape practice.
3. **No competitor fills the gap.** AECOM `BioInstinct` is a measurement / valuation tool (remote sensing + AI on existing canopy), not a digital-twin platform. Arup has a conceptual framework but no shipped landscape DT product. No peer-reviewed landscape DT case study has been published by a top-tier landscape architecture firm. The whitespace is real and currently uncontested.

The strategic insight: **MARPA does not author landscape data; it normalizes Vectorworks output into iTwin's operational layer.** The sidecar JSON schema + CityGML 3.0 Vegetation ADE-compatible normalization is the durable product moat — it is the one layer that neither Bentley, nor Vectorworks, nor any current competitor is building.

## Competitive landscape

| Player | What they do | Gap vs. LATTICE/MARPA |
|---|---|---|
| Vectorworks Landmark | Industry-leading landscape BIM authoring; design-phase only | No digital twin / operational layer; IFC export loses landscape semantic richness |
| Bentley iTwin (core platform) | Full lifecycle infrastructure DT — design / construction / ops / maintenance | No landscape semantic ingestion; vegetation treated as visual decoration |
| Bentley OpenSite+ AI | Civil site engineering (residential / commercial / industrial) — early access, no public API | No landscape architecture or ecological use cases; not callable programmatically |
| Nemetschek dTwin | Built-asset / facility twin (post-VW acquisition platform play) | Not landscape-specific; no landscape semantic schema |
| AECOM BioInstinct | Remote-sensing + AI measurement of existing vegetation | Measurement tool, not a platform; not an authoring/ops bridge |
| Arup Digital Twin (conceptual) | Published framework; no shipped landscape product | Conceptual only; no operational case studies |
| Top-tier landscape firms (Sasaki, SWA, EDAW/AECOM-Landscape) | No published landscape DT capability | The whitespace MARPA exploits |

## Target client segments (priority order)

1. **Boulder, CO pilot (the MARPA pilot itself)** — single landscape architecture firm with active VW Landmark workflow + civic/campus project with institutional owner who values a digital-twin deliverable. Cost in Phase 1: zero software cost to firm; LATTICE absorbs the integration build. Source: `marpa-research-report-v1-20260508.md` § "Initiate the Boulder pilot conversation".
2. **Municipal parks departments** — CityGML 3.0 Vegetation ADE forward-compatibility story (Sofia / Tallinn / OneTree prior art). When a city requests a CityGML handoff, MARPA generates it from sidecar data directly.
3. **Campus institutions** — universities, hospitals, transit agencies — Bentley's existing iTwin account managers serve these; Partner Program turns those relationships into indirect distribution channels.
4. **Landscape-architecture firm partnerships** — one client project per quarter; IP ownership clarity (LATTICE = platform; client owns their data).

## Adoption signals (verified)

- **ASLA 2024 Digital Technology Survey** (370+ respondents): drones at 66% adoption, BIM at ~40%, AI at ~40%, mobile/VR < 5%. Digital twins NOT yet tracked as a category — meaning **no incumbent platform** has captured landscape DT mindshare. First credible entry captures greenfield adoption.
- **ASLA framing** of the profession as "conservative end of AECO" with "greater room for innovation and nimbleness" — first-mover advantage is real and currently uncontested.
- **CityGML 3.0 Vegetation ADE** is at conceptual stage (ISPRS 2024 paper, Petrova-Antonova et al.). No published XSD as of 2026-05. Sofia / Tallinn / OneTree are the first planned implementations. MARPA designing the sidecar schema to mirror the ADE positions us as an **early implementer of an emerging standard** — significant credentialing advantage for municipal handoff conversations.

## Strategic sequence (from `bentley-ecosystem-deep-dive-20260508.md`)

1. **Secure MARPA principal authorization** — required before any external partnership conversation.
2. **Apply to Bentley iTwin Partner Program immediately** (this week, not next quarter). Free, year-round, no waitlist. Standard tier is the appropriate entry. Application form: bentley.com/software/itwin-partner-program/.
3. **Begin GitHub engagement in parallel** — github.com/iTwin organization. Active issues, pull requests, public roadmap discussions — creates an evidence trail of sustained commitment.
4. **Warm outreach to James Kress** (Director, Digital Acceleration, iTwin Ventures) and **Clive Hackforth** before the 2026 iTwin Activate cohort window opens. See `outreach-templates.md`.
5. **Position for iTwin Activate application** the moment the 2026 cohort is announced. The MARPA-bridge pattern is a **textbook fit** for Activate's selection criteria (every Cohort 1/4/5 participant was an integration play converting external data into iTwin-consumable operational assets).
6. **Boulder pilot in parallel** — convert one VW Landmark project into a live MARPA digital twin deliverable. Acts as the "named pilot customer" that eliminates the typical accelerator-applicant risk.

## Revenue / monetization model (working hypothesis)

- **Phase 1 (pilot, no revenue):** LATTICE absorbs build cost. Pilot is the proof-of-concept that opens the Bentley Activate door and the municipal-handoff conversation.
- **Phase 2 (Activate cohort, ~$250K SAFE note via iTwin Ventures):** non-dilutive (or favorably-dilutive) entry capital. See `itwin-pricing.md`.
- **Phase 3 (follow-on iTwin Ventures or independent commercial):** iTwin Ventures is a $100M fund with $250K-to-$5M check range. Activate is the first filter into the larger pipeline.
- **Long-term revenue:** per-MARPA-project licensing + per-project sidecar/normalization services + ecological reporting subscriptions (Sustainability Dashboard export). Client pays for LATTICE's value-add, never for Bentley cloud spend (OSS-only stance preserves margin).

## Risk register

- **Bentley/Cesium acquisition trajectory** (Sept 2024 acquisition; Patrick Cozzi → Bentley CPO): iTwin.js rendering API may shift between major versions. Mitigation: `CameraSyncAPI` against generic `CameraState`, never iTwin.js or Cesium-specific camera types. (Already a cardinal rule.)
- **`@deck.gl-community/editable-layers` is "semi-maintained"** post-nebula.gl abandonment. Mitigation: DrawAPI abstraction in exactly one adapter file. (Already a cardinal rule.)
- **VW 2026 SDK satellite-credentials requirement** — must be handled as packaging step, not a custom file invention. See `vw-2026-toolchain.md`.
- **OGC CityGML Vegetation ADE publication timing unknown** — MARPA schema mirrors the conceptual model from the ISPRS 2024 paper. If OGC publishes a divergent normative XSD, expect a mechanical mapping step.

## Cross-references

- `marpa-research-report-v2-20260508-verified.md` — full claim-verified report (this synthesis draws from it)
- `marpa-research-report-v1-20260508.md` — v1 (superseded; kept for provenance)
- `bentley-ecosystem-deep-dive-20260508.md` — Partner Program / BDN / Activate / developer channels deep dive
- `meta/harness/docs/specs/amended-research-proposal.md` — research framing that produced these reports
- `meta/harness/docs/specs/itwin-visgl-slide-bullets.md` — 28-slide architecture spec (the source document that v2 verifies)
- `outreach-templates.md` (sibling spec) — outbound messaging derived from this BI
- `itwin-pricing.md` (sibling research) — pricing-side competitive intelligence
- `vw-2026-toolchain.md` (sibling research) — technical-stack constraints
