---
title: "Cesium ion Paid Tiers — Pricing + Capability Stub"
type: research
status: dormant
gate_required: ["Gate A: Accelerator", "Gate B: Partner Program", "Gate C: Developer Subscription", "Gate D: External Funding", "Gate E: Client-Funded Seat"]
gate_status: not_triggered
activation_log: []
doctrine_default: "Self-host Cesium OSS components wherever possible — this paid-tier content is dormant"
vendor: "Cesium (Bentley subsidiary since Sept 2024)"
source: "Stub created in Phase 1.5 §5.3; populate when a gate fires or when a client engagement requires paid ion access"
---
# Cesium ion Paid Tiers — Stub

> **Gated content.** Read `_gated/README.md` (top-level dormancy policy) and `_gated/cesium-commercial/README.md` (vendor-specific gate state + self-hosting doctrine) before using anything here for architectural purposes.

This file exists so the `_gated/cesium-commercial/` structure is complete and the gate state table in the parent README can reference it. The Phase 1 research trove did not include detailed Cesium ion paid-tier pricing.

## Why this is a stub

LATTICE doctrine defaults to **self-hosting** the Cesium OSS components (CesiumJS, Cesium 3D Tiles standard, terrain / imagery / 3D Tiles serving from our own storage). The Cesium ion paid SaaS path is **not** the default — it is one possible alternative when a real gate fires.

Until a gate fires, populating this file with pricing detail would architect against commercial terms we have explicitly chosen not to adopt. That is exactly the failure mode the `_gated/` policy exists to prevent.

## What this file will contain when activated

When/if Gate A (Accelerator), D (External Funding), or E (Client-Funded Seat) fires for Cesium, populate this file with:

- **Cesium ion paid tier table** — at minimum: free tier + Commercial tier + Enterprise tier with monthly cost, asset-hosting quota, asset-streaming quota, support level
- **Asset-hosting costs** — cost per GB-month for hosted assets (terrain bundles, imagery, 3D Tiles)
- **Terrain bundle costs** — pricing for premium terrain datasets (e.g., Cesium World Terrain, premium DEM packages)
- **Premium imagery costs** — pricing for premium imagery datasets (e.g., Maxar, Vivid)
- **Premium 3D Tiles costs** — pricing for hosted 3D Tiles sets (e.g., Cesium OSM Buildings, Cesium Photorealistic 3D Tiles)
- **API request quotas** — per-tier rate limits and overage pricing
- **Worked example** — what a typical MARPA project + supporting infrastructure costs per month at the chosen tier
- **Comparison to self-hosted equivalent** — engineering hours to stand up the equivalent self-hosted stack vs. monthly SaaS spend

All sourced from `cesium.com/pricing/` (or wherever Cesium publishes paid-tier terms at activation time). Per the Capability Harvest Protocol, every claim cites a primary source.

## What to do RIGHT NOW

Nothing. This stub exists so the directory structure is complete. Do not architect against Cesium ion paid tiers; use the self-hosted path described in `_gated/cesium-commercial/README.md` § "Self-hosting expansion note".

If you arrived here looking for guidance on which Cesium components to use in default LATTICE architecture, the answer is in `_gated/cesium-commercial/README.md` § "What is NOT gated (stays in regular architecture)".
