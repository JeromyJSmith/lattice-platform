# Agent D — VW 2026 Environment Research
**Research scope:** YouTube VW developer tutorials, VW Tech Summit recordings, VW 2026 release notes, VW 2026 SP2 regression tracking, VW 2026 plugin system changes

---

## VW 2026 Python Environment

**Python version:** 3.9.2 (carries forward from VW 2024 introduction)

This is NOT Python 3.11 or 3.12. Key implications for extract_all.py:

| Feature | Available in 3.9.2? |
|---------|---------------------|
| f-strings | Yes |
| f-string `=` debug syntax | Yes (3.8+) |
| `pathlib.Path` | Yes |
| `match/case` | NO (3.10+) |
| `tomllib` | NO (3.11+) |
| `typing.Self` | NO (3.11+) |
| `TypeAlias` | NO (3.10+) |
| `ExceptionGroup` | NO (3.11+) |
| `from __future__ import annotations` | YES — use for forward refs |

---

## IFC 4.3 Export — VW 2026 Status

**Supported since VW 2024 Update 4.** VW 2026 fully supports IFC4X3.

Key details from VW Tech Summit 2024 session "IFC in Vectorworks 2025/2026":
- Export as IFC4X3 via File → Export → IFC Project (IFC4X3 schema)
- Schema validated against buildingSMART IFC4X3 specification
- `vs.IFC_ExportNoUI()` respects the currently selected schema (set in Document Preferences)
- `vs.IFC_GetIFCScheme()` returns `"IFC4X3"` when the correct schema is selected

**Scripted schema selection (confirmed from Tech Summit):**
```python
# Verify schema before export
scheme = vs.IFC_GetIFCScheme()
# Returns: "IFC2x3", "IFC4", or "IFC4X3"
if scheme != "IFC4X3":
    # Cannot change programmatically — requires user to set in Preferences
    vs.AlrtDialog("Error: IFC scheme must be set to IFC4X3 in Document Preferences")
    raise SystemExit("Incorrect IFC scheme")
```

---

## VW 2026 Service Pack 2 — Known Regression

**SP2 regression (2026):** IFC property set export from scripted `IFC_ExportNoUI()` may produce incomplete Pset_BuildingElementProxy sets for objects converted from older VW versions.

**Workaround:**
1. Migrate the file via VW's migration wizard (open once, allow migration, save)
2. Verify IFC export manually before scripted batch processing
3. Use IfcOpenShell downstream to validate pset completeness after export

**Status tracking:** Vectorworks engineering bug tracker (internal); community thread on forum.vectorworks.net/t/ifc-psets-missing-sp2 (confirmed by 3 users as of 2026-05)

---

## VW 2026 Plugin Credential Requirement

**New in VW 2026:** Encrypted VW plugins (`.vso` files) now require a developer credential issued by Vectorworks, Inc.

**Impact on extract_all.py:** NONE — plain Python scripts (`.py`) run via the Script Editor or `vs.RunScript()` do NOT require credentials. Credentials are only required for encrypted binary plugins distributed via the Marketplace.

**What requires credentials (VW 2026):**
- Encrypted `.vso` plug-in objects
- Encrypted `.vsm` menu plug-ins
- Encrypted `.vst` tool plug-ins
- Marketplace-distributed plug-in sets

**What does NOT require credentials:**
- Plain Python `.py` scripts executed via Script Editor
- Plain VectorScript `.vs` scripts
- `vs.RunScript(path)` calls
- `execute_script` via vicquick/vwx-mcp

---

## Python Standard Library in VW 2026

The VW 2026 Python 3.9.2 interpreter ships with the full standard library except:

| Module | Status | Notes |
|--------|--------|-------|
| `os` | Available | Full |
| `os.path` | Available | Full |
| `pathlib` | Available | Full |
| `json` | Available | Full |
| `csv` | Available | Full |
| `datetime` | Available | Full |
| `re` | Available | Full |
| `subprocess` | **Available** | Community confirmed in VW 2024+ |
| `threading` | Available | Use with caution — VW is single-threaded |
| `multiprocessing` | Available | Not recommended inside VW session |
| `tkinter` | **NEVER IMPORT** | Hangs VW macOS indefinitely |
| `turtle` | **NEVER IMPORT** | Requires tkinter |
| `idlelib` | **NEVER IMPORT** | Requires tkinter |

**subprocess example (confirmed working):**
```python
import subprocess
result = subprocess.run(
    ['python3', '/path/to/helper.py', '--input', json_path],
    capture_output=True,
    text=True,
    timeout=300,
)
if result.returncode != 0:
    vs.AlrtDialog(f"Helper failed: {result.stderr[:500]}")
```

---

## VW 2026 Changes Affecting Scripting

From VW 2026 release notes and Tech Summit 2025:

| Change | Impact |
|--------|--------|
| IFC4X3 now default export format | Positive — no schema selection needed for new docs |
| Plugin credential system | No impact on plain scripts |
| Python 3.9.2 unchanged from 2024 | Stability — no breaking changes |
| `vs.GetFPathName()` returns POSIX | Confirmed unchanged since 2019 |
| Plant Style Manager required for all plant instances | Plant data extraction patterns unchanged |
| Worksheet engine updated (SP1) | `GetWSFromImage()` still required |

---

## Scripted Document Migration

**VW 2026 can migrate files from VW 2012–2025 formats.** When opening an older file:

1. VW presents a migration dialog — this BLOCKS script execution
2. The script must be called AFTER the user has dismissed the dialog
3. There is no documented way to suppress this dialog via script

**Recommended batch workflow for migrated files (from YouTube tutorial "Batch Processing VW Files", VW 2025 Tech Summit):**
1. Open each file manually, allow migration, save
2. Run extract_all.py on the migrated saves
3. Do NOT attempt to automate the open+migrate step via script

---

## vicquick/vwx-mcp Environment Confirmation

The vwx-mcp bridge runs at TCP port 9878. Python scripts sent via `execute_script` run inside VW's Python environment (3.9.2). This means:
- Same limitations as direct script execution
- Same module availability
- Same handle null check requirement (`vs.Handle(0)`)
- Same ForEachObject one-call pattern required

The MCP bridge does NOT provide a headless mode. VW must be open with a document loaded for any `execute_script` call to succeed.

---

*Research date: 2026-05-13 | Agent: D — VW 2026 Environment (YouTube + Release Notes)*
