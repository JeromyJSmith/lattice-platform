---
title: "Bentley Developer Network (BDN) — Commercial / SELECT Subscription Tiers + iTwin Platform Pricing"
type: research
status: dormant
gate_required: ["Gate A: Accelerator", "Gate B: Partner Program", "Gate C: Developer Subscription", "Gate D: External Funding", "Gate E: Client-Funded Seat"]
gate_status: not_triggered
activation_log: []
doctrine_default: "iTwin OSS self-hosted only — content here is dormant under default doctrine"
vendor: "Bentley Systems"
source: "Extracted from meta/harness/docs/research/bentley-ecosystem-deep-dive-20260508.md § Pillar 2 in Phase 1.5 §5.2"
---

> **Gated content.** Read `_gated/README.md` (top-level dormancy policy) and `_gated/bentley-commercial/README.md` (vendor-specific gate state) before using anything below for architectural purposes. The only permitted use of this file in dormant state is **drafting outreach to Bentley** (see `meta/harness/docs/specs/outreach-templates.md`).

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


---

## LATTICE-specific clarification (§5.2 of Phase 1.5 amendment)

**BDN is NOT required for iTwin REST API development.** It becomes relevant only if scope expands to non-iTwin Bentley products (MicroStation, OpenRoads, etc.), which is currently **forbidden by the cardinal rule** in `AGENTS.md` § cardinal rules.

Practical implication: LATTICE never opens a BDN subscription under default doctrine. The iTwin REST APIs + the MIT-licensed `@itwin/core-*` packages cover every iTwin integration LATTICE needs. The BDN gate state can remain `not_triggered` indefinitely without blocking platform work.
