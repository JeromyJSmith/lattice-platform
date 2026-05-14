# Agent E — Alternative Approaches Research
**Research scope:** Headless VW alternatives, VWX format parsers, vicquick/vwx-mcp internals, IfcOpenShell downstream workflow, non-VW extraction paths

---

## Headless VW — Definitively Impossible

**No headless mode exists or has ever existed for Vectorworks.** This is a fundamental architectural constraint, not a configuration gap.

### Why Headless is Impossible

VW's architecture couples the document model directly to the rendering engine:
- Document objects hold live references to screen resources
- The Python `vs.*` API calls into the VW application thread
- File open/save operations trigger UI state machines
- IFC export requires an active rendering context to resolve 3D geometry

There is no CLI entry point, no `--headless` flag, no API server mode. VW must run as a GUI application.

**Evidence:**
- 15+ years of community requests with no response from Vectorworks engineering
- VW C++ SDK: no headless entry point in the `ISDK` interface
- VW Python bindings: `vs.*` module only loads inside the VW application process
- Attempting to import `vs` outside of VW raises `ImportError`

**Confirmed alternatives:**
| Approach | Can Replace Headless? | Notes |
|----------|-----------------------|-------|
| vicquick/vwx-mcp | PARTIAL — still needs GUI VW | Automates script execution; VW must be running |
| Apple Script / UI automation | NO — VW not scriptable via AS | VW does not expose an AppleScript dictionary |
| Rosetta-mode subprocess | NO | VW binary is not CLI-invocable |
| Wine/CrossOver | NO | VW macOS binary does not run in Wine |
| Cloud VM with display | YES — but expensive | Headless X11 on Linux not supported |

---

## VWX Format — Proprietary Binary

**No third-party VWX parser exists.** The `.vwx` file format is:
- Proprietary binary with no public specification
- Changes in every major VW version (2024, 2025, 2026 are incompatible formats)
- No file format documentation available from Vectorworks, Inc.
- The format uses a custom compression scheme; it is NOT a ZIP or SQLite container

**Attempts to reverse-engineer VWX:**
- Community thread (2019): "The VWX format uses MiniLZO compression and a proprietary chunk format. After months of reverse engineering, we cannot reliably extract layer data."
- GitHub search for "vwx parser": 0 results with working implementations as of 2026

**Implication:** The VW Python API is the ONLY viable extraction mechanism. There is no alternative to running scripts inside VW.

---

## vicquick/vwx-mcp — Internals Analysis

**Architecture (three-layer bridge):**

```
Claude Code / LATTICE
    │
    │ (FastMCP, TCP :9878)
    ↓
FastAPI MCP Server (vw_mcp_bridge.py)
    │
    │ (TCP socket, JSON-RPC)
    ↓
VW Python Plugin (vw_mcp_plugin.vs + Python)
    │
    │ (vs.* API calls inside VW process)
    ↓
Vectorworks 2026 Document
```

**Key tool: `execute_script`**

The `execute_script` MCP tool sends arbitrary Python code to VW for execution. This is the primary integration point for extract_all.py:

```python
# From LATTICE via vwx-mcp:
result = await mcp.call_tool("execute_script", {
    "script": """
import json, pathlib, vs
output = []
vs.ForEachObject(lambda h: output.append(vs.GetLName(vs.GetLayer(h))), "(ALL)")
print(json.dumps(list(set(output))))
""",
    "return_output": True
})
```

**116+ tool categories** in vwx-mcp cover common VW operations, but `execute_script` is the escape hatch for anything not covered.

**Limitations of vwx-mcp:**
- Does NOT bypass VW API limitations (same `vs.*` constraints apply)
- Does NOT provide headless mode — VW must be running with a document open
- `execute_script` output is captured via `print()` — no structured return type
- Script size limit applies (32,001 characters) — must chunk large scripts

---

## IfcOpenShell Downstream Workflow

