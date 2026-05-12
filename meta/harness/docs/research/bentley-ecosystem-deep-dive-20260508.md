---
title: "Navigating the Bentley Developer and Partner Ecosystem: A Strategic Deep Dive for the Marpa Landscape Architecture Initiative"
date: 2026-05-08
version: 1.0
mode: ultradeep
scope: "Bentley iTwin Partner Program · Bentley Developer Network · iTwin Activate · Product Roadmap Channels"
proposer: "Jeromy — independent technologist and developer"
---

## Executive Summary

The Bentley Systems developer and partner ecosystem offers four distinct programmatic pathways relevant to Marpa Landscape Architecture's proposed technology modernization initiative. Each pathway serves a different strategic purpose, requires different timing, and unlocks different resources — and understanding exactly how they interlock is the single highest-leverage piece of information Jero needs before making first contact with Bentley.

The iTwin Partner Program is the entry gate and costs nothing to join. It exists in two tiers — Standard and Premier — and operates through three structured engagement phases (Envision, Design, Sprint) that move partners from initial use-case exploration to active co-development hackathons. Bentley explicitly recruits independent software vendors, systems integrators, and solution providers. An integration partner building a bridge between Vectorworks Landmark and iTwin maps cleanly onto their ISV category, and the open-year-round application process means Marpa can be inside the ecosystem within weeks [1].

The Bentley Developer Network (BDN) is a separate, older subscription program that predates the iTwin era and governs SDK access for Bentley's broader product portfolio. It operates in two tracks: a Commercial Subscription for developers building products to sell, and a SELECT Subscription for Bentley licensees building internally. The BDN is architecturally distinct from the iTwin Partner Program — iTwin's developer tooling (the core iTwin.js library and all REST APIs) is MIT-licensed and publicly accessible without a BDN subscription. For Marpa's specific use case — building on the public iTwin REST APIs and the open-source iTwin.js library — the BDN may not be required at the outset, but it becomes relevant if and when the initiative needs SDK-level access to non-iTwin Bentley products such as MicroStation or OpenRoads [2].

The iTwin Activate accelerator is the most strategically significant program for Marpa. Run by iTwin Ventures, a $100 million committed corporate VC fund, it funds early-stage companies with up to $250,000 via SAFE note across themed 20-week co-development cohorts. Five cohorts have been completed since the program launched in 2023, spanning verticals from electric grid infrastructure to Cesium-native 3D geospatial applications. The most recent cohort (Cesium and 3D Tiles, 2025) selected four participants whose selection pattern provides a clear playbook: every winner was a bridge/integration play connecting an external data ecosystem to iTwin for a vertical iTwin does not currently serve natively. Marpa's proposed Vectorworks-to-iTwin landscape architecture bridge is a textbook fit for this pattern — with the added advantage that Marpa is itself the named pilot customer, eliminating the "find a customer" risk that typically challenges early-stage accelerator applicants [3, 4].

The product roadmap and developer engagement channels — GitHub (github.com/iTwin), Bentley Communities, the developer blog at developer.bentley.com, and the Year in Infrastructure conference — form the intelligence layer. Bentley's roadmap is genuinely more transparent than most infrastructure software vendors: API changelogs are public, GitHub discussions surface feature gaps, and early access programs like iTwin Engage accept applications on a rolling basis. For Marpa, active engagement with these channels signals technical seriousness to the Bentley team and creates an evidence trail of sustained commitment before any formal program application [5, 6].

The strategic sequence that follows from this analysis is clear: secure Marpa principal authorization first, then apply to the Partner Program immediately (this week, not next quarter), begin GitHub engagement in parallel, warm outreach to James Kress and Clive Hackforth before the 2026 Activate window opens, and position for an iTwin Activate application the moment the 2026 cohort is announced.

---

## Introduction

### Scope

