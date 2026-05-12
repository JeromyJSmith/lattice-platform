---
title: "iTwin Partner Program — Commercial Terms Layer"
type: research
status: dormant
gate_required: ["Gate A: Accelerator", "Gate B: Partner Program", "Gate C: Developer Subscription", "Gate D: External Funding", "Gate E: Client-Funded Seat"]
gate_status: not_triggered
activation_log: []
doctrine_default: "iTwin OSS self-hosted only — content here is dormant under default doctrine"
vendor: "Bentley Systems"
source: "Extracted from meta/harness/docs/research/bentley-ecosystem-deep-dive-20260508.md § Pillar 1 in Phase 1.5 §5.2"
---

> **Gated content.** Read `_gated/README.md` (top-level dormancy policy) and `_gated/bentley-commercial/README.md` (vendor-specific gate state) before using anything below for architectural purposes. The only permitted use of this file in dormant state is **drafting outreach to Bentley** (see `meta/harness/docs/specs/outreach-templates.md`).

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

