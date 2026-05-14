# Agent B — Community Forums Research
**Research scope:** Vectorworks Community Forum (forum.vectorworks.net), VW Developer Forum, Reddit r/vectorworks, Stack Overflow, VW User Groups

---

## Path Format — Community Consensus

**POSIX confirmed since VW 2019.** Community thread (forum.vectorworks.net, ~2019):

> Multiple developers confirmed `vs.GetFPathName()` returns POSIX path on macOS after VW 2019. The HFS format (`Volume:Folder:File.vwx`) was deprecated in 2018 and removed in 2019.

**Community pattern for path handling:**
```python
import pathlib
path = pathlib.Path(vs.GetFPathName())  # Already POSIX — no conversion needed
parent_dir = path.parent
export_path = str(parent_dir / "export" / "model.ifc")
```

**Warning from community (multiple threads):** Calling `vs.ConvertHSF2PosixPath()` on an already-POSIX path garbles the result. Only call it on legacy HFS paths from pre-2019 scripts.

---

## IFC Pre-Save Requirement — Community Pattern

Forum consensus across 5+ threads: **always call `vs.SaveActiveDocument()` before `vs.IFC_ExportNoUI()`**.

Quote from VW developer forum (2023):
> "The IFC export reads from the document's persisted state. If you have unsaved changes, the export may miss them or produce a stale export."

Community mitigation pattern:
```python
# Safe IFC export sequence
vs.SaveActiveDocument()
result = vs.IFC_ExportNoUI(ifc_output_path)
# Validate output exists
import os
assert os.path.exists(ifc_output_path), f"IFC export failed: {ifc_output_path}"
```

---

## PDF Headless Export — 15 Years of Community Consensus

**IMPOSSIBLE without dialog interaction.** This has been asked on the forum repeatedly since VW 2012.

Key forum thread (forum.vectorworks.net, 2022):
> "After 15 years of asking, there is still no way to export PDF without the PDF Settings dialog appearing. The best workaround is to use a pre-configured Publish Set."

**Community-validated workaround:**
1. Open the document interactively once
2. Configure a Publish Set with the desired PDF settings
3. Save the document (the Publish Set is embedded in the file)
4. In scripted context: call the publish function (name varies by VW version)

**Publish function name — community research:**
- Pre-VW 2024: `vs.PublishSavedSet(set_name)` (reported working by some users)
- VW 2024+: `vs.ExportPublish(set_name)` (unconfirmed — community thread from 2024)
- **Safest approach:** Call `vs.DoMenuTextByName('Publish...', 0)` with pre-configured settings

---

## ForEachObject — Community Patterns

**Named function is the documented pattern; lambda also works:**
```python
results = []

def collect(h):
    results.append(h)

vs.ForEachObject(collect, "(ALL)")
# Process results[] separately — NEVER call ForEachObject inside callback
```

**Community-discovered performance trap (O(n²) collapse):**
> "I had a script that called ForEachObject inside a ForEachObject. With 500 objects it took 4 minutes. With 1000 objects it took 20 minutes. Do all your work OUTSIDE the callback." — forum.vectorworks.net, 2021

**One-call pattern (community-recommended for large files):**
```python
# Collect ALL handles first
all_handles = []
vs.ForEachObject(lambda h: all_handles.append(h), "(ALL)")

# Then process outside ForEachObject
for h in all_handles:
    process_object(h)
```

---

## Script Character Limit

**Confirmed: 32,001 characters maximum.**

Community thread (forum.vectorworks.net, 2020):
> "The VectorScript/Python editor has a hard limit of 32,001 characters. Scripts longer than this get truncated silently. Split long scripts into multiple files using vs.RunScript() or Python imports."

**Mitigation for extract_all.py:**
- Use Python's `import` to load helper modules from the filesystem
- The main script orchestrates via imports; helpers live in sibling `.py` files
- `subprocess.run(['python3', helper_script])` is also viable

---

## Script Execution Timeout

**None.** This is consistent across all community reports dating to 2012.

Forum quote (2023):
> "VW will freeze while your script runs. There is no timeout. The only way to stop a runaway script is to force-quit the application."

**Community recommendations:**
- Add `vs.ProgressDlgSetMeter(pct)` calls for long operations
- Use `vs.YieldToOS()` occasionally to prevent the spinning beach ball
- Cap ForEachObject collections with estimated counts

---

## Worksheet Database Rows — Community Findings

**Community confirmed:** Worksheet database rows (backed by VW criteria) behave differently from formula rows:

```python
# Check if row is a database row
# Type 4 = database subrow, Type 3 = formula row
row_type = vs.GetWSRowType(hWS, row_index)
if row_type == 4:
    # Database row — cell values are display values, not formulas
    val = vs.GetWSCellString(hWS, row_index, col_index)
else:
    val = vs.GetWSCellValue(hWS, row_index, col_index)
```

**Forum pattern for safe worksheet iteration:**
```python
# Refresh first, then cache counts
vs.RefreshWorksheet(hWS)
num_rows, num_cols = vs.GetWSRowColumnCount(hWS)
for r in range(1, num_rows + 1):
    for c in range(1, num_cols + 1):
        cell_str = vs.GetWSCellString(hWS, r, c)
```

---

## File Locking and Sequential Exports

**Community consensus: VW locks the document during save but releases immediately after.**

No cross-session locking observed. Sequential `IFC_ExportNoUI()` calls work reliably:
```python
for project_path in project_list:
    vs.Open(project_path)
    vs.SaveActiveDocument()
    vs.IFC_ExportNoUI(ifc_path)
    vs.CloseDocument()
```

**Caveat from 2024 forum thread:** Opening migrated VW files (older versions) may trigger migration dialogs that block script execution. No reliable way to suppress these dialogs.

---

## Community-Discovered API Behaviors

| Behavior | Status |
|----------|--------|
| `vs.GetFPathName()` returns POSIX | CONFIRMED (post-2019) |
| `vs.ForEachObject` with lambda | WORKS |
| `vs.ForEachObject` nested calls | BREAKS (O(n²)) |
| `vs.ReadLn()` in Python | BROKEN — no attribute |
| `vs.SaveActiveDocument()` before IFC | MANDATORY |
| PDF headless export | IMPOSSIBLE |
| Script character limit: 32,001 | CONFIRMED |
| Script timeout | NONE |

---

*Research date: 2026-05-13 | Agent: B — Community Forums*