This report constitutes a dedicated deep dive into the Bentley Systems developer and partner ecosystem, produced as a companion addition to the Marpa Landscape Architecture Technology Modernization Initiative research series. While the primary gap analysis report (v2.0) established the strategic rationale — Vectorworks Landmark has no iTwin connector, iTwin has no landscape architecture vertical, and no competitor occupies this whitespace — this report provides the operational intelligence needed to navigate Bentley's programs in the right order, at the right pace, with the right framing.

Four pillars are analyzed in depth: the iTwin Partner Program (the organizational entry gate), the Bentley Developer Network (SDK and technical resource layer), iTwin Activate (the corporate VC accelerator and co-funding mechanism), and the product roadmap and developer engagement channels (the ongoing intelligence and relationship layer). Each pillar is analyzed for structure, eligibility, cost, benefit, and Marpa-specific strategic relevance.

### Methodology

Research was conducted on May 8, 2026 using direct web fetches of primary Bentley documentation, developer portals, official press releases, and third-party industry coverage of program participants. Primary sources consulted include the official iTwin Partner Program page, the iTwin Activate program page, the iTwin Platform pricing page, the Cesium blog (which co-hosted the 2025 cohort announcement), individual participant company pages for cohort participants SuperDNA 3D Lab and IPS AI, the GitHub iTwin organization repository, Bentley newsroom announcements, and trade press coverage of program launches. Where official documentation was silent on specific terms (notably the BDN pricing and the specific SAFE note investment terms), this is explicitly noted and the gap is flagged as a high-materiality assumption.

### Key Assumptions

The following assumptions carry material weight and should be verified before acting on specific recommendations:

**High-materiality assumption 1:** BDN pricing is not publicly disclosed on any page accessible at time of research. The two subscription tier categories (Commercial and SELECT) are confirmed from multiple sources, but specific annual fees are not. The assumption that BDN is not required for iTwin REST API development is based on Bentley's explicit documentation that iTwin.js is MIT-licensed and the APIs are publicly accessible — but BDN costs are unknown and should be requested directly from Bentley before budgeting.

**High-materiality assumption 2:** SAFE note specific terms — valuation cap, discount rate, most-favored-nation clause — are not disclosed by Bentley in any public document. The "$250,000 maximum via SAFE note" figure is confirmed across multiple sources, but the specific economic terms of conversion are bilaterally negotiated and will only appear in a term sheet. The report treats the SAFE as potentially non-dilutive in the short term (pre-funding round) but acknowledges that SAFE conversion economics vary significantly based on undisclosed terms.

**High-materiality assumption 3:** The 2026 iTwin Activate cohort theme, application window, and eligibility criteria are not yet announced as of May 2026. Historical patterns from five prior cohorts inform strategic guidance, but the specific theme of the 2026 cohort may shift the framing required.

---

## Pillar 1: The Bentley iTwin Partner Program

> **Commercial-terms layer gated under `_gated/bentley-commercial/partner-program.md`** — see `_gated/README.md` for the dormancy policy and the five-gate activation procedure.
>
> What remains in scope from Pillar 1 under default doctrine:
> - Partner Program **applications are free and accepted year-round** (this fact is doctrine-aligned and stays here).
> - Partner Program is the operational channel through which LATTICE *applies* — the application path is referenced from `meta/harness/docs/specs/outreach-templates.md`.
> - Tier specifics (Standard vs. Premier), three engagement phases (Envision / Design / Sprint), and the co-marketing / commercial-implications layer live in the gated file. Activate Gate B when accepted into the program.

## Pillar 2: The Bentley Developer Network (BDN) and iTwin Platform Pricing

> **Gated under `_gated/bentley-commercial/bdn-developer-access.md` (BDN tiers + non-iTwin SDK scope)** and **`_gated/bentley-commercial/itwin-pricing.md` (iTwin Platform Community / Standard / Premium / Enterprise tier table + credit cost structure)**. See `_gated/README.md` for the dormancy policy.
>
> What remains in scope from Pillar 2 under default doctrine:
> - **`@itwin/core-geometry`, `@itwin/core-common`, `@itwin/core-quantity`, `@itwin/core-frontend` are MIT-licensed.** This is doctrine-aligned and stays here.
> - **iTwin REST APIs are publicly accessible.** The protocol surface is doctrine-aligned and stays here.
> - **iTwin.js library is MIT.** Doctrine-aligned.
> - **BDN is NOT required for iTwin REST API development.** This fact is doctrine-aligned and stays here. BDN itself (Commercial Subscription, SELECT Subscription, non-iTwin SDK scope) is gated.
> - iTwin Platform paid-tier credit budgets and pricing tables are gated. Architecting LATTICE against any specific paid tier is forbidden until a gate fires.

