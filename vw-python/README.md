# Vectorworks Python API (`vs.*`) — Reference and Patterns

Vectorworks 2026+ ships a Python API at `vs.*` that runs inside the VW process. It's a thinner alternative to the C++ plugin for read-mostly scripts.

**Reference scope:** the `vs.*` API. The local knowledge stack indexes this at scope `vw-dev-scripting` — query with `knowledge_search` before guessing.

## Examples

| File | What it shows |
|---|---|
| [`examples/list_layers.py`](examples/list_layers.py) | Enumerate design layers and their visibility |
| [`examples/read_plant_records.py`](examples/read_plant_records.py) | Walk all Plant Style instances and dump records to JSON |
| [`examples/export_ifc_trigger.py`](examples/export_ifc_trigger.py) | Trigger IFC4.3 export from a script, no UI prompts |

## Running

Open Vectorworks → `Tools → Plug-Ins → Run Script…` → pick a file. Or wire via the `vicquick/vwx-mcp` MCP server (see [`AGENTS.md`](../AGENTS.md) § Vectorworks Integration).

## Differences from the C++ plugin

| Concern | Python `vs.*` | C++ Plugin |
|---|---|---|
| Performance | Slower (script-evaluated) | Native, fast |
| Geometry creation | Limited primitives | Full geometry API |
| Distribution | Just a `.py` file | Compiled `.bundle`/`.dll` |
| Use case | Read, report, one-shot scripts | Menu commands, batch geometry, MCP bridge |

Use Python for exploration and one-shots. Promote to C++ when you need a menu command or fast batch geometry.
