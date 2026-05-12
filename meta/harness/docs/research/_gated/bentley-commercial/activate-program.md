---
title: "iTwin Activate — Corporate VC Accelerator (SAFE / Cohorts / iTwin Ventures Pipeline)"
type: research
status: dormant
gate_required: ["Gate A: Accelerator", "Gate B: Partner Program", "Gate C: Developer Subscription", "Gate D: External Funding", "Gate E: Client-Funded Seat"]
gate_status: not_triggered
activation_log: []
doctrine_default: "iTwin OSS self-hosted only — content here is dormant under default doctrine"
vendor: "Bentley Systems"
source: "Extracted from meta/harness/docs/research/bentley-ecosystem-deep-dive-20260508.md § Pillar 3 in Phase 1.5 §5.2"
---

> **Gated content.** Read `_gated/README.md` (top-level dormancy policy) and `_gated/bentley-commercial/README.md` (vendor-specific gate state) before using anything below for architectural purposes. The only permitted use of this file in dormant state is **drafting outreach to Bentley** (see `meta/harness/docs/specs/outreach-templates.md`).

## Pillar 3: iTwin Activate — The Corporate VC Accelerator

### 3.1 Program Architecture and Fund Structure

iTwin Activate is a themed co-development accelerator operated by iTwin Ventures, a dedicated corporate venture capital fund that Bentley Systems committed $100 million to invest over a five-year period [10]. The fund's investment mandate spans Seed to Series B, with individual investments ranging from $250,000 to $5 million per company — meaning iTwin Activate's $250K SAFE note is the entry point of a larger funding relationship, not the ceiling. Companies that complete an Activate cohort and demonstrate traction can pursue follow-on investment from iTwin Ventures outside the cohort structure [10].

The Activate program functions as the first filter and first investment in iTwin Ventures' pipeline. A company that goes through Activate demonstrates technical capability on Bentley's platform, validates a real infrastructure use case, and builds relationships with Bentley's product and commercial teams. These relationships are the channel through which larger Seed or Series A conversations begin. The implication for Marpa is that a successful Activate cohort is not just $250K — it is the beginning of a Bentley co-investment and co-development relationship that can scale to $5M and a formal commercial partnership.

iTwin Ventures also describes its value proposition beyond capital: industry expertise and mentorship, access to the iTwin Platform (including capabilities beyond what the public APIs expose), and connections with infrastructure industry leaders across Bentley's client base [10]. This last point is particularly valuable for Marpa, because Bentley's clients are the exact organizations — municipalities, campus institutions, transit agencies, infrastructure owners — who would be the end customers for a landscape BIM digital twin handover.

### 3.2 Cohort History and Evolution: Five Cohorts, Clear Pattern

The iTwin Activate program has operated five confirmed cohorts since its launch in 2023, each with a distinct technology or industry theme. Understanding the full cohort history reveals a consistent selection pattern that Marpa can apply directly to its application framing.

| Cohort | Theme | Year | Confirmed Participants |
|--------|-------|------|------------------------|
| **1 — Grid** | Electric utility infrastructure | 2023 | Spatial Data.AI; Virtual Technology Simplified; Rebase Energy; SurPlus Maps |
| **2 — IIoT** | Infrastructure Internet of Things | 2023 | Announced summer 2023; participants not fully documented in public sources |
| **3 — Generative AI** | Generative AI for infrastructure | 2023–2024 | Theme confirmed; participant roster not fully documented |
| **4 — Asset Monitoring for Transportation** | Transportation infrastructure monitoring | 2024–2025 | The Cross Product (TCP); IPS AI; Roebling Labs; Telemattica |
| **5 — Cesium and 3D Tiles** | 3D geospatial and Cesium ecosystem | 2025 | AERO AI; The Cross Product (TCP); Jakarto; SuperDNA 3D Lab |

*Note: The Cross Product appeared in both Cohort 4 and Cohort 5, described by Cesium as their "second consecutive year" of participation — an unusual pattern suggesting Bentley extended support for a particularly aligned company.*