## Pillar 3: iTwin Activate — The Corporate VC Accelerator

> **Gated under `_gated/bentley-commercial/activate-program.md`** — see `_gated/README.md` for the dormancy policy.
>
> What remains in scope from Pillar 3 under default doctrine:
> - **Activate exists as a vendor program.** This fact is doctrine-aligned and stays here.
> - **Application path** to Activate is referenced from `meta/harness/docs/specs/outreach-templates.md` (outreach is the single permitted use of gated content).
> - **Activate is a Gate A trigger.** When LATTICE is accepted into a cohort, follow the activation procedure in `_gated/README.md` — open a PRD-tracked issue before architecting against newly-active capabilities.
>
> Specifics — SAFE structure, $250K cap, iTwin Ventures $100M fund and $250K-$5M check range, cohort history and pattern, named contacts, 20-week structure, investment mechanics — all live in the gated file.

## Pillar 4: Product Research and Roadmap Channels

### 4.1 Official Documentation and API Changelogs

Bentley's developer portal at developer.bentley.com is the primary authoritative source for the iTwin Platform's current capabilities and near-term development direction [6]. The portal provides API reference documentation, conceptual guides, sample applications, and — critically — per-API changelogs that document when new capabilities are added. The Reporting API changelog, for example, tracks feature additions by API version [14]. For Marpa, monitoring the Synchronization API changelog is the fastest way to detect if a Vectorworks VWX connector is added to the supported formats list — a development that would fundamentally simplify the integration path and reduce its technical moat value.

The developer blog at developer.bentley.com/blog/ publishes technical walkthroughs of new API capabilities, integration patterns, and platform updates. These posts are written by Bentley engineers and product managers — the same people who run the Design phase of the Partner Program — and represent the closest thing to an unmediated developer roadmap signal available without a formal partnership relationship.

### 4.2 GitHub: The Open Development Layer

Bentley's GitHub organization at github.com/iTwin is the single most information-dense source of real-time platform intelligence available [5]. The organization hosts multiple repositories of direct relevance:

**iTwin/itwinjs-core** is the core MIT-licensed library with 714 stars, 237 forks, and 21,333 commits as of May 2026. The repository maintains 184 releases and was last updated in May 2026 with version 5.9.2, confirming active development. The 343 open issues represent real developer pain points — reading through them reveals where the platform is technically mature (iModel ingestion, 3D rendering) and where gaps persist (landscape-specific schemas, vegetation data models, CityGML integration) [5].

**iTwin/iTwinUI** is the design system for building web interfaces on iTwin — relevant for Marpa's client-facing portal layer.

**github.com/orgs/iTwin/discussions/categories/ideas** is the official feature idea submission channel, where developers can propose improvements and other community members vote on them [15]. Submitting a well-articulated idea for "Landscape architecture planting semantic schema for IFC VEGETATION elements" or "CityGML 3.0 Vegetation ADE connector" serves two purposes: it creates a permanent record of Marpa's technical intent that Bentley product managers can reference, and it surfaces community demand for a capability that only Marpa's initiative is currently proposing. Even one or two upvotes from landscape architecture adjacent communities (municipal GIS, ecological monitoring) signals genuine demand.

The GitHub Discussions board (separate from the Ideas category) is where developers post technical questions and receive responses from both the community and Bentley engineers. Active participation — answering questions about IFC vegetation semantics or CityGML integration that other developers raise — builds reputation within the developer community and creates organic visibility for Marpa's expertise before the first formal Bentley conversation.

