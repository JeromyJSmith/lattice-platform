---
title: "iTwin Pricing Notes — Phase A Stub"
type: research
status: draft
historical_only: false
source: "Stub created in Phase 1 Amendment §3.2; awaiting user-sourced notes"
---
# iTwin Pricing Notes

**Status:** draft stub. Phase A artifact. Will be populated with the user's notes.

## Purpose

Capture the pricing landscape for Bentley iTwin Platform offerings — both to validate the OSS-only architectural decision and to inform partner / pilot conversations where pricing might come up.

## Key facts already verified (from existing research)

- iTwin OSS packages (`@itwin/core-geometry`, `@itwin/core-common`, `@itwin/core-quantity`, BIS schemas, `@itwin/core-frontend`) are MIT-licensed and free.
- Bentley cloud services (iTwin Platform, Synchronization API hosting, iModel Hub, Reality Management API) are paid SaaS.
- Cesium ion has a free tier for low-volume use; paid tiers for higher quotas + curated content.
- LATTICE's stance: **OSS-only path**. Zero recurring Bentley spend at the platform level. (See AGENTS.md, CLAUDE.md, ITWIN_MAPPING.md Tier 4.)

## TODO

- [ ] Concrete pricing data for iTwin Platform tiers (where published; many are quote-only)
- [ ] Synchronization API pricing (per-iModel, per-sync, per-element-write?)
- [ ] iModel Hub pricing for read-only vs. read-write briefcase access
- [ ] Reality Management API pricing
- [ ] Cesium ion pricing tiers — free tier limits, hobbyist, commercial
- [ ] Bentley OpenSite+ early-access pricing posture (North America only as of 2026-05; no programmatic access)
- [ ] Comparison table: hypothetical LATTICE-on-OSS vs. LATTICE-on-paid-Bentley monthly cost for a 10-project landscape firm
- [ ] Pricing positioning for our Bentley Partner Program inquiry

## Strategic implications to capture

- The OSS-only stance is a moat: clients pay for LATTICE's value-add, not Bentley's cloud spend
- Cesium ion's free terrain tier may be sufficient for Phase 1 / Phase 2 if usage stays under quota
- If the platform scales beyond Cesium ion free tier, the cost is per-MARPA-project not per-LATTICE-license

## Cross-references

- `meta/ITWIN_MAPPING.md` — Tier 4 skip list (what we deliberately do NOT pay for)
- `AGENTS.md` § cardinal rules (iTwin OSS, no Bentley cloud)
- `meta/harness/docs/research/marpa-business-intelligence.md` — strategy context
- `meta/harness/docs/specs/outreach-templates.md` — partner-program inquiry framing