The pattern across all confirmed cohorts is consistent and clear: Bentley selects companies that build bridges or integration layers between external data ecosystems and iTwin for infrastructure verticals that iTwin does not currently serve natively. Every confirmed Cohort 1, 4, and 5 participant was an integration play — converting data from an external domain (LiDAR, drone imagery, railway sensor data, urban 3D mapping) into iTwin-consumable operational assets [3, 4, 11, 12].

### 3.3 The 2025 Cohort in Detail: The Closest Structural Analog

The Cohort 5 participants (Cesium and 3D Tiles, 2025) provide the most directly applicable precedent for Marpa, because the cohort theme explicitly aligned with the Cesium ion + 3D Tiles architecture that Marpa's proposed stack uses natively.

AERO AI transforms drone imagery, CAD/BIM models, and GIS data into 3D visualizations and AI insights for AEC firms, cities, and utilities [4]. The framing is identical to Marpa's: CAD/BIM source data → AI processing → infrastructure digital twin interface. The difference is sector (general AEC/cities vs. landscape architecture specifically) and data type (drone imagery vs. Vectorworks IFC planting/terrain/irrigation data).

SuperDNA 3D Lab, the Amsterdam-based participant, built "an end-to-end platform to manage infrastructure assets by connecting Cesium with iTwin Platform's asset management capabilities" [4]. Their explicit use of "connecting [external ecosystem] with iTwin" is precisely the framing Bentley rewards. Marpa's initiative connects Vectorworks Landmark (external landscape BIM ecosystem) with iTwin (infrastructure operations ecosystem) for a vertical iTwin has never served.

James Kress, Director of Digital Acceleration at iTwin Ventures, explained the Cohort 5 selection rationale: "These startups are going to help us fill gaps... building them on Bentley platforms" [11]. This is the exact language that should appear in Marpa's Activate application framing: the initiative fills a gap in Bentley's platform by bringing a $9.3B industry segment — US landscape architecture — into the iTwin ecosystem for the first time.

### 3.4 Investment Mechanics: What the SAFE Note Means

The iTwin Activate funding mechanism is a SAFE note — Simple Agreement for Future Equity — of up to $250,000 per cohort participant [3]. SAFE notes are common in early-stage startup financing and have specific structural characteristics that Marpa must understand before accepting them.

A SAFE note is not a loan. It does not accrue interest and does not have a maturity date requiring repayment. Instead, it converts to equity (ownership in the company) at a future triggering event — typically a priced equity financing round (Series A, B, etc.) or a liquidity event (acquisition, IPO). The conversion terms — valuation cap, discount rate, and most-favored-nation (MFN) provisions — determine the economic impact of the SAFE when it converts.

Bentley does not publicly disclose the specific SAFE terms for iTwin Activate participants. The "$250K maximum" is confirmed, but the valuation cap (which determines how much ownership Bentley receives when the SAFE converts), the discount rate (typically 10–25%), and MFN provisions are bilateral and confidential. This is a high-materiality assumption: the SAFE could be highly dilutive (low valuation cap relative to future rounds) or minimally dilutive (high valuation cap that allows conversion at market price). Legal review of the SAFE terms by a startup-experienced attorney is essential before acceptance.

Critically, for an established firm like Marpa Landscape Architecture rather than a startup, the SAFE structure presents a structural challenge worth analyzing. SAFEs are designed for venture-backed startups with equity to offer. If the Marpa initiative is positioned as an initiative of the existing Marpa LA partnership (not a separate incorporated startup), the SAFE conversion mechanism may not apply cleanly. One resolution path is to structure the initiative as a separate technology entity — which Bentley's Activate program precedents (all four to five participants per cohort are independent companies, not divisions of larger firms) suggest is required. A separate LLC or C-corporation is likely necessary to receive and convert a SAFE note. This structural decision should be addressed in the Marpa principal authorization conversation (Template 1).

