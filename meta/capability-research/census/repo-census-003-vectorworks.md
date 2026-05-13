# Repo Census 003 — Vectorworks Corpus

Date: 2026-05-13
Status: first Vectorworks sweep, live GitHub metadata

This census maps the Vectorworks side of LATTICE: Python scripts, VectorScript,
Marionette, worksheet functions, ODBC/data exchange, SDK examples, C++ plugins,
MCP bridges, and plugin helper libraries. The goal is to identify the source
material for the Vectorworks -> Pixeltable data spine.

## Target Workflow

```text
Vectorworks document
-> worksheet/script/plugin extraction
-> object records, classes, layers, styles, geometry, coordinates, and exports
-> Pixeltable normalized rows
-> BIS/IFC/iTwin/DDC workflows downstream
```

## Top Vectorworks Sources

| Row target | Repo | Why it matters |
|---|---|---|
| `vectorworks-developer-scripting-reference` | `Vectorworks/developer-scripting` | Official Python, VectorScript, Marionette, common/function-reference material. |
| `vectorworks-developer-worksheets-reference` | `Vectorworks/developer-worksheets` | Official worksheet functions and object parameter references; critical for fast plant/style/record extraction. |
| `vectorworks-developer-sdk-reference` | `Vectorworks/developer-sdk` | Official SDK development information and version docs. |
| `vectorworks-sdkexamples-cpp-plugin-reference` | `VectorworksDeveloper/SDKExamples` | C++ SDK distribution plus Examples2021-2026 and VectorworksSDK payload. |
| `mako-vectorworks-mcp-sdk-socket-bridge` | `mako-357/vectorworks-mcp` | SDK plugin plus Unix socket MCP architecture for controlling Vectorworks from Claude. |
| `togawamanabu-vectorworks-mcp-doc-rag` | `togawamanabu/vectorworks-mcp` | Documentation/RAG-style MCP surface over Vectorworks material. |
| `dlibrary-python-plugin-helper` | `dietergeerts/dlibrary` | Python helper library for faster Vectorworks plugin development. |
| `vectorworks-python-plugin-basics` | `machistore/basics_of_Vectorworks_plugins` | Small MIT examples for Python plugin basics. |
| `vectorworks-wall-quantity-cpp-plugin` | `h-ikeda/vectorworks-plugin-wall-quantity` | C++ plugin example for quantity calculation, relevant as a shape of geometry/quantity plugin. |
| `vectorworks-odbc-postgres-mysql-references` | `rgm/vectorworks-postgres`, `rgm/vectorworks-mysql` | Old but conceptually relevant ODBC/database-link examples. |

## Watchlist

- `brageiversen/vectorworksPlugins`
- `vpilone/VectorworksPlugins`
- `robertjaniak/change-lighting-type-class`
- `robertjaniak/jands-vista-export`
- `jncogs/3D-Solid-From-Orthographic`
- `onokennote/Ladybug-tool_for_Vectorworks` (GPL-3.0; environmental analysis
  reference only unless isolated)
- `john-salutz/Salutz-Tools-VW` (LGPL-2.1 VectorScript objects)
- `rgm/marionette`
- `marissakfarrell/vectorworks-python-tools`
- `ricardoc1207/*Vectorworks*` Python workflow repos for classes, wall styles,
  and slab styles
- `OpenSpotlightDataExchange` for Spotlight/Lightwright data exchange patterns

## Capability Families To Harvest

- Python `vs.*` scripting and plugin command shape.
- VectorScript and Marionette examples.
- Worksheet object parameters and worksheet formulas.
- Plant/object/class/layer/style extraction patterns.
- C++ SDK menu command, plugin object, resource, and build structure.
- MCP socket bridge architecture for Vectorworks.
- ODBC/database-link patterns for bidirectional record sync.
- Quantity calculation examples and geometry/object traversal.
- Export/data exchange conventions for CSV, Excel, IFC, DXF, and VWX resources.

## Recommended Proof Fixtures

1. Worksheet vocabulary proof:
   parse a small reference manifest from `developer-worksheets` and assert that
   selected worksheet/object parameter names are harvested into deterministic
   rows.
2. Python script shape proof:
   inspect a tiny `vs.*` script fixture and verify it declares allowed calls,
   denied calls, expected output fields, and no secrets/filesystem writes.
3. SDK plugin manifest proof:
   parse `SDKExamples` directory structure and assert examples exist for the
   current target Vectorworks version.
4. MCP bridge manifest proof:
   parse `mako-357/vectorworks-mcp` top-level tree and assert both `mcp-server`
   and `vw-plugin` surfaces exist.
5. ODBC/data-link design proof:
   produce a design-only contract mapping Vectorworks record/class/style fields
   to Pixeltable write targets; no database connection required.

## Not Now

- Do not install the Vectorworks SDK into the repo.
- Do not compile C++ plugins during this census.
- Do not run Vectorworks GUI automation from the harness yet.
- Do not copy unlicensed plugin code directly.
- Do not treat lighting/theatre-specific scripts as landscape-ready; harvest
  patterns only.
- Do not bypass the Vectorworks-only authoring rule.

