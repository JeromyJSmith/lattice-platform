# Research Proposal: Vectorworks Scripting & Extraction Pipeline
<!-- Created: 2026-05-13 | Status: AWAITING RESEARCH -->
<!-- Purpose: Full intelligence gathering before implementing VW extraction automation -->

---

## Problem Statement

We are building a fully automated extraction pipeline that runs inside Vectorworks 2026
using its internal Python (`vs.*`) and VectorScript (Pascal) APIs. The pipeline must:

1. Save a versioned copy of the open document without any dialog or UI interaction
2. Extract all layers, classes, record formats, plant data, symbol definitions, worksheets
   (including cell content), sheet layers, and IFC entity assignments into structured JSON/CSV
3. Export IFC 4.3 (and IFC 2x3 fallback), DXF, and PDF headlessly — no user prompts
4. Write all output to a structured folder relative to the document's own path
5. Do all of this reliably across five large sample projects (266 MB – 1.5 GB VWX files)
   that were just migrated from older VW versions to VW 2026

We have a working draft (`extract_all.py`) and a preliminary plan. Before we implement
and run it on real files, we need a complete intelligence picture of:

- What the VW scripting community has actually gotten to work
- Where people have hit walls and why
- Undocumented behaviors, version regressions, and platform-specific traps
- Community workarounds that are not in the official docs
- What has changed between VW 2024 / 2025 / 2026 that might affect our scripts

---

## Research Objectives

### Objective 1 — Verify our core API assumptions
Each of these calls is in our current plan. We need real-world confirmation that each
works as documented, and known failure modes:

| Call | What we need to know |
|---|---|
| `vs.SaveActiveDocument(path)` | Does it accept POSIX paths on Mac? HFS paths? Both? Known failure cases beyond "same path returns -1"? Any VW 2026 regressions? |
| `vs.GetFPathName()` | Does it return HFS or POSIX on Mac in VW 2026? Behavior on unsaved documents? |
| `vs.CreateFolder(path)` | Path format requirements? Behavior if folder already exists? Return value meaning? |
| `vs.IFC_ExportNoUI(path)` | Real-world success rate. Known failures (missing georef, empty file, silent crash). VW 2026 behavior. IFC version controlled by which preference exactly? |
| `vs.ExportDXFDWG()` | What settings does it actually inherit? Any reports of it exporting wrong layers/classes? Silent failure modes? |
| `vs.AcquireExportPDFSettingsAndLocation()` | Any known headless/bypass? Can it be pre-seeded so dialog is skipped? Community workarounds? |
| `vs.PublishSavedSet(name, folder)` | Does the Publish Set have to be in the document or can it be in a workspace? Failure modes when set doesn't exist? |
| `vs.ForEachObject(cb, criteria)` | Callback signature requirements in Python. Stack depth limits. Performance on large files (1.5 GB). Known crashes. |
| `vs.GetWSCellValue(h, row, col)` | Does it return computed or raw values? Formula strings? Behavior on database rows? |
| `vs.ConvertHSF2PosixPath()` | The docs warn it returns gibberish on already-POSIX paths. What format does VW 2026 actually use internally? |
| `vs.IFC_GetIFCEntity(h)` | Works on all object types or only IFC-assigned ones? Return value on unassigned objects? |

### Objective 2 — Discover undocumented behaviors and community workarounds
The official function reference is often incomplete. We need to find:
- Community scripts that implement "save a copy as" without dialog
- Any known alternative to `AcquireExportPDFSettingsAndLocation` for headless PDF
- Scripts that successfully batch-export from large VWX files
- Any VW plugin or workspace trick that enables fully headless operation
- The actual IFC version preference number (we have 8908/8909 — verify these)

### Objective 3 — Identify known problems before we hit them
- VW 2026 migration bugs: what breaks when opening older-version VWX files
- Memory/crash behavior on very large files (1.5 GB lakehouse project)
- `ForEachObject` on files with thousands of plant instances — stack issues?
- IFC export failures on files with missing georeferencing
- DXF export exporting wrong coordinate space after version migration
- Python script timeout limits inside VW (is there a watchdog?)
- Script Runner dialog limitations — can a Python script call another Python script?
- File locking issues when writing output while VW has the document open
- Unicode/encoding issues in plant names, layer names, class names

### Objective 4 — VW 2026 specific changes
- What changed in VW 2026's Python scripting environment vs 2025/2024
- Any new `vs.*` functions relevant to extraction
- Deprecations or behavioral changes to functions we're using
- IFC 4.3 support status in VW 2026 (vs IFC 2x3)
- Changes to the Publish system in VW 2026

