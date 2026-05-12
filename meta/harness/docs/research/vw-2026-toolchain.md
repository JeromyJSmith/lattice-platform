---
title: "Vectorworks 2026 Toolchain — Verified Capability + SDK Notes"
type: research
status: reference
historical_only: false
source: "Synthesized from MARPA_DevStack_Research_20260508/vectorworks-2026-sdk-print-guide.md + marpa-research-report-v2-20260508-verified.md (verified against VW2026 docs + buildingSMART certification database)"
---
# Vectorworks 2026 Toolchain — Verified

The technical-stack facts that constrain LATTICE's VW bridge work. This is the verified version — every claim here is sourced from `marpa-research-report-v2-20260508-verified.md` or `vectorworks-2026-sdk-print-guide.md` (both in the research/specs trees).

## Vectorworks Landmark 2026 — what it gives us

**Authoring capabilities (industry-leading for landscape):**

| Capability | Status | Strategic value for LATTICE |
|---|---|---|
| Plant Style Manager (NEW 2026) | Spreadsheet-style batch editing across hundreds of plant objects | Canonical control point — all instances update globally. Already a cardinal rule. |
| `Copy External Data` command (NEW 2026) | Live pricing + specification pull from partner nursery databases | Cost-estimation pipeline gets real market data, not stub values |
| Rebuilt Existing Tree tool (NEW 2026) | 8-directional canopy spread geometry via Maxon Plant engine | Replaces symmetric idealized crowns with organic canopy variability |
| Sustainability Dashboard (NEW 2026) | Real-time aggregation: Embodied Carbon, Urban Greening Factor, Biomass Density, Biodiversity Net Gain | Source feed for the LATTICE ecological-metrics export |
| One Click LCA integration (Update 1) | Carbon-footprint reporting integration | Pipe-through to client-facing dashboards |
| Esri ArcGIS live binding | Direct streaming of feature services (parcels, roads, utilities, tree surveys) | Vectorworks and iTwin both speak ArcGIS — the GIS layer is a coordination backbone |
| Bidirectional GIS publish | Geolocated VW models → ArcGIS Web Scenes | Alternative review path for stakeholders without iTwin access |

## IFC certification — verified

- **IFC2x3 Coordination View 2.0 — Architecture:** import and export certified
- **IFC4 Reference View 1.2 — Architectural Reference Exchange:** export certified 2019 (first architectural software to achieve IFC4 export certification); import certified July 2023
- **IFC4.3:** import/export supported in the software (per Help 2026 docs) but **formal buildingSMART certification not publicly confirmed as of 2026-05**.

Citations live in `marpa-research-report-v2-20260508-verified.md` § 1.3 (BSI + VW-IFC-cert).

## IFC export limitations that matter for LATTICE

Certification ≠ completeness. **VW's landscape-specific objects do NOT map to standard IFC schema:**

- Existing Trees / Plants / Grade Objects / Irrigation components are NOT part of standard IFC schema for buildings
- IFC4.3 adds `IfcGeographicElement` with `Pset_VegetationCommon` (2 properties: BotanicalName, LocalName) — professionally unusable
- A landscape architect exporting VW Landmark to IFC **will lose**: species taxonomy, canopy spread, health status, planting date, maintenance schedule, irrigation parameters, ecological function tags

**LATTICE's role:** the sidecar JSON normalization layer that captures everything IFC drops. CityGML 3.0 Vegetation ADE-compatible. (See `marpa-business-intelligence.md` § strategic frame.)

## SDK build prerequisites (verified)

| Platform | Requirement |
|---|---|
| Windows | Visual Studio 2022 version 17.12, toolset v143 |
| macOS | Xcode 16.2 |
| Both | `VectorworksDeveloper/SDKExamples` checkout; start from `ObjectExample` per VW staff guidance |

**Setup path (verified):**

1. Install Vectorworks 2026 + the matching build tools for the target platform.
2. Clone or download `VectorworksDeveloper/SDKExamples`. Begin with `ObjectExample` (NOT a blank plugin project).
3. First Windows build: `Debug | x64` so symbols are available and breakpoint behavior is sane.
4. Install the generated `.vlb` and `.vwr` outputs by shortcut or copy into the user-specific Vectorworks Plug-ins path. Restart Vectorworks to force a fresh scan.

## Satellite credentials requirement

VW 2026 requires encrypted / obfuscated script plug-ins and SDK plug-ins to include a **satellite credentials file** identifying the developer. The public docs confirm the requirement but do NOT expose a fully documented self-serve file-authoring workflow.

**LATTICE stance:** Treat credentials setup as a packaging step tied to official Vectorworks developer documentation and support channels. **Do NOT invent a custom file format.** The requirement does NOT apply to open-source VectorScript or Python scripts — encryption / obfuscation are opt-in. LATTICE's VW plugin path is C++ (vw-plugin/) + Python `vs.*` (vw-python/); the C++ side needs credentials, the Python side does not.

## What Vectorworks deliberately does NOT do

Vectorworks Landmark is **explicitly a design-and-documentation tool**, not an operations platform — VW's own official digital-twin position confirms this. Within the Nemetschek Group, the designated operations platform is **dTwin**, but dTwin is built-asset/facility-focused:
- Ingests outdoor data (laser scans, GIS context) for surrounding context
- Managed-object semantics concentrate on commercial real estate, industrial buildings, HVAC / lighting / security systems
- **No object types for vegetation management, planting lifecycle, or ecological monitoring as active operational assets**

This gap persists **within Vectorworks' own parent-company ecosystem**. Strategic implication: LATTICE / MARPA fills a gap not just for the broader iTwin platform but for Nemetschek itself.

## TODO — open items requiring user-sourced content

- [ ] Confirmed VW 2026 release date + minor-version cadence
- [ ] Plant Style Manager API surface for vwx-mcp invocation (cardinal control point)
- [ ] vwx-mcp installation + version pinning
- [ ] vicquick / mako-357 / togawamanabu VW-MCP comparison (briefly captured in `meta/harness/docs/specs/meta-harness-specification.md`; needs canonical reference here)
- [ ] DXF export schema differences between VW 2024 and 2026 (relevant for `ddc/converters/` Linux fallback)
- [ ] IFC4.3 export edge cases on VW 2026 (specifically `IfcPlant` placement matrix conventions)
- [ ] LandXML export from VW Landmark (if available) and how it maps to iTwin LandXML connector
- [ ] Known bugs / workarounds for current VW 2026 build
- [ ] Python `vs.*` API additions or removals vs. VW 2024

## Cross-references

- `marpa-research-report-v2-20260508-verified.md` § 1 (Vectorworks Landmark 2026 — Verified Capability)
- `meta/harness/docs/specs/meta-harness-specification.md` — vwx-mcp + ifcMCP + plugin architecture
- `meta/ITWIN_MAPPING.md` — which iTwin pieces consume the VW IFC4.3 export
- `vw-plugin/` (in-repo) — the C++ plugin path that uses this SDK
- `vw-python/` (in-repo) — the Python `vs.*` API path
- `meta/harness/docs/research/marpa-business-intelligence.md` — strategic frame
- `meta/harness/docs/research/_gated/README.md` — pricing-side framing is gated commercial content; consult only via the dormancy policy