### 3.5 The 20-Week Co-Development Structure

The Activate program runs for 20 weeks — approximately five months — on a virtual format [3, 13]. The structure is not publicly documented in granular detail, but confirmed program elements from multiple participant accounts include:

Technical support from Bentley and the cohort co-host (in 2025, from Cesium) for building the project using the cohort's thematic technology. For Marpa, in a future cohort, this technical support would include Bentley engineers and potentially Cesium engineers providing architecture guidance, API debugging, and design review on the Vectorworks→iTwin pipeline.

Industry and market insights from Bentley product leaders, including visibility into Bentley's commercial roadmap, customer use cases, and market strategy for the relevant vertical. This is valuable beyond the technical support — it is early access to proprietary Bentley strategic intelligence.

Access to Bentley products including the iTwin Platform and iTwin Capture, at production scale, for the duration of the program [3]. This means the Community tier's non-commercial constraints and credit limits are effectively waived during the cohort — participants build on the full platform.

Go-to-market guidance, including how to position within Bentley's partner ecosystem, how to approach joint sales with Bentley account managers, and how to build a case study and joint announcement for the post-cohort Phase.

The program kicks off in late August each year (based on 2025 timeline) and completes by mid-December [4]. Applications for each cohort close in late July. Bentley announces the cohort theme in June and opens applications in early-to-mid July, based on the 2025 pattern where the Cesium cohort was announced July 9, 2025 with an application deadline of July 25, 2025 — a 16-day application window [3]. This compressed timeline means that preparation — a working demo, a polished pitch, and an active Bentley relationship — must be in place before the announcement arrives. The relationship that wins Activate is built before the application window opens.

### 3.6 Strategic Positioning: How Marpa Uniquely Fits

Marpa Landscape Architecture's proposed initiative has several structural characteristics that differentiate it from a typical iTwin Activate applicant, in ways that are either advantages or challenges to manage.

The primary advantage is that Marpa IS the pilot customer. Every iTwin Activate cohort description references participants building for "a named customer segment" or demonstrating "a workflow end-to-end" for infrastructure. The most common risk in accelerator applications is the lack of a credible early customer commitment. Marpa eliminates this risk entirely: the pilot is Marpa's own 50-year practice with 51 ASLA awards and real Vectorworks Landmark project files ready to ingest. Bentley receives a named, award-winning landscape architecture firm as their first landscape BIM showcase on iTwin — a fact James Kress's stated goal ("fill gaps in Bentley's platform") maps directly onto.

The secondary advantage is that the Cesium 3D Tiles architecture is already central to Marpa's proposed stack. Cohort 5 made 3D Tiles native infrastructure. Bentley's acquisition of Cesium in September 2024 means the 3D Tiles architecture is now permanently iTwin-native. Any future cohort will implicitly favor applications that use this architecture. Marpa's deck.gl + Cesium 3D Tiles + Cesium ion viewer stack is architecturally aligned with Bentley's post-Cesium platform direction.

The primary challenge to manage is the SAFE note / entity structure question. Bentley's Activate program is designed for startups, and Marpa is an established professional services firm. The resolution is to structure the technology initiative as a separate entity — a technology spin-off or LLC — that holds the software IP, receives the SAFE funding, and eventually commercializes the integration to other landscape architecture firms. The Marpa LA practice is the pilot firm, the reference client, and the credential; the separate entity is the software company that Activate funds.

The secondary challenge is framing. Bentley's vertical list does not include landscape architecture. Applications that self-identify as "landscape architecture software" are entering a category Bentley doesn't recognize as a priority. The winning framing, derived from the Cohort 5 selection language, is: site-scale infrastructure digital twin bridge for green and site infrastructure, stormwater asset management, ecological monitoring, and campus/civic owner-operators. These frame the initiative within Bentley's documented verticals (Digital Cities, Environmental, Transportation, Utilities Reliability) rather than outside them.

---

