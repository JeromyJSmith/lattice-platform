# Vectorworks Export Commands Reference
<!-- Auto-copied into every project by: lattice project init -->
<!-- Source: Vectorworks/developer-scripting, live 2026-05-13 -->

This document is the canonical reference for all Vectorworks Python/VectorScript
export API calls used in the LATTICE extraction pipeline. It is written into
every project directory at `docs/VW_EXPORT_COMMANDS.md` by `lattice project init`.

---

## IFC Export

### Headless (no dialog) — USE THIS

```python
# IFC 4.3 — no dialog, no user interaction required
ok = vs.IFC_ExportNoUI("/path/to/output.ifc")   # returns BOOLEAN

# IFC 2x3 — same call; IFC version is controlled by VW preferences
# Switch version in File > Document Settings > IFC Settings first, then call:
ok = vs.IFC_ExportNoUI("/path/to/output_2x3.ifc")
```

### With dialog (fallback)
```python
vs.IFC_ExportWithUI(False)   # False = export all objects (not just selected)
```

### Read IFC assignments from objects
```python
ifc_class = vs.IFC_GetIFCEntity(obj_handle)          # e.g. "IfcPlant"
predefined = vs.IFC_GetEntityProp(obj_handle, "PredefinedType")
num_psets = vs.IFC_GetNumPsets(obj_handle)
pset_name = vs.IFC_GetPsetName(obj_handle, index)    # 0-based index
```

---

## DXF / DWG Export

```python
# Export current document to DXF/DWG using last-configured settings
vs.ExportDXFDWG()

# Settings are pre-configured via File > Export > Export DXF/DWG...
# There is no direct parameter to set format (DXF vs DWG) or version in script;
# configure once via dialog, then call ExportDXFDWG() repeatedly.
```

---

## PDF Sheet Export

### Batch PDF (preferred — exports all sheet layers at once)
```python
# Step 1: show settings dialog (once, to configure)
ok = vs.AcquireExportPDFSettingsAndLocation(False)  # False = single document
if ok:
    # Step 2: open PDF document
    opened = vs.OpenPDFDocument("/path/to/output.pdf")
    if opened:
        # Step 3: export each sheet (by saved view name or sheet name)
        for sheet_name in sheet_names:
            pages_written = vs.ExportPDFPages(sheet_name)
        # Step 4: close
        vs.ClosePDFDocument()
```

### Publish saved set (highest-level batch output — covers PDF + DXF + IFC)
```python
# PublishSavedSet publishes a named publish set to a folder.
# Configure the set once via File > Publish..., give it a name, save.
# Then call:
ok = vs.PublishSavedSet("LATTICE Export Set", "/path/to/output/folder/")
# This one call can export PDF + DXF + IFC simultaneously per set configuration.
```

### Print without dialog
```python
vs.PrintWithoutUsingPrintDialog()   # uses last print settings
vs.PrintUsingPrintDialog()          # shows dialog
```

---

## 3D Geometry Interchange

```python
vs.ExportSTEP("/path/to/output.step", False)  # False = solids (not surfaces)
vs.ExportSTL()                                 # STL mesh
vs.ExportSAT()                                 # SAT/ACIS solids
vs.ExportIGES()                                # IGES
```

---

## Data Extraction (Headless — no dialog needed)

### Design Layers
```python
layer = vs.FActLayer()
while layer:
    name = vs.GetLName(layer)
    visibility = vs.GetLVisibility(layer)   # 0=visible 1=invisible 2=grey
    scale = vs.GetLScale(layer)
    layer_type = vs.GetObjectVariableInt(layer, 154)  # 0=design 1=sheet
    layer = vs.NextLayer(layer)
```

### Classes
```python
count = vs.ClassNum()
for i in range(1, count + 1):
    name = vs.ClassList(i)
```

### Record Formats
```python
vs.ForEachObject(callback, "T=RECFMT")
# In callback:
name = vs.GetName(rec_handle)
num_fields = vs.NumFields(rec_handle)
field_name = vs.GetFldName(rec_handle, field_index)   # 1-based
field_type = vs.GetFldType(rec_handle, field_index)
field_default = vs.GetFldDefault(rec_handle, field_index)
```

### Record Field Values on Objects
```python
value = vs.GetRField(obj_handle, "RecordName", "FieldName")
vs.SetRField(obj_handle, "RecordName", "FieldName", "new_value")
```

### Worksheets
```python
vs.ForEachObject(callback, "T=SPRDSHEET")
# In callback:
name = vs.GetName(ws_handle)
rows, cols = vs.GetWSRowColumnCount(ws_handle)
cell_value = vs.GetWSCellValue(ws_handle, row, col)    # 1-based
criteria = vs.GetWSDatabaseCriteria(ws_handle, row)    # database row criteria
# or: vs.GetWSDatabaseCriteriaA(ws_handle, row)
row_type = vs.GetWSRowType(ws_handle, row)
```

