# Vectorworks Plugin (C++)

VWSDK plugin that adds the "Generate LATTICE Placeholders" menu command, an MCP socket bridge for in-document automation, and parametric geometry builders.

**Status:** scaffold only. Build pipeline + actual command bodies are open issues (see [`meta/FEATURE_BACKLOG.md`](../meta/FEATURE_BACKLOG.md) § C++ VECTORWORKS PLUGIN).

## Layout

```
src/         PlaceholderCmd.cpp, MCPBridge.cpp, GeometryUtils.cpp, plugin-entry.cpp
include/     Headers
config/      placeholder_rules.json — category → color/height/shape (Claude-editable via MCP)
sdk/         VWSDK files — NOT committed (download from Vectorworks Developer Portal)
CMakeLists.txt
```

## Build (when sources land)

```bash
# 1. Download VW SDK from https://developer.vectorworks.net and unzip into sdk/
# 2. Configure + build
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
```

Mac → `.bundle`, Windows → `.dll`. Both go into the Vectorworks `Plug-Ins/` directory after build.

See [`AGENTS.md`](../AGENTS.md) for the C++ plugin invariants (Plant Style Manager assignment, Mac+Windows targets, MCP bridge over Unix socket).
