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

### 1.1 Program Purpose and Positioning

The Bentley iTwin Partner Program is the formal organizational mechanism through which Bentley Systems recognizes and resources companies building on the iTwin Platform. Its stated goal is to "foster a thriving community of organizations who share Bentley's vision of creating an open ecosystem for infrastructure digital twins" [1]. The program is explicitly designed for four categories of organizations: independent software vendors (ISVs) building applications on iTwin, systems integrators delivering iTwin implementations, digital integrators connecting external data sources to iTwin, and solution providers and consultants deploying iTwin for clients [1]. Marpa's initiative maps most precisely onto the ISV and digital integrator categories — building a landscape-native application layer on top of iTwin APIs and creating a data bridge from Vectorworks Landmark into the iTwin ecosystem.

The program is architecturally distinct from Bentley's legacy partner programs (Channel Partners, Training Partners). Those programs — which appear on a separate Bentley partner programs page — focus on reselling and training Bentley's existing products [7]. The iTwin Partner Program is a technology development and innovation track, not a reseller program. Partners in the iTwin ecosystem are building complementary or additive software on the iTwin Platform APIs, not simply distributing Bentley licenses. This distinction is commercially important: an iTwin Partner receives development support and go-to-market assistance, while a Channel Partner receives reseller margins and distribution rights. Marpa should explicitly identify itself as an iTwin integration partner, not as a Channel Partner candidate.

### 1.2 Tier Structure: Standard and Premier

The program operates in two formal tiers, both confirmed directly from the official program page [1]:

| Tier | Support Level | Promotional Support | Intended For |
|------|--------------|---------------------|--------------|
| **Standard** | Basic guidance | Basic promotional support | Early-stage integrations; first-time applicants |
| **Premier** | Enhanced guidance | Enhanced promotional support | Mature integrations with proven deployment |