### All Objects by Type
```python
vs.ForEachObject(callback, "T=PLUGINOBJECT")  # parametric objects (plants, etc)
vs.ForEachObject(callback, "T=SYMDEF")         # symbol definitions
vs.ForEachObject(callback, "T=SPRDSHEET")      # worksheets
vs.ForEachObject(callback, "T=RECFMT")         # record formats
vs.ForEachObject(callback, "")                 # all objects
```

### Symbol 2D/3D presence
```python
child_2d = vs.FInGroup(sym_handle)    # first child = 2D group
child_3d = vs.NextSObj(child_2d)      # second child = 3D group (if present)
```

### Plant Record Fields (standard VW Plant Style)
```python
PLANT_RECORD = "Plant Record"
latin    = vs.GetRField(h, PLANT_RECORD, "LatinName")
common   = vs.GetRField(h, PLANT_RECORD, "CommonName")
height   = vs.GetRField(h, PLANT_RECORD, "Height")
spread   = vs.GetRField(h, PLANT_RECORD, "Spread")
quantity = vs.GetRField(h, PLANT_RECORD, "Quantity")
id_tag   = vs.GetRField(h, PLANT_RECORD, "IDTag")
```

### Object 3D position
```python
loc = vs.GetEntPenLoc3D(obj_handle)   # returns (x, y, z) tuple
```

### Document info
```python
doc_name = vs.GetFName()          # current document filename
vs.Message("text")                # status bar message (non-blocking)
vs.AlrtDialog("text")             # alert dialog (blocking)
```

---

## VW Preferences for Export Configuration

```python
# IFC: reuse last-used export settings
vs.SetPref(8908, True)             # use last-used IFC settings
vs.SetSavePref(8909, "/path.ifc")  # output path for IFC export

# General: get/set preferences
value = vs.GetPref(pref_number)
vs.SetPref(pref_number, value)
```

---

## Vectorworks SDK & Reference Repos

These are the authoritative sources for the vs.* API. Pulled into every project.

| Repo | What it has | URL |
|------|-------------|-----|
| `Vectorworks/developer-scripting` | Python, VectorScript, Marionette, full function reference | https://github.com/Vectorworks/developer-scripting |
| `Vectorworks/developer-worksheets` | Worksheet functions, object parameter references | https://github.com/Vectorworks/developer-worksheets |
| `Vectorworks/developer-sdk` | C++ SDK, version docs, build info | https://github.com/Vectorworks/developer-sdk |
| `VectorworksDeveloper/SDKExamples` | C++ SDK examples 2021–2026, menu commands, plugin objects | https://github.com/VectorworksDeveloper/SDKExamples |
| `mako-357/vectorworks-mcp` | SDK plugin + Unix socket MCP bridge architecture | https://github.com/mako-357/vectorworks-mcp |
| `togawamanabu/vectorworks-mcp` | VW documentation RAG via MCP | https://github.com/togawamanabu/vectorworks-mcp |
| `dietergeerts/dlibrary` | Python helper library for VW plugin development | https://github.com/dietergeerts/dlibrary |
| `machistore/basics_of_Vectorworks_plugins` | Python plugin basics (MIT) | https://github.com/machistore/basics_of_Vectorworks_plugins |

---

## ODBC / Database Connection

VW can connect to external databases via ODBC for bidirectional record sync.

**Drivers supported (Mac):**
- PostgreSQL: iODBC + psqlODBC
- MySQL: iODBC + MySQL ODBC driver
- SQLite: iODBC + SQLite ODBC

**Setup flow:**
1. Install iODBC + driver on Mac
2. Configure DSN in `/Library/ODBC/odbc.ini`
3. In VW: File > Database > Database Setup... → connect DSN
4. Link record format fields to database columns (bidirectional)
5. Object data syncs on update

**Reference:**
- https://app-help.vectorworks.net/2023/eng/VW2023_Guide/Database/Database_setup.htm
- https://product-help.vectorworks.net/2025/jpn/VW2025_Guide/Database/ODBC_driver_information.htm
- `meta/capability-research/census/repo-census-004-odbc.md`

---

## DDC Connection Points

Each exported IFC feeds the DDC pipeline:

```
VWX → IFC_ExportNoUI() → IfcOpenShell parse → Pixeltable lattice/projects/{id}/ifc_elements
                                                          ↓
                                               ddc/erp/boq-adapter.py → BOQ
                                               ddc/cwicr/cost-search.py → unit costs
                                               ddc/admin/*.sql → reporting
```

---

## iTwin Connection Points

```
IFC file → POST /v1/projects/{id}/ingest/ifc
                → pixeltable/service/routes/itwin.py
                → itwin_adapter.py (Bentley APIs: iModels, Reality Data, Changed Elements)
                → lattice/projects/{id}/ifc_elements (Pixeltable)
```

**Current state:** Export path only (C++ VW plugin is future).
**iTwin APIs wired:** iModels, Reality Data, Changed Elements, Synchronization.

---

*Generated: 2026-05-13 | Updated by: lattice project init on every project creation*
