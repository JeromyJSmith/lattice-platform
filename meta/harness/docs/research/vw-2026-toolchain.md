---
title: "Vectorworks 2026 Toolchain Notes — Phase A"
type: research
status: draft
historical_only: false
source: "MARPA_DevStack_Research_20260508/vectorworks-2026-sdk-print-guide.md + Phase 1 Amendment §3.2 stub for additional content"
---
# Vectorworks 2026 Toolchain Notes

**Status:** partial — seeded from `vectorworks-2026-sdk-print-guide.md` (canonical research). Phase A stub awaits user-sourced additions for the items marked TODO.

## Build prerequisites (verified from upstream)

| Platform | Requirement |
|---|---|
| Windows | Visual Studio 2022 version 17.12, toolset v143 |
| macOS | Xcode 16.2 |
| Both | `VectorworksDeveloper/SDKExamples` checkout; start from `ObjectExample` per VW staff guidance |

## Setup path (verified)

1. Install Vectorworks 2026 + the matching build tools for the target platform.
2. Clone or download `VectorworksDeveloper/SDKExamples`. Begin with `ObjectExample` rather than a blank plugin project.
3. First Windows build: `Debug | x64` so symbols are available and breakpoint behavior is sane.
4. Install the generated `.vlb` and `.vwr` outputs by shortcut or copy into the user-specific Vectorworks Plug-ins path, then restart Vectorworks to force a fresh scan.

## Satellite credentials requirement

VW 2026 requires encrypted / obfuscated script plug-ins and SDK plug-ins to include a satellite credentials file identifying the developer. The public docs confirm the requirement but do not expose a fully documented self-serve file-authoring workflow.

**LATTICE stance:** treat credentials setup as a packaging step tied to official Vectorworks developer documentation and support channels — do NOT invent a custom file format. The requirement does NOT apply to open-source VectorScript or Python scripts; encryption / obfuscation are opt-in.

## TODO (Phase A additions)

- [ ] Confirmed VW 2026 release date + minor-version cadence
- [ ] VW Plant Style Manager API surface (canonical control point per AGENTS.md)
- [ ] vwx-mcp installation + version pinning notes
- [ ] vicquick / mako-357 / togawamanabu VW-MCP comparison (briefly captured in `meta-harness-specification.md`; needs canonical reference here)
- [ ] DXF export schema differences between VW 2024 and 2026 (relevant for `ddc/converters/` Linux fallback path)
- [ ] IFC4.3 export edge cases observed on VW 2026 (specifically `IfcPlant` placement matrix conventions)
- [ ] LandXML export (if available in VW 2026 Landmark) and how it maps to iTwin LandXML connector
- [ ] Known bugs / workarounds for current VW 2026 build
- [ ] Python `vs.*` API additions or removals vs. VW 2024

## Cross-references

- `meta/harness/docs/specs/meta-harness-specification.md` § "Vectorworks Integration" — vwx-mcp + ifcMCP + plugin architecture
- `meta/ITWIN_MAPPING.md` — which iTwin pieces consume the VW IFC4.3 export
- `vw-plugin/` — the C++ plugin path that uses this SDK
- `vw-python/` — the Python `vs.*` API path