### 4.3 Bentley Communities: The ServiceNow-Based Forum Network

Bentley operates a community platform at bentleysystems.service-now.com/community that hosts multiple topical forums [16]. The relevant forums for Marpa are:

The **iTwin Services Forum** for questions and discussions about the iTwin Platform APIs, Synchronization, and integration patterns [16]. This is where developers raise technical issues with the APIs and where Bentley engineers respond. Reading the forum history for the last 12–18 months reveals which integration patterns are causing friction, which APIs have known limitations, and what workarounds Bentley engineers recommend. For the IFC VEGETATION semantic mapping challenge specifically — a problem unique to landscape BIM integrations — the forum history is likely sparse, which means Marpa's posting of a well-framed technical question would receive direct attention from Bentley engineers.

The **Bentley Developer Network Forum** for SDK-level technical questions [16]. This is most relevant if and when the BDN becomes part of Marpa's resource stack.

The **bentley-itwin community topic** aggregates cross-product iTwin discussions and is the highest-traffic entry point for general platform questions [16].

### 4.4 iTwin Engage Limited Availability Program

iTwin Engage is Bentley's next-generation immersive visualization platform, blending iTwin, Cesium, Unreal Engine, and open geospatial standards [17]. It entered a limited availability program accepting applications on a rolling basis as of 2025. Participation requires: project data stored as an iTwin; current Bentley Infrastructure Cloud user status; and a role as a Virtual Design/Construction Engineer, BIM Manager, or 4D Planner [17].

For Marpa, the Engage limited availability program is a relevant parallel track for two reasons. First, iTwin Engage explicitly includes AI vegetation placement in its Copilot toolset [18] — participating in the limited availability program gives Marpa visibility into exactly how Bentley is approaching vegetation in the digital twin context and how deep (or shallow) the horticultural data model goes. Second, participating organizations that provide feedback on Engage become part of Bentley's product development conversation at an early stage, which creates the same relationship-building effect as GitHub participation, but at the product manager level rather than the engineering level.

### 4.5 Year in Infrastructure (YII): The Annual Roadmap Signal

Bentley's Year in Infrastructure conference, held annually in October, is the single most important signal for Bentley's product strategy. It is where Bentley announces major product direction changes (the "+"-branded generational rebuilds of SYNCHRO+ and OpenSite+ were announced at YII 2025), new partnership directions, and accelerator cohort outcomes [19]. The 2024 YII was where Bentley signaled the Cesium-native iTwin architecture; the 2025 YII confirmed SYNCHRO+ and OpenSite+ as AI-native rebuilds; and the 2026 YII (expected October 2026) will likely reveal the next major platform direction.

For Marpa, attending YII — virtually or in person — serves as both intelligence gathering and relationship visibility. The conference brings together Bentley product managers, engineering leadership, partner companies, and infrastructure owner clients in one place. A Marpa representative who is visibly present at YII 2026, having already submitted a Partner Program application, engaged on GitHub, and built a relationship with James Kress through warm outreach, arrives at the conference as a known quantity rather than an unknown applicant.

### 4.6 Direct PM Engagement: The Undocumented Channel

The most valuable roadmap intelligence comes from direct conversations with Bentley product managers — not from public documentation. Bentley product managers publish on LinkedIn, present at YII, and respond to substantive technical inquiries through the Partner Program's Design phase. They also respond to feature requests submitted through the GitHub Ideas channel when those requests are technically detailed, commercially justified, and represent a novel use case.

A practical approach for Marpa: before formal Partner Program acceptance, identify the Landmark-adjacent product managers at Bentley — those responsible for the Synchronization API, the iModel schema team, and the iTwin Engage product — and engage them on LinkedIn with substantive technical observations (the IFC VEGETATION semantic gap, the absence of CityGML Vegetation ADE connector support) rather than sales pitches. Product managers respond to genuine technical engagement. They do not respond to cold applications asking for product access.

---

## Synthesis and Strategic Implications

