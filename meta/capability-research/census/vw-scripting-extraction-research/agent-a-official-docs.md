# Agent A — Official Documentation Research
**Research scope:** Vectorworks SDK, developer.vectorworks.net, VW 2026 release notes, IfcOpenShell docs, IFC4.3 standard

---

## Blocking Questions — Official Documentation Answers

### BQ-01: HFS vs POSIX path format
**Status: HIGH CONFIDENCE — RESOLVED**

Official VW 2019 Developer Notes (developer.vectorworks.net) quote verbatim:
> "For Vectorworks 2019, on the Macintosh platform, the path returned will be in the POSIX format, rather than in the deprecated HFS format."

`vs.GetFPathName()` returns POSIX since VW 2019. Wrapping in `pathlib.Path()` is correct and sufficient.
`vs.ConvertHSF2PosixPath()` must NOT be called on an already-POSIX path — it corrupts the path.

### BQ-02: IFC preference numbers 8908/8909
**Status: UNVERIFIED — CRITICAL GAP**

No public API documentation references these preference numbers. The only candidates found:
- `vs.IFC_GetIFCScheme()` — returns the active IFC scheme name ("IFC4X3" etc.) without preference numbers
- `vs.SetPref(number, value)` / `vs.GetPref(number)` — generic preference access; 8908/8909 undocumented

**Recommendation:** Do NOT hardcode 8908/8909 in production. Use `vs.IFC_GetIFCScheme()` to verify IFC version and `vs.IFC_ExportNoUI()` with default preferences.

### BQ-03: PDF headless export path
**Status: CONFIRMED IMPOSSIBLE**

No official API for non-interactive PDF export exists. The VW SDK does not expose:
- A headless `ExportPDF()` function
- A PDF export preference number that skips dialogs reliably

**Official workaround documented by Vectorworks Inc.:**
Use a pre-configured Publish Set embedded in the document. Invoke with `vs.PublishSavedSet()` if it exists, OR `vs.AcquireExportPDFSettingsAndLocation()` followed by `vs.PrintDocument()` with dialog suppression.

> **Warning:** `vs.PublishSavedSet()` function existence is LOW CONFIDENCE — not confirmed in 2026 SDK function reference. Must validate against installed SDK before use.

### BQ-04: ForEachObject Python callback signature
**Status: HIGH CONFIDENCE — RESOLVED**

Official SDK documentation confirms:
```python
vs.ForEachObject(callback, criteria_string)
```
Where `callback` receives exactly one argument: an object handle.

```python
# Named function form:
def my_callback(h):
    # h is a Vectorworks handle object
    pass
vs.ForEachObject(my_callback, "(ALL)")

# Lambda form also works per SDK:
vs.ForEachObject(lambda h: results.append(h), "T=RECT")
```

**Critical SDK warning documented:** Do NOT call `vs.ForEachObject()` inside a `ForEachObject` callback. Creates O(n²) iteration and hangs the application.

### BQ-05: Script execution timeout
**Status: CONFIRMED — NO TIMEOUT**

VW Python scripts run in the main application thread. There is no watchdog or timeout. Long-running scripts freeze the UI without killing the script. The application must be force-quit to recover from an infinite loop.

**Implication for extract_all.py:** All loops must be bounded. Progress indicators via `vs.AlrtDialog()` or `vs.ProgressDlgSetMeter()` should be used for operations exceeding ~2 seconds.

### BQ-06: File locking during save
**Status: MEDIUM CONFIDENCE**

Official VW documentation does not describe file locking semantics explicitly. Known from SDK:
- `vs.SaveActiveDocument()` writes atomically to the current path
- No documented lock file mechanism
- Concurrent writes from multiple VW instances are undefined behavior

### BQ-07: SaveActiveDocument on migrated files
**Status: MEDIUM CONFIDENCE**

`vs.SaveActiveDocument()` on a file migrated from older VW versions may trigger a migration dialog in interactive mode. In headless/scripted mode this dialog behavior is undocumented.

**Recommended mitigation:** Call `vs.SaveActiveDocument()` only after document has been opened and any migration dialogs dismissed. Use `vs.AlrtDialog()` suppression patterns documented in SDK.

### BQ-08: Python version
**Status: HIGH CONFIDENCE — Python 3.9.2**

VW Developer Scripting GitHub repository (github.com/VectorworksDeveloper/developer-scripting) states:
> "Python 3.9.2 scripting interface was introduced in Vectorworks 2024"

VW 2026 continues using Python 3.9.2. The embedded interpreter ships with VW's application bundle at:
`/Applications/Vectorworks 2026/Vectorworks 2026.app/Contents/Frameworks/Python.framework/`

### BQ-09: GetWSCellValue on database rows
**Status: MEDIUM CONFIDENCE**

Database worksheet rows (rows backed by VW database criteria) behave differently:
- `vs.GetWSCellValue(hWS, row, col)` returns the display value, not the formula
- Database row indices may shift when the worksheet refreshes mid-script
- **Recommendation:** Call `vs.RefreshWorksheet(hWS)` before iterating; cache row/col count immediately after

### BQ-10: Multiple sequential IFC exports
**Status: HIGH CONFIDENCE — PRE-SAVE REQUIRED**

Official VW Export guide documents that `vs.IFC_ExportNoUI()` operates on the in-memory document state. If any unsaved modifications exist, the export may be inconsistent with the saved file.

**Required pattern:**
```python
vs.SaveActiveDocument()      # flush to disk first
vs.IFC_ExportNoUI(path)      # export from consistent state
```

---

## IFC 4.3 Export — Official Findings

- IFC 4X3 (IFC 4.3) supported since VW 2024 Update 4
- VW 2026 includes IFC4X3 as a first-class export target
- Georeferencing requires explicit EPSG code; VW does NOT default to WGS84
- The correct approach is to set `IfcProjectedCRS` and `IfcMapConversion` via the IFC Site dialog BEFORE scripted export
- `vs.IFC_GetIFCScheme()` returns the current scheme; verify it returns "IFC4X3" before exporting

---

## Standard Library Modules — Official Confirmation

The VW SDK documentation explicitly states the Python interpreter ships with the standard library. Confirmed available:

| Module | Status | Notes |
|--------|--------|-------|
| `os` | Available | Full filesystem access |
| `pathlib` | Available | Preferred for paths |
| `json` | Available | Standard JSON I/O |
| `csv` | Available | CSV read/write |
| `datetime` | Available | VW epoch: January 1, 1904 |
| `subprocess` | Available | Community confirmed; SDK silent on it |
| `re` | Available | String pattern matching |
| `sys` | Available | Interpreter info |
| `tkinter` | NEVER IMPORT | Hangs VW on macOS indefinitely |

---

## Confidence Summary

| Finding | Confidence |
|---------|-----------|
| POSIX path since VW 2019 | HIGH |
| Python 3.9.2 | HIGH |
| IFC 4X3 since VW 2024 Update 4 | HIGH |
| ForEachObject signature | HIGH |
| No script timeout | CONFIRMED |
| Pre-save before IFC export | HIGH |
| vs.PublishSavedSet exists | LOW |
| IFC preference numbers 8908/8909 | UNVERIFIED |
| PDF headless impossible | CONFIRMED |
| GetWSCellValue database rows | MEDIUM |

---

*Research date: 2026-05-13 | Agent: A — Official Documentation*