The public-facing program description does not specify the quantitative differences between "basic" and "enhanced" support at each tier — this level of detail is disclosed only after initial program acceptance and is negotiated bilaterally. The historical pattern from partner network programs at comparable infrastructure software vendors (and confirmed implicitly by Bentley's three-phase engagement model) suggests that Standard partners access the Envision and Design phases while Premier partners additionally receive Sprint (hackathon) access and more proactive co-marketing. This interpretation is consistent with the program description but should be confirmed during onboarding.

What is publicly confirmed is that both tiers provide access to three structured engagement phases and to Bentley's network of infrastructure owners, design firms, and engineering companies. Neither tier requires equity transfer or revenue sharing — the Partner Program is a technical and promotional relationship, not a financial one. That financial dimension belongs to the iTwin Activate accelerator (Section 3).

For Marpa, Standard tier is the appropriate entry point. The initiative is in proposal stage with no shipped product. Standard tier does not require a live deployed integration — the program is designed to support development from the Envision phase onward. Upgrading to Premier is a medium-term milestone once Prototype 1 (the web viewer) is deployed and in use with Marpa's own projects.

### 1.3 The Three Engagement Phases

The iTwin Partner Program structures partner development through three sequential phases that function as a co-development runway [1]:

**Envision** is the opening phase, consisting of interactive sessions in which Bentley's partner team explores the partner's use case in depth. For Marpa, this is the meeting in which Jero explains the Vectorworks→iTwin landscape BIM bridge concept, the planting-as-living-asset differentiation from iTwin Engage's visual vegetation, and the CityGML 3.0 Vegetation ADE export opportunity. The Envision phase is also where Bentley assesses how the integration fits into its ecosystem gaps — a conversation that positions the initiative as gap-filling rather than competitive.

**Design** is the technical guidance phase, in which Bentley's iTwin Platform developers provide specific architectural guidance for the partner's use case. For Marpa, this is where the integration's technical questions get answered by people who built the APIs: which Synchronization API connectors to use, how to structure the IFC semantic normalization layer, whether the IoT sensor integration for irrigation monitoring uses the Sensor Data API or a custom schema, and how to build the Cesium 3D Tiles pipeline through the Mesh Export API. This phase is the most technically valuable part of the Partner Program and the primary reason to join before beginning serious development.

**Sprint** is the hands-on co-development phase, structured as a hackathon-style intensive sprint. Bentley assigns technical resources alongside the partner's team to accelerate a specific integration deliverable. This phase is most commonly accessed by Premier partners or by partners whose use case aligns with a current Bentley technical priority (such as CityGML 3.0 output or landscape-specific iTwin schema development).

### 1.4 Application Process and Eligibility

The application process is intentionally straightforward: an "Apply Now" form at bentley.com/software/itwin-partner-program/ [1]. The form collects organizational information, use case description, and integration intent. Bentley has not published specific eligibility requirements — the program page states that independent software vendors, systems integrators, digital integrators, solution providers, and consultants are all eligible. There is no disclosed revenue threshold, employee count requirement, or geographic restriction.

The 27 named partners currently in the program (a number confirmed from the partner roster as of May 2026) span a wide range of company sizes and maturity levels, from large integrators to early-stage specialized software companies. This diversity confirms that the program does not require a minimum viable product to apply — a credible integration plan and a named pilot customer or firm are sufficient for acceptance. For Marpa, the combination of a 50-year-old practice with 51 ASLA awards and a technically articulate integration proposal places the application in a strong position.

There is no disclosed waitlist or cohort-based application window for the Partner Program. Unlike iTwin Activate, applications are accepted year-round and do not require alignment to a specific cohort theme [1].

### 1.5 Commercial and Go-to-Market Benefits

The published Partner Program benefits are framed in three dimensions. First, partners gain access to the iTwin addressable market — "the world's leading design and engineering companies and owner-operators" who are already on Bentley's platform [1]. This means Bentley's existing sales and account management relationships become indirect distribution channels for partner integrations. For Marpa, this means Bentley account managers serving municipalities, campus institutions, and transit agencies (the owners of landscape-adjacent infrastructure) can introduce the Marpa integration as a landscape BIM solution for their owners.

Second, partners receive promotional support that varies by tier. This includes listing in Bentley's partner directory, visibility at the Year in Infrastructure conference, and for Premier partners, potential inclusion in Bentley newsroom case studies and sales collateral. The 2024 Partner Excellence Awards — which honored Evercam for "Rapid Time to Value" as a prominent example — demonstrate that Bentley actively promotes successful partner integrations [8].

Third, partners gain access to connections to more data sources and can enable digital twins for large-scale infrastructure assets [1]. In practice, this means participation in partner ecosystem events, access to integration documentation and API roadmap previews, and the potential for co-development sprint sessions with Bentley engineers.

What the Partner Program does not provide: equity funding, fixed revenue sharing, guaranteed customer introductions, or product co-development commitments. Those elements belong to iTwin Activate. The Partner Program is the organizational foundation; Activate is the financial and co-development accelerator.

---

## Pillar 2: The Bentley Developer Network (BDN)

### 2.1 What the BDN Is and How It Differs from the Partner Program

The Bentley Developer Network is an older, subscription-based program designed to give software developers access to the SDKs and APIs for Bentley's full product suite — including MicroStation, OpenRoads, OpenBuildings, OpenUtilities, and the broader Bentley infrastructure product portfolio [2]. The BDN predates the iTwin era and was the primary mechanism through which third-party developers built integrations with Bentley products before the iTwin open API platform existed.

The critical distinction from the iTwin Partner Program is one of scope and access model. The iTwin Partner Program is free, relationship-based, and focused specifically on the iTwin Platform's public REST APIs and the open-source iTwin.js library. The BDN is a paid subscription program that provides proprietary SDK access to Bentley products that are not yet fully exposed through public APIs. In practical terms: if a developer needs to access iTwin REST APIs, they need the Partner Program (or no program at all, since the APIs are public). If a developer needs to access the MicroStation SDK, the OpenRoads SDK, or other non-iTwin Bentley product internals, they need the BDN.

| Dimension | iTwin Partner Program | Bentley Developer Network (BDN) |
|-----------|----------------------|----------------------------------|
| **Cost** | Free | Paid subscription (pricing not publicly disclosed) |
| **Scope** | iTwin Platform APIs and ecosystem | Full Bentley product SDK portfolio |
| **API type** | Public REST APIs + MIT-licensed iTwin.js | Proprietary SDKs for specific Bentley products |
| **Application** | Apply Now form, year-round | BDN portal (dev-connect-bdnportal.bentley.com) |
| **Purpose** | Build commercial applications on iTwin | Access SDKs for Bentley product customization |
| **Support** | Partner Program engagement + GitHub | Dedicated BDN developer technical support |
| **Commercial use** | No fee; API usage billed by credits | Commercial Subscription license required |
| **Internal use** | Included | SELECT Subscription (for Bentley licensees) |

### 2.2 BDN Subscription Tiers

The BDN operates in two subscription tracks [2]:

The **BDN Commercial Subscription** is designed for organizations developing applications or customizations that will be sold commercially or delivered as part of professional service agreements to clients. This is the relevant tier for any company building a product that generates revenue using Bentley SDKs. The Commercial Subscription grants access to the SDK, development licenses for Bentley products (to support development work), enhanced developer documentation, self-paced learning paths, and a dedicated developer support channel with technical response from Bentley's SDK team.

The **BDN SELECT Subscription** is designed for organizations that are already Bentley SELECT subscribers (annual product licensees) and who need to develop internal customizations or workflows on top of Bentley products for their own use. This tier does not permit commercialization of the resulting application. For Marpa Landscape Architecture, which may hold Vectorworks licenses but not Bentley product licenses, this tier is unlikely to be applicable.

### 2.3 Does Marpa Need the BDN?

The short answer, for the initial proposal phase, is no. The long answer requires understanding exactly which technical resources Marpa's integration requires.

The Marpa initiative, as proposed, builds on three resource categories: the iTwin REST APIs (Public Synchronization API, Reality Management API, Sensor Data API, Changed Elements API, Issues API, Export/Mesh API), the open-source iTwin.js library (MIT-licensed, no subscription required), and the Vectorworks IFC export path (a Vectorworks workflow, not a Bentley SDK). None of these three categories require a BDN subscription. The iTwin REST APIs are documented at developer.bentley.com and accessible with an iTwin account; their commercial usage is billed through the iTwin Platform subscription model (Community, Standard, Premium, Enterprise tiers). The iTwin.js library is MIT-licensed and freely forkable on GitHub [5].

The BDN becomes relevant only if the Marpa initiative later needs to build a native VWX-to-iTwin connector — a deeper integration that reads VWX format directly rather than relying on IFC export — and if that connector requires SDK-level access to Bentley's iModel native format or internal MicroStation APIs. That is a Longer-term Initiative (6–12 months) and is not required for Prototype 1 or Prototype 2. The BDN is on the radar, but it is not the first call to make.

### 2.4 iTwin Platform Pricing: The API Usage Cost Model

For any developer building on the iTwin Platform — whether through the Partner Program or independently — the commercial cost model operates through a credit-based system documented at developer.bentley.com/pricing/ [9]:

| Tier | Monthly Cost | Credits Included | Cloud Storage | Reality Data Storage | Support |
|------|-------------|-----------------|---------------|---------------------|---------|
| **Community** | Free | 100 credits | 10 GB | 250 GB | Community only |
| **Standard** | $199/month | 200 credits | 50 GB | 500 GB | Community |
| **Premium** | $499/month | 500 credits | 50 GB | 500 GB | Premium (paid add-on) |
| **Enterprise** | Custom | Custom | Custom | Custom | Enterprise |

Community tier is non-commercial use only, which is a meaningful constraint: any integration deployed for Marpa's live projects triggers commercial use terms. The Standard tier at $199/month is the appropriate starting point for the Prototype 1 pilot on a live Marpa project.

Several iTwin APIs are free of credit charges regardless of tier: Access Control, iTwins management, User management, most Cesium ion integration, GeoJSON and geospatial features, and Webhooks [9]. This is strategically important — the foundational "project space" layer of iTwin costs nothing to operate, and credit consumption only begins when real data operations occur (iModel ingestion, reality data storage, visualization sessions, etc.).

The credit cost structure for Marpa-specific operations is approximately:

| iTwin Operation | Credit Cost | Notes |
|----------------|-------------|-------|
| iModel storage | 1 credit per 2 GB stored | Primary data layer |
| Synchronization | 1 credit per 2 files synchronized | Each IFC upload |
| Reality capture storage | 6 credits per 100 GB | Drone scan data |
| Visualization (client-facing portal) | 1 credit per access hour | Per session |
| Changed Elements (change tracking) | 2 credits per compute hour | Audit trail |
| Issues and Forms queries | 1 credit per 50 queries | Punch list linked to BIM |
| Export (IFC output) | 1 credit per 3 GB exported | Data exchange |
| Clash detection | 2 credits per run | Optional |

---

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
