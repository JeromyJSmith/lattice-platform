---
title: "Cesium Commercial — Gate State + Self-Hosting Doctrine"
type: gating-policy
status: dormant
gate_required: ["Gate A: Accelerator", "Gate B: Partner Program", "Gate C: Developer Subscription", "Gate D: External Funding", "Gate E: Client-Funded Seat"]
gate_status: not_triggered
activation_log: []
doctrine_default: "Self-host Cesium OSS components wherever possible — Cesium ion paid SaaS is gated"
vendor: "Cesium (Bentley subsidiary since Sept 2024)"
source: "Phase 1.5 amendment (this folder created 2026-05-12)"
---
# Cesium Commercial — Gate State + Self-Hosting Doctrine

> **Read `_gated/README.md` first.** This folder is dormant by default per the five-gate policy.

## Vendor

**Cesium / Bentley.** Cesium was acquired by Bentley Systems in September 2024 (Patrick Cozzi → Bentley CPO) but remains a **separate billing surface** for Cesium ion. The OSS components remain MIT / Apache and are not gated.

## What is NOT gated (stays in regular architecture)

The following Cesium components are **fully aligned with LATTICE doctrine** and remain in the regular architecture under `src/**`, `pixeltable/service/**`, etc.:

- **CesiumJS library** — open-source 3D globe / mapping engine; used freely for the `/globe` route and the Cesium-side rendering surface
- **Cesium 3D Tiles standard** — OGC community standard (non-proprietary); used freely for tiled streaming of 3D geometry
- **Self-hosted terrain serving** — terrain tiles served from LATTICE infrastructure (e.g., quantized-mesh or 3D Tiles terrain) directly from disk / our own static CDN
- **Self-hosted imagery serving** — base imagery (raster tiles) served from open sources (OpenStreetMap, public satellite imagery, MapTiler self-host, etc.)
- **Self-hosted 3D Tiles asset serving** — point clouds / meshes / models served as 3D Tiles from LATTICE storage
- **`@deck.gl/cesium`** integration package — open source; used freely

## What IS gated (lives in this folder)

The following Cesium ion offerings are **commercial SaaS** and are dormant under default doctrine:

- **Cesium ion SaaS API access** (anything requiring an API key against Cesium's hosted ion cloud)
- **Cesium ion hosted asset serving** (when ion hosts our assets and serves them on our behalf)
- **Cesium ion premium curated commercial datasets** (paid imagery, paid terrain, paid 3D building tile sets)
- **Any feature that requires an ion API key against Cesium's hosted SaaS** — even if our usage stays under the free quota, dependency on the hosted endpoint is a gated surface

The free Cesium ion tier *technically* has zero recurring cost, but architecting against the hosted endpoint creates a dependency on a SaaS surface that may be re-priced or rate-limited. The doctrine response is: **self-host the equivalent capability from OSS**, and treat the ion-hosted path as a gated optimization for when a real gate fires.

## Self-hosting expansion note

Self-hosting Cesium OSS components requires **more setup work** than using Cesium ion SaaS:

- Terrain server (e.g., serve quantized-mesh tiles from our own static CDN; or use a self-hosted terrain pipeline)
- Imagery server (raster tile pyramid generation + serving)
- 3D Tiles server (tile asset bundling + range-request-friendly static serving)
- Asset pipeline (3D model → 3D Tiles conversion; PotreeConverter already covers point clouds)

**This setup work is mandatory per doctrine.** The shorter ion-SaaS path is forbidden by default. The cost is paid in upfront engineering work rather than recurring SaaS spend — that trade matches the OSS-self-hosted doctrine exactly.

## Gate status table

| Gate | Status | Last evaluated | Notes |
|---|---|---|---|
| Gate A: Accelerator Cohort Acceptance | `not_triggered` | 2026-05-12 | If 2026 iTwin Activate cohort theme aligns with Cesium 3D Tiles (as Cohort 5 did), Activate gates would activate both Bentley and Cesium folders simultaneously. |
| Gate B: Partner Program Acceptance | `not_triggered` | 2026-05-12 | Cesium has its own community / partner relationships. Application path TBD. |
| Gate C: Developer Subscription | `not_triggered` | 2026-05-12 | No Cesium ion paid subscription. Free tier could be used as a backstop only when self-hosting is genuinely infeasible — see "Open work" below. |
| Gate D: External Funding | `not_triggered` | 2026-05-12 | LATTICE has no external funding. |
| Gate E: Client-Funded Seat | `not_triggered` | 2026-05-12 | No client currently funds a Cesium ion seat that LATTICE operates on. |

## Activation log

```yaml
# Same YAML shape as bentley-commercial/README.md activation_log.
activation_log: []
```

## Contents inventory

| File | What it contains | Status |
|---|---|---|
| `cesium-ion-paid-tiers.md` | STUB — paid tier table, asset hosting costs, terrain bundle costs, premium imagery costs. Populated when/if Gate A or D fires for Cesium, or when a client engagement requires Cesium ion paid access (Gate E). | stub |

## Cross-references

- `_gated/README.md` — top-level five-gate policy + activation procedure
- `_gated/bentley-commercial/README.md` — paired vendor (Cesium is a Bentley subsidiary; accelerator gates may activate both simultaneously)
- `meta/harness/docs/research/marpa-research-report-v2-20260508-verified.md` — strategic context for the Cesium acquisition and its renderer-strategy implications (still aligned with the OSS components which remain non-gated)
- `meta/CESIUM_SETUP.md` (if present in the repo) — non-gated Cesium integration guide that uses CesiumJS + 3D Tiles + self-hosted assets

## Open work (to be issue-tracked during Phase B / Phase 2 sequencing)

- **Self-hosting setup work.** File a GH issue when Phase B sequencing begins: "Stand up self-hosted terrain + imagery + 3D Tiles serving for the `/globe` route — replaces any default-path reliance on Cesium ion hosted endpoints." Currently a TODO; promote to a tracked issue when Phase B starts.
- **OSS Cesium ion alternative evaluation.** Research and document the OSS terrain-server stack (e.g., cesium-terrain-builder, planetiler, Felt's terrain workflow) and pick a default. Currently undefined; defer to Phase B.
- **Ion-API-key audit at codebase level.** Once any Cesium integration code lands under `src/`, audit that no code path requires a Cesium ion API key in the default architecture. Any required key path violates this doctrine and must be either moved behind a gate-checked feature flag or replaced with self-hosted equivalent.