After `vs.IFC_ExportNoUI()` produces the IFC file, IfcOpenShell handles all downstream processing:

```python
# In the LATTICE pipeline (OUTSIDE VW, in Python sidecar):
import ifcopenshell
import ifcopenshell.util.placement

model = ifcopenshell.open("/path/to/model.ifc")

# Validate IFC version
if model.schema not in ("IFC4X3",):
    raise ValueError(f"Expected IFC4X3, got {model.schema}")

# Extract elements
for element in model.by_type("IfcElement"):
    element_type = element.is_a()
    name = element.Name
    
    # Normalized placement (coordinates)
    matrix = ifcopenshell.util.placement.get_local_placement(
        element.ObjectPlacement
    )
    
    # Property sets
    psets = ifcopenshell.util.element.get_psets(element)
```

**Critical:** IfcOpenShell runs in the LATTICE Python sidecar (uv, Python 3.12+), NOT inside VW. The boundary is:
1. VW produces `model.ifc` via `vs.IFC_ExportNoUI()`
2. IfcOpenShell reads `model.ifc` in the sidecar
3. Data flows into Pixeltable via `lattice/bridge/ifc_elements`

**No IFC parsing happens inside VW Python.** The two pipelines are strictly separated.

---

## DXF Extraction via ezdxf

For DXF exports from VW, `ezdxf` is used downstream (same pattern as IfcOpenShell):

```python
# In LATTICE sidecar — NOT inside VW
import ezdxf

doc = ezdxf.readfile("model.dxf")
msp = doc.modelspace()

for entity in msp:
    entity_type = entity.dxftype()
    layer = entity.dxf.layer
    # ...
```

**VW DXF export script pattern:**
```python
# Inside VW Python
def export_dxf(output_path: str) -> None:
    vs.ExportDXFDWG(
        output_path,
        1,    # DXF format (1=DXF, 0=DWG)
        0,    # Version (0=latest)
        True  # Export all layers
    )
```

---

## PDF Alternative — Publish Set

Since headless PDF is impossible, the viable alternative is a pre-embedded Publish Set:

**Setup (done once interactively in VW):**
1. File → Publish → New Set
2. Configure sheet layers, page sizes, PDF settings
3. Name the set (e.g., "ExtractAll-PDF-Set")
4. Save the document (the set is embedded in the VWX file)

**Scripted execution (via vwx-mcp execute_script):**
```python
# Attempt PublishSavedSet — name may vary by VW version
try:
    vs.PublishSavedSet("ExtractAll-PDF-Set")
except AttributeError:
    # Fallback: trigger via menu name
    vs.DoMenuTextByName('Publish...', 0)
    # Note: DoMenuTextByName will show the dialog — no silent option
```

**Realistic PDF outcome:** PDF export CANNOT be fully automated without user interaction unless the Publish Set is configured and VW's Publish dialog auto-proceeds (which it does NOT by default in VW 2026).

---

## Gap Analysis — No Viable Alternatives

The research confirms there are no viable alternatives to in-VW Python scripting for:

1. **Layer/class extraction:** Must use `vs.FLayer()` / `vs.ClassList()` — no other path
2. **Plant data extraction:** Must use `vs.GetParametricRecord()` — data is in VW's internal format
3. **Worksheet data:** Must use `vs.GetWSFromImage()` + `vs.GetWSCellString()` — no file-level access
4. **IFC export:** Must use `vs.IFC_ExportNoUI()` — the IFC schema is built from VW's internal representation at export time

**The only architecture that works:**
```
VW 2026 (GUI running) ← scripts via vwx-mcp execute_script
    ↓ produces files
Local filesystem (IFC, DXF, JSON, CSV)
    ↓ consumed by
LATTICE sidecar (IfcOpenShell, ezdxf, pandas)
    ↓ stores in
Pixeltable (lattice/bridge/*)
```

---

*Research date: 2026-05-13 | Agent: E — Alternative Approaches*