### Objective 5 — Alternative approaches we haven't considered
- Is there a VW command-line / headless mode we don't know about?
- VW Cloud Services scripting hooks
- The `vicquick/vwx-mcp` approach — what does it actually do internally?
- Any VW SDK C++ plugin approach that exposes a cleaner scripting surface
- Third-party tools that extract from VWX without opening VW (IfcOpenShell already handled)

---

## Research Agent Team

### Agent A — VectorScript / Python API Deep Researcher
**Mission:** Exhaust the official developer documentation and the Vectorworks GitHub repos.

**Sources to cover:**
- `https://github.com/Vectorworks/developer-scripting` — full function reference, all examples
- `https://github.com/Vectorworks/developer-worksheets` — worksheet formula/criteria reference
- `https://github.com/Vectorworks/developer-sdk` — SDK docs, version history, changelogs
- `https://github.com/VectorworksDeveloper/SDKExamples` — C++ examples that reveal internal behavior
- Vectorworks Developer Portal: `https://developer.vectorworks.net`
- VW Help Center scripting sections

**Specific searches:**
- `SaveActiveDocument` site:github.com/Vectorworks
- `IFC_ExportNoUI` examples in the wild
- `GetFPathName` Mac path format
- `ForEachObject` Python callback examples
- VW 2026 release notes for scripting changes

---

### Agent B — Community Intelligence (Forums, Reddit, Hacker News)
**Mission:** Find real-world reports of successes, failures, and workarounds.

**Sources to cover:**
- Vectorworks Community Forum: `https://forum.vectorworks.net` — search all scripting threads
- Reddit: r/vectorworks, r/CAD, r/BIM, r/Python
- Hacker News: search `vectorworks scripting`, `vectorworks python`, `vectorworks automation`
- Stack Overflow: `vectorworks` tag, `vectorscript` tag
- Vectorworks Tech Support board archives

**Specific searches:**
- `SaveActiveDocument` forum threads — any reports of it not working
- `IFC export headless` VW forum
- `python script vectorworks crash large file`
- `ForEachObject timeout` or `ForEachObject crash`
- `vectorworks 2026 scripting changes` forum threads
- `PDF export automation vectorworks` workarounds
- `vectorworks script file path mac` — HFS vs POSIX confusion threads
- Any threads about batch processing multiple VWX files

---

### Agent C — GitHub Deep Search
**Mission:** Find every script, plugin, and tool on GitHub that touches VW scripting.

**Sources to cover — search all of these:**
- `github.com/search?q=vectorworks+python+script&type=repositories`
- `github.com/search?q=vectorscript+export&type=code`
- `github.com/search?q=vs.SaveActiveDocument`
- `github.com/search?q=IFC_ExportNoUI`
- `github.com/search?q=vectorworks+ForEachObject`
- `github.com/search?q=vectorworks+extract+layers`
- `github.com/mako-357/vectorworks-mcp` — full repo audit
- `github.com/togawamanabu/vectorworks-mcp` — full repo audit
- `github.com/dietergeerts/dlibrary` — Python helper library, read every module
- `github.com/machistore/basics_of_Vectorworks_plugins` — basics, read all examples
- Any repo with `vwx` in name or `vectorworks` topic

**Specific code patterns to find:**
- Any working implementation of headless save/export
- Any implementation of batch worksheet export
- Any implementation of plant data extraction
- Error handling patterns for VW Python scripts
- Path handling utilities for Mac VW

---

### Agent D — YouTube Research
**Mission:** Find tutorials, demos, and screencasts that show real VW Python/VectorScript in action.

**Sources to cover:**
- YouTube search: `vectorworks python scripting tutorial`
- YouTube search: `vectorworks vectorscript automation`
- YouTube search: `vectorworks IFC export script`
- YouTube search: `vectorworks marionette script data extraction`
- YouTube search: `vectorworks batch export`
- Vectorworks official YouTube channel — scripting/developer playlists
- Any VW University sessions on scripting

**What to capture:**
- Actual code shown on screen — transcribe key function calls
- Timestamps where people hit problems and show workarounds
- Any mention of file path issues on Mac
- Any mention of large file performance
- Marionette network approaches that parallel our extraction goals

---

### Agent E — VW Help Center & Official Docs Audit
**Mission:** Read every scripting-adjacent page in the official VW Help Center.

**Sources to cover:**
- `https://app-help.vectorworks.net/2026/` — VW 2026 help (scripting, IFC, worksheet sections)
- `https://developer.vectorworks.net/index.php/VS:Function_Reference`
- IFC export documentation pages
- Worksheet formula reference
- VW 2026 "What's New" — scripting section
- VW 2025 → 2026 migration guide