The four pillars of the Bentley ecosystem, viewed together, reveal a coherent strategic architecture that Marpa must navigate sequentially rather than simultaneously. Each program serves a different purpose at a different stage of maturity, and premature entry into the wrong program wastes organizational capital that cannot be recovered.

The most important structural insight is that the iTwin Partner Program and iTwin Activate are not alternatives — they are sequential. The Partner Program is the organizational foundation that Activate applicants are expected to already have in place. Every confirmed Activate participant builds on iTwin; every one of them had presumably explored the platform (often through the Partner Program or through direct API development) before applying to the accelerator. Applying to Activate without a Partner Program relationship and without a working prototype is applying cold — and cold applications lose to applicants who have been building relationships for months.

The second structural insight is that Bentley's open developer ecosystem (MIT-licensed iTwin.js, public REST APIs, GitHub discussions, open changelogs) is genuinely more permissive than its infrastructure software peers. Marpa can begin substantive technical development and community engagement without any formal program membership. The Community tier of the API provides 100 credits/month for exploration, GitHub is fully public, and the documentation is comprehensive. This means the "waiting to join a program" mentality is a strategic error — the work should begin now, and the formal programs should follow the work.

The third insight is specific to Marpa's unique positioning: the landscape architecture vertical is a provably unoccupied gap in iTwin's ecosystem, and a 50-year practice with 51 ASLA awards and real Vectorworks project data is the rarest possible application credential. No other Activate applicant in the program's history has had the pilot customer built into the applicant's own practice. This is a structural advantage that should be the first sentence of every Bentley interaction.

---

## Strategic Sequence: The Exact Chronological Order

The following sequence represents the optimal order of actions, derived from the program timelines, relationship-building requirements, and the historical pattern of successful Activate participants.

**Weeks 1–2: Secure Marpa Principal Authorization**
Before any external outreach, Jero needs authorization from Marpa LA's principals to use the firm's name, credentials, and project data in vendor applications. This is Template 1 in the outreach sequence. The principals must understand that: (a) Phase 1 costs the firm almost nothing, (b) the Bentley SAFE note structure likely requires forming a separate technology entity, and (c) the opportunity window is time-sensitive (Activate 2026 applications likely close in July 2026).

**Weeks 1–4: Apply to the iTwin Partner Program**
The application takes minutes to complete. Acceptance signals to every future Bentley interaction that Marpa is inside the ecosystem, not outside it. The Partner Program is the credential that turns a cold Activate application into a warm one. Apply via bentley.com/software/itwin-partner-program/ immediately after principal authorization.

**Weeks 2–8: Begin GitHub Engagement**
Create a GitHub account for the initiative. Subscribe to the iTwin/itwinjs-core repository. Read the open issues — specifically any issues related to IFC, vegetation, geospatial, or landscape data. Submit a well-articulated feature idea to github.com/orgs/iTwin/discussions/categories/ideas about landscape planting semantic schema support. This costs zero dollars and creates permanent evidence of technical seriousness.

