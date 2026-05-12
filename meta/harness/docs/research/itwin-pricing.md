---
title: "iTwin Pricing — Verified Tiers and Strategic Implications"
type: research
status: reference
historical_only: false
source: "bentley-ecosystem-deep-dive-20260508.md § Pillar 2.4 (verified against developer.bentley.com/pricing 2026-05-08)"
---
# iTwin Pricing — Verified

Pricing structure for the **commercial / API-usage / accelerator** layers of the iTwin ecosystem. The free / OSS layer is unchanged and well-known.

## Free / OSS layer (zero recurring cost)

| Layer | Status |
|---|---|
| `@itwin/core-geometry`, `@itwin/core-common`, `@itwin/core-quantity`, `@itwin/core-frontend` | MIT-licensed; free for any use |
| BIS schemas | Open source; free |
| iTwin REST APIs | Public; usage-metered per the table below |
| iTwin.js library | MIT; free |
| Cesium 3D Tiles standard | OGC community standard; non-proprietary |
| Bentley iTwin Partner Program (Standard tier) | Free to join; year-round acceptance |

**LATTICE stance:** OSS-only path at the platform layer. Zero recurring Bentley spend on core LATTICE infrastructure. (See `AGENTS.md`, `CLAUDE.md`, `ITWIN_MAPPING.md` Tier 4 skip list.)

## iTwin Platform API pricing tiers (verified 2026-05-08)

Source: `developer.bentley.com/pricing/` (verified in `bentley-ecosystem-deep-dive-20260508.md` § 2.4).

| Tier | Monthly Cost | Credits Included | Cloud Storage | Reality Data Storage | Support |
|---|---|---|---|---|---|
| **Community** | Free | 100 credits | 10 GB | 250 GB | Community only |
| **Standard** | $199/month | 200 credits | 50 GB | 500 GB | Community |
| **Premium** | $499/month | 500 credits | 50 GB | 500 GB | Premium (paid add-on) |
| **Enterprise** | Custom | Custom | Custom | Custom | Enterprise |

### Important constraint

**Community tier is non-commercial use only.** Any LATTICE / MARPA integration deployed for live MARPA projects triggers commercial-use terms. The **Standard tier at $199/month** is the appropriate starting point for the Prototype 1 pilot on a live MARPA project.

### APIs that are free regardless of tier

The following iTwin APIs consume **zero credits** at any tier:
- Access Control
- iTwins management
- User management
- Most Cesium ion integration
- GeoJSON / geospatial features
- Webhooks

**Strategic implication:** the foundational "project space" layer of iTwin costs nothing to operate. Credit consumption only begins when real data operations occur (iModel ingestion, reality data storage, visualization sessions).

## Credit cost structure for MARPA-specific operations

| iTwin Operation | Credit Cost | Notes for LATTICE |
|---|---|---|
| iModel storage | 1 credit per 2 GB stored | Primary data layer |
| Synchronization | 1 credit per 2 files synchronized | Each IFC upload from VW |
| Reality capture storage | 6 credits per 100 GB | Drone scan data |
| Visualization (client-facing portal) | 1 credit per access hour | Per browser session |

### Worked example — 10-project landscape firm, Standard tier

Hypothetical monthly load: 10 active projects × 5 GB iModel + 20 IFC syncs + 50 GB drone capture + 200 client portal hours = ~5+10+3+200 ≈ 218 credits/month.

→ **Standard tier (200 credits / $199) is borderline; Premium ($499 / 500 credits) is the safe envelope** for any firm running >5 active projects with reality capture. LATTICE's stance is that the firm pays Bentley for their tier, never LATTICE — preserves margin and decouples our recurring revenue from Bentley's pricing changes.

## iTwin Activate accelerator

| Term | Value |
|---|---|
| Investment vehicle | SAFE note |
| Max investment | $250,000 (Activate program entry) |
| Larger fund range | $250K–$5M (iTwin Ventures pipeline; Activate is the first filter) |
| Parent fund | iTwin Ventures, $100M committed over 5 years |
| Equity dilution | NOT disclosed publicly. Specific terms (valuation cap, discount rate, MFN) negotiated bilaterally per `bentley-ecosystem-deep-dive-20260508.md` § 4 assumption 2 |
| Cohort cadence | Annual themed cohort; 5 cohorts complete since 2023 launch |
| Cohort duration | 20 weeks |
| Application window | Cohort-themed; 2026 theme not yet announced as of 2026-05 |
| Benefits during cohort | Community-tier credit constraints **waived**; build at production scale for cohort duration |

## Bentley Developer Network (BDN)

| Tier | Use case | Pricing |
|---|---|---|
| Commercial Subscription | Developers building products to sell | **NOT publicly disclosed** — quote-only |
| SELECT Subscription | Bentley licensees building internally | **NOT publicly disclosed** — quote-only |

**LATTICE stance:** BDN is **NOT required** for iTwin REST API development (the iTwin.js library is MIT, the APIs are publicly accessible). BDN becomes relevant only if we need SDK-level access to non-iTwin Bentley products (MicroStation, OpenRoads, etc.). Per the cardinal rule, those are out of scope — LATTICE never depends on them.

## Cesium ion pricing (post-Bentley-acquisition)

Cesium ion remains a separate billing surface even after the Sept 2024 acquisition. The free tier covers low-volume terrain + curated content. Cesium ion APIs are listed as "most" free of iTwin credit charges — meaning combining iTwin Platform APIs with Cesium ion stays mostly within the iTwin tier credit budget.

**LATTICE stance:** Cesium ion's free tier is sufficient for Phase 1 and likely Phase 2. Costs scale only when usage exceeds the free quota or when curated commercial datasets are required.

## Bentley OpenSite+ AI (early access)

- North America only as of 2026-05.
- No public API.
- Pricing not disclosed (early-access program).

**LATTICE stance:** OpenSite+ is an **inspiration**, not an integration target. (Already a cardinal rule.) We build the equivalent capability for landscape on public iTwin APIs + Python ML.

## Strategic implications

- The **$199/month Standard tier** is the canonical Phase-1 operating cost for one live MARPA project. Scales linearly with credits, not with seats.
- **No upfront platform license fee.** Marpa pays for compute, not for software.
- **OSS-only stance is a moat:** clients pay LATTICE for value-add, never for Bentley cloud spend. Pricing changes at Bentley don't break LATTICE's revenue model.
- **Activate cohort = $250K non-dilutive runway** (favorable SAFE terms TBD) + production-scale platform access for 20 weeks + direct relationships with the iTwin Ventures pipeline.
- **Year-round Partner Program acceptance** means we can start the Envision phase **this week** and have the Design-phase conversations before serious development begins.

## Open items (need direct Bentley contact)

- BDN annual fees — request via `bentley.com/support/software-developers/`.
- Activate 2026 cohort theme + application window — monitor `bentley.com/software/itwin-activate/` for announcement.
- SAFE term sheet — only disclosed bilaterally after Activate acceptance.

## Cross-references

- `bentley-ecosystem-deep-dive-20260508.md` — full Partner Program / BDN / Activate / developer-channel deep dive
- `marpa-research-report-v2-20260508-verified.md` — claim-verified strategic context
- `marpa-business-intelligence.md` — strategic frame using these pricing facts
- `outreach-templates.md` — partner-program inquiry language (cites Standard tier appropriately)
- `meta/ITWIN_MAPPING.md` — Tier 4 skip list (what we deliberately do NOT pay for)
- `AGENTS.md` § cardinal rules (iTwin OSS, no Bentley cloud)