**Specific pages:**
- Run Script dialog behavior and limitations
- Script execution environment (Python version, available modules)
- File path handling on Mac vs Windows
- IFC export settings reference (which preferences control what)
- Publish dialog and saved sets — full documentation

---

## Specific Questions That Must Be Answered

These are blocking questions. The plan cannot proceed until we have documented answers.

1. **Path format**: Does `vs.GetFPathName()` return HFS (colon-delimited) or POSIX (slash-delimited) on Mac VW 2026? Does `vs.SaveActiveDocument()` require HFS or POSIX or does it accept both?

2. **IFC version control**: The docs reference preference numbers 8908/8909. Are these the correct and current preference indices for IFC version selection in VW 2026? What are the valid values and what do they map to?

3. **PDF headless**: Is there any way to call `AcquireExportPDFSettingsAndLocation` with pre-seeded settings so it skips the dialog? Or is there a completely different headless PDF path?

4. **`ForEachObject` in Python**: What is the exact signature of the Python callback? Does it receive a handle? Can it be a lambda or must it be a named function? Any stack/recursion limits?

5. **Script execution timeout**: Does VW kill a Python script after a certain time? What happens on a 1.5 GB file that takes 10+ minutes to process?

6. **File writing while VW has document open**: Can a Python script write files to the same folder as the open VWX without VW interfering? Any file locking issues?

7. **`vs.SaveActiveDocument` on migrated files**: If a file was just migrated from VW 2024 to VW 2026 and hasn't been saved yet, does `SaveActiveDocument` work correctly or does it fail?

8. **VW 2026 Python version**: What version of Python does VW 2026 embed? What stdlib modules are available? Is `json`, `os`, `os.path`, `hashlib` available without `import` restrictions?

9. **`GetWSCellValue` on database rows**: Does it return the computed cell value for database rows, or does it throw/return empty for non-summary rows?

10. **Multiple exports in one script run**: Can one Python script call `IFC_ExportNoUI`, then `ExportDXFDWG`, then the PDF chain, all in sequence? Or does VW require separate script invocations per export?

---

## Known Risks to Investigate

| Risk | Severity | What to look for |
|---|---|---|
| HFS/POSIX path confusion crashes `SaveActiveDocument` | High | Forum reports, code examples showing working path format |
| IFC export silently writes empty file on migrated doc | High | Reports of 0-byte or invalid IFC after version migration |
| `ForEachObject` crashes on files with 10k+ objects | High | Performance reports, any mention of object count limits |
| VW kills long-running script mid-execution | High | Any mention of script timeout or watchdog |
| `ExportDXFDWG()` inherits wrong previous settings | Medium | Forum reports of DXF coming out wrong after automated call |
| PDF export requires dialog — no true headless path | Medium | Any workaround found or confirmed impossible |
| VW 2026 broke `IFC_ExportNoUI` (regression) | Medium | VW 2026 release notes, forum bug reports |
| Python stdlib restricted inside VW | Medium | Any mention of import errors inside VW Python environment |
| File path unicode issues (project names with spaces/special chars) | Medium | Forum reports, known encoding bugs |
| `SaveActiveDocument` on already-open file in VW returns -1 always | Low | Docs say different path required — confirm this is the correct behavior |

---

## Deliverables Expected from Research

Each agent produces a structured report with:

1. **Confirmed working patterns** — code snippets verified by community/docs
2. **Confirmed broken patterns** — things that look like they should work but don't
3. **Open questions** — things that still couldn't be verified
4. **Recommended changes to the current plan** — specific line items
5. **Sources** — every URL, repo, forum thread, video timestamp used

The combined research output feeds directly into a final revised `extract_all.py` and
a VectorScript save-version script before anything runs on the real project files.

---

## Output File Location

Research reports go in:
```
meta/capability-research/census/vw-scripting-extraction-research/
  agent-a-official-docs.md
  agent-b-community-forums.md
  agent-c-github-deep.md
  agent-d-youtube.md
  agent-e-help-center.md
  SYNTHESIS.md          ← combined findings + final plan adjustments
```

---

## Success Criteria

Research is complete when:
- All 10 blocking questions above have documented answers with sources
- Every function in `extract_all.py` has a confirmed working pattern or a documented workaround
- The PDF export situation is resolved (headless path found OR confirmed impossible with documented fallback)
- Known risks table above has a mitigation or acceptance decision for each row
- `SYNTHESIS.md` is written and reviewed

Only after `SYNTHESIS.md` is complete do we write a single line of production script.

---

*Proposal authored: 2026-05-13*
*Status: Ready for research skill execution*