**Weeks 2–8: Warm Contact with James Kress and Clive Hackforth**
LinkedIn outreach with a one-paragraph pitch + a link to Prototype 1 (when ready). Do not wait for the Activate announcement. The relationship before the application window opens is the advantage. The pitch should reference: Marpa as the named pilot firm (51 ASLA awards, 50-year practice), the Vectorworks→iTwin gap (confirmed by Synchronization API documentation), and the Cesium 3D Tiles native architecture (aligned with Bentley's platform direction post-Cesium acquisition).

**Weeks 4–12: Build and Deploy Prototype 1**
The web viewer: Vectorworks IFC4 export → web-ifc → React Three Fiber / Three.js → deck.gl + Cesium 3D Tiles via Cesium ion. Deploy to a public URL. This demo URL is the most powerful element of every subsequent Bentley interaction. An application with a live demo outperforms a proposal without one by an enormous margin — every Activate cohort participant has shipped something.

**Months 3–6: Pursue iTwin Engage Limited Availability**
Apply to the iTwin Engage limited availability program to gain early access to Bentley's immersive visualization layer and begin the product feedback relationship with Bentley's product managers.

**Month 4 onwards: Partner Program Design Phase**
After Partner Program acceptance, schedule the Design phase session with Bentley's iTwin Platform engineers. Use this session to get architectural guidance on: (a) the correct Synchronization API path for IFC-based landscape data ingestion, (b) the iModel schema options for extending VEGETATION semantics, (c) the Cesium ion pipeline for Prototype 1, and (d) how CityGML 3.0 output would be handled in the current API surface.

**Summer 2026 (June–July): Apply to iTwin Activate 2026**
When the 2026 cohort is announced, Marpa should have: Partner Program membership, a live Prototype 1 demo, a warm relationship with James Kress and Clive Hackforth, Marpa principal authorization documentation, and a polished pitch deck. The application should be prepared in advance using the historical cohort framing language: "design-centric digital twin bridge for site-scale and landscape-adjacent infrastructure, using an established 50-year landscape architecture firm as the named pilot customer."

**Month 6–9: Apply to Bentley Developer Network (Commercial) if Needed**
If the integration roadmap requires SDK-level access to Bentley products beyond the iTwin public APIs — specifically if a native VWX-to-iTwin connector is prioritized — apply to the BDN Commercial Subscription. Contact Bentley's developer support team for pricing and terms.

| Timeline | Action | Program | Investment Required |
|----------|--------|---------|---------------------|
| Weeks 1–2 | Marpa principal authorization | Internal | None |
| Weeks 1–4 | Apply to iTwin Partner Program | Partner Program | None |
| Weeks 2–8 | GitHub engagement (Issues, Ideas) | Open ecosystem | None |
| Weeks 2–8 | Warm outreach (Kress, Hackforth) | Activate prep | None |
| Weeks 4–12 | Build and deploy Prototype 1 | Development | Engineering time |
| Months 3–6 | Apply to iTwin Engage LA program | Engage beta | None |
| Month 4+ | Partner Program Design phase | Partner Program | None |
| Summer 2026 | Apply to iTwin Activate 2026 | Activate | $0 upfront; SAFE note on acceptance |
| Month 6–9 (if needed) | BDN Commercial Subscription | BDN | Subscription fee (undisclosed) |

---

## Limitations and Caveats

Several material limitations apply to this report and should inform how its findings are acted on.

The BDN subscription pricing is not publicly disclosed. The report confirms the existence of Commercial and SELECT subscription tiers and their general purpose, but specific annual fees are unknown. Before budgeting for BDN access, Jero should contact Bentley's developer support team directly at bentley.com/support/software-developers/ to request a quote.

The SAFE note terms for iTwin Activate are not publicly disclosed. The $250K maximum is confirmed across multiple sources, but valuation cap, discount rate, and MFN provisions are bilateral and confidential. Legal review by a startup-experienced attorney is required before acceptance.

The iTwin Partner Program's tier transition criteria are not publicly specified. The report establishes that Standard and Premier tiers exist with "basic" vs. "enhanced" support, but the criteria for advancing from Standard to Premier are not documented and are presumably negotiated with Bentley's partner team.

The 2026 iTwin Activate cohort theme, application window, and eligibility criteria have not been announced as of May 2026. The strategic guidance in this report is based on historical cohort patterns, which may not predict the 2026 theme with certainty.

The third iTwin Activate cohort (Generative AI) participant roster was not fully documented in any publicly accessible source at time of research. The pattern analysis in Section 3.2 is therefore based on confirmed cohorts 1, 4, and 5, with cohorts 2 and 3 partially inferred.

---

## Recommendations

The following recommendations are ordered by priority and urgency.

Apply to the iTwin Partner Program this week. The application requires minutes to complete, costs nothing, and creates the organizational foundation for every subsequent Bentley interaction. There is no strategic reason to delay.

Begin GitHub engagement in parallel with the Partner Program application. Subscribe to iTwin/itwinjs-core, read the open issues, and submit a feature idea for landscape planting semantic schema support. This is free and creates permanent evidence of technical commitment.

Warm outreach to James Kress (LinkedIn: linkedin.com/in/jim-kress-1a14201b/) should happen within 30 days of principal authorization. Reference the Marpa firm specifically — 51 ASLA awards, 50-year practice, Vectorworks Landmark shop — and the Cesium 3D Tiles native architecture alignment. Copy Clive Hackforth (linkedin.com/in/clive-hackforth/).

Build Prototype 1 before any formal Activate application. A live URL is worth 10 pitch decks. The application window for Activate 2026 is likely to open in June or July — that is 8–10 weeks from now. Prioritize the web viewer demo above all other deliverables.

Consult a startup-experienced attorney about the SAFE note / entity structure question before committing to an Activate application. The Marpa LA partnership firm and a separate technology entity have different implications for SAFE conversion. This is a one-time structural decision with permanent consequences.

---

## Bibliography

[1] Bentley Systems (2026). "iTwin Partner Program." bentley.com/software/itwin-partner-program/ Retrieved May 8, 2026.

[2] Bentley Systems. "Bentley Developer Network (BDN)." bentleysystems.service-now.com/community?id=kb_article_view&sysparm_article=KB0012395 Retrieved May 8, 2026.

[3] Cesium (2025, July 9). "Applications Now Open: iTwin Activate Cohort Focusing on Cesium and 3D Tiles." cesium.com/blog/2025/07/09/itwin-activate-cohort-cesium-3d-tiles/ Retrieved May 8, 2026.

[4] Cesium (2025, September 22). "Participants Announced for iTwin Activate Cohort Focusing on Cesium and 3D Tiles." cesium.com/blog/2025/09/22/participants-announced-for-itwin-activate-cohort/ Retrieved May 8, 2026.

[5] GitHub — iTwin Organization (2026). "iTwin/itwinjs-core." github.com/iTwin/itwinjs-core Retrieved May 8, 2026. (MIT License, v5.9.2, 714 stars, 237 forks, 21,333 commits.)

[6] Bentley Systems (2026). "iTwin Platform Developer Portal." developer.bentley.com Retrieved May 8, 2026.

[7] Bentley Systems (2026). "Partner Programs." bentley.com/partner-programs/ Retrieved May 8, 2026.

[8] Bentley Systems (2024, October). "Bentley Systems Announces Winners of its 2024 Partner Excellence Awards." bentley.com/news/bentley-systems-announces-winners-of-its-2024-partner-excellence-awards-2/ Retrieved May 8, 2026.

[9] Bentley Systems (2026). "iTwin Platform Pricing." developer.bentley.com/pricing/ Retrieved May 8, 2026.

[10] Bentley Systems (2026). "iTwin Ventures." bentley.com/company/itwin-ventures/ Retrieved May 8, 2026.

[11] Bentley Systems / Blog (2025). "From Drone Scans to Digital Twins: Bentley Accelerator Awards $250,000 to Startups Using 3D Tech for Infrastructure." blog.bentley.com/insights/from-drone-scans-to-digital-twins-bentley-accelerator-awards-250000-to-startups-using-3d-tech-for-infrastructure/ Retrieved May 8, 2026.

[12] Construction & Property News (2025). "Bentley Systems Awards $1 Million to 3D Tech Startups for Infrastructure Innovation." construction-property.com/bentley-systems-awards-1-million-to-3d-tech-startups-for-infrastructure-innovation/ Retrieved May 8, 2026.

[13] Bentley Systems (2023, June). "Bentley Systems Announces iTwin Activate: Infrastructure Internet of Things." bentley.com/news/bentley-systems-announces-itwin-activate-infrastructure-internet-of-things/ Retrieved May 8, 2026.

[14] Bentley Systems (2026). "Changelog — Reporting API." developer.bentley.com/apis/insights/changelog/ Retrieved May 8, 2026.

[15] GitHub (2026). "iTwin Ideas — Discussions." github.com/orgs/iTwin/discussions/categories/ideas Retrieved May 8, 2026.

[16] Bentley Systems Community (2026). "iTwin Services Forum." bentleysystems.service-now.com/community?id=community_forum&sys_id=151077ca1b1a3110f3fc5287624bcbaa Retrieved May 8, 2026.

[17] Bentley Systems (2025). "iTwin Engage Limited Availability Program." bentley.com/lp/itwin-engage-limited-availability-program/ Retrieved May 8, 2026.

[18] Bentley Systems (2025). "Year in Infrastructure 2025." bentley.com/news/bentley-systems-advances-infrastructure-ai-with-new-applications-and-industry-collaboration/ Retrieved May 8, 2026.

[19] Bentley Systems (2025). "A Groundbreaking Year for Infrastructure Intelligence." blog.bentley.com/insights/a-groundbreaking-year-for-infrastructure-intelligence/ Retrieved May 8, 2026.

[20] Intelligent Project Solutions (2025). "Bentley Invests in IPS AI." ips-ai.com/resource-centre/news/bentley-invests-in-ips-ai-to-integrate-with-itwin-platform/ Retrieved May 8, 2026.

[21] SuperDNA 3D Lab (2025). "Bentley iTwin Integration & Interoperability Services." superdna3dlab.com/bentley-itwin-integration-interoperability-services/ Retrieved May 8, 2026.

[22] Bentley Systems (2023). "Bentley iTwin Activate — IoT Cohort Announcement." controlglobal.com/industry-news/news/33007451/bentley-systems-bentley-supports-iot-for-infrastructure-startups Retrieved May 8, 2026.

---

## Methodology Appendix

**Research date:** May 8, 2026
**Mode:** Ultradeep
**Sources consulted:** 22 primary and secondary sources across official Bentley documentation, developer portals, press releases, participant company pages, GitHub repositories, and trade press coverage
**Source types:** Official vendor documentation (8), developer portals (3), press releases (4), participant company pages (2), trade press (3), GitHub repository (1), conference/event material (1)

**Outline adaptations from Phase 4.5 OUTLINE REFINEMENT:**
- Added explicit SAFE note structure caveat after discovering that the Bentley iTwin Ventures page confirms investment range is "$250K to $5M" — the $250K SAFE note is the Activate entry point, not the ceiling of the relationship
- Expanded the "does Marpa need the BDN?" analysis after discovering that iTwin.js is MIT-licensed with no BDN requirement for iTwin REST API development — a nuance not initially in scope
- Added strategic insight about entity structure (SAFE note requires a separate incorporated entity) after confirming that all Activate participants are independent companies, not divisions of larger professional services firms
- The Cohort 3 (GenAI) participant roster was not recoverable from public sources; this gap is noted in Limitations

**Claim verification status:**
- iTwin Partner Program two-tier structure (Standard/Premier): CONFIRMED via official program page [1]
- iTwin Activate $250K SAFE note: CONFIRMED via Cesium blog [3] and Bentley blog [11]
- 20-week cohort duration: CONFIRMED via multiple sources [3, 13]
- iTwin.js MIT license: CONFIRMED via GitHub [5]
- Developer pricing tiers and credit costs: CONFIRMED via developer.bentley.com/pricing/ [9]
- Cohort 5 participants (AERO AI, TCP, Jakarto, SuperDNA): CONFIRMED via Cesium [4] and Bentley blog [11]
- Cohort 1 participants (Spatial Data.AI, VTS, Rebase, SurPlus): CONFIRMED via Bentley newsroom [13]
- Cohort 4 participants (TCP, IPS AI, Roebling, Telemattica): CONFIRMED via multiple press sources [20, 22]
- BDN subscription tiers (Commercial vs SELECT): CONFIRMED via Bentley support and BDN brochure [2]
- iTwin Ventures $100M fund, $250K–$5M range, Seed–Series B: CONFIRMED via iTwin Ventures page [10]
- James Kress quote ("fill gaps"): CONFIRMED via Bentley blog [11]
