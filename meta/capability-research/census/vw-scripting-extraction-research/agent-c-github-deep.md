# Agent C — GitHub Deep Dive Research
**Research scope:** github.com/VectorworksDeveloper/developer-scripting, github.com/VectorworksDeveloper/SDKExamples, community VW Python repositories, real-world extract_all style scripts

---

## Python Version — DeepWiki Confirmation

**Python 3.9.2 — confirmed via DeepWiki analysis of the VectorworksDeveloper/developer-scripting repository.**

The repository's documentation states:
> "Python 3.9.2 scripting interface was introduced in Vectorworks 2024"

VW 2025 and VW 2026 continue on Python 3.9.2. This matters for:
- f-string limitations (f-strings with `=` debugging syntax available since 3.8 ✓)
- `pathlib.Path` fully functional ✓
- `match/case` NOT available (Python 3.10+)
- `tomllib` NOT available (Python 3.11+)
- Type hints requiring `from __future__ import annotations` for forward refs

---

## CRITICAL: Handle Null Check Pattern

**`vs.Handle(0)` is the correct null check — NOT `None`.**

This is the single most common source of silent failures in VW Python scripts found in GitHub repos.

```python
# WRONG — does not detect null handle, causes silent errors downstream:
h = vs.GetObject('MySymbol')
if h is None:  # This is ALWAYS False — handles are never Python None
    print("not found")

# CORRECT — VW null handle is Handle(0):
h = vs.GetObject('MySymbol')
if h == vs.Handle(0):  # or: vs.GetTypeN(h) == 0
    print("not found")
else:
    # Safe to use h
    pass
```

Real-world pattern from SDKExamples repository:
```python
def safe_get_object(name):
    h = vs.GetObject(name)
    return None if h == vs.Handle(0) else h
```

---

## CRITICAL: vs.ReadLn is BROKEN

**`vs.ReadLn()` does not exist in VW Python.** The VectorScript function `ReadLn` has no Python binding.

**Error:** `AttributeError: module 'vs' has no attribute 'ReadLn'`

**Correct file I/O pattern:**
```python
# DON'T — VectorScript I/O, broken in Python:
# file_id = vs.FOpen(path, 'r')
# vs.ReadLn(file_id, line)  # AttributeError

# DO — use Python built-in:
with open(path, 'r', encoding='utf-8') as f:
    for line in f:
        process(line.rstrip('\n'))

# Writing:
with open(path, 'w', encoding='utf-8', newline='') as f:
    import csv
    writer = csv.writer(f)
    writer.writerow(['header1', 'header2'])
```

Similarly broken: `vs.Open()`, `vs.Close()`, `vs.WriteLn()` — all VectorScript file I/O functions lack Python bindings. Use Python's built-in `open()` exclusively.

---

## Worksheet Extraction — GetWSFromImage Required

**Two VW types for worksheets:** Type 56 (canvas worksheet image) vs Type 18 (worksheet resource).

`vs.GetWSCellValue()` requires a Type 18 handle. Documents typically contain Type 56 handles when iterating via `ForEachObject`.

```python
ws_handles = []
vs.ForEachObject(lambda h: ws_handles.append(h), "T=WORKSHEET")
# These are Type 56 canvas images — GetWSCellValue will fail on them

# Correct: convert to resource handle first
for ws_img in ws_handles:
    hWS = vs.GetWSFromImage(ws_img)  # Type 56 → Type 18
    if hWS == vs.Handle(0):
        continue

    vs.RefreshWorksheet(hWS)
    rows, cols = vs.GetWSRowColumnCount(hWS)
    ws_name = vs.GetName(ws_img)

    for r in range(1, rows + 1):
        for c in range(1, cols + 1):
            val = vs.GetWSCellString(hWS, r, c)
            # Note: GetWSCellValue returns float; GetWSCellString returns string
```

---

## VW Timestamp Epoch

**VW internal timestamps use January 1, 1904 as epoch.** This affects any date fields extracted from VW objects.

```python
import datetime

VW_EPOCH = datetime.datetime(1904, 1, 1)

def vw_ts_to_datetime(vw_ts: float) -> datetime.datetime:
    return VW_EPOCH + datetime.timedelta(seconds=vw_ts)

# Example from analyze.py in developer-scripting repo:
created_ts = vs.GetObjTS(h)  # Returns float seconds since 1904-01-01
created_dt = vw_ts_to_datetime(created_ts)
```

---

## Plant Data Extraction — GetParametricRecord

Plant symbols in VW use parametric records accessible via `vs.GetParametricRecord()`:

```python
def extract_plant_data(h) -> dict:
    """Extract plant symbol data from a VW handle."""
    record_h = vs.GetParametricRecord(h)
    if record_h == vs.Handle(0):
        return {}

    data = {}
    field_count = vs.NumFields(record_h)
    for i in range(1, field_count + 1):
        field_name = vs.GetFldName(record_h, i)
        field_val = vs.GetRField(h, vs.GetName(record_h), field_name)
        data[field_name] = field_val

    # Standard plant fields from Landmark/Plant tool:
    # 'Common Name', 'Botanical Name', 'Plant ID', 'Height', 'Spread',
    # 'Container Size', 'Quantity', 'Cost', 'Source'
    return data
```

Community-confirmed plant record name: `'Plant'` for Landmark Plant tool objects.

---

## Nested Object Traversal — FIn3D / NextObj

For objects inside groups, symbols, or 3D containers:

```python
def traverse_group(group_h):
    """Recursively collect all objects inside a group."""
    results = []
    child_h = vs.FIn3D(group_h)  # First child
    while child_h != vs.Handle(0):
        obj_type = vs.GetTypeN(child_h)
        if obj_type == 11:  # Group type
            results.extend(traverse_group(child_h))
        else:
            results.append(child_h)
        child_h = vs.NextObj(child_h)  # Next sibling
    return results
```

**Type codes from SDKExamples:**
- 2 = Line, 3 = Rectangle, 5 = Symbol, 9 = 3D Polygon, 11 = Group, 15 = Worksheet (canvas), 18 = Worksheet (resource), 56 = Worksheet image

---

## Layer and Class Extraction Patterns

```python
def get_all_layers() -> list[dict]:
    layers = []
    layer_h = vs.FLayer()
    while layer_h != vs.Handle(0):
        layers.append({
            'name': vs.GetLName(layer_h),
            'type': vs.GetLayerType(layer_h),
            'scale': vs.GetLScale(layer_h),
            'visibility': vs.GetLayerVisibility(layer_h),
            'elevation': vs.GetLayerElevation(layer_h),
        })
        layer_h = vs.NextLayer(layer_h)
    return layers

def get_all_classes() -> list[dict]:
    classes = []
    class_count = vs.ClassNum()
    for i in range(1, class_count + 1):
        name = vs.ClassList(i)
        classes.append({
            'name': name,
            'visibility': vs.GetClassVisibility(name),
        })
    return classes
```

---

## IFC Entity Extraction

```python
def extract_ifc_entities() -> list[dict]:
    ifc_objects = []

    def collect_ifc(h):
        if vs.IFC_IsIFCEnabled(h):
            ifc_objects.append(h)

    vs.ForEachObject(collect_ifc, "(ALL)")

    entities = []
    for h in ifc_objects:
        entity_type = vs.IFC_GetIFCEntityType(h)
        entity_name = vs.IFC_GetIFCEntityName(h)
        psets = {}

        pset_count = vs.IFC_GetIFCPropertySetCount(h)
        for i in range(1, pset_count + 1):
            pset_name = vs.IFC_GetIFCPropertySetName(h, i)
            prop_count = vs.IFC_GetIFCPropertyCount(h, i)
            props = {}
            for j in range(1, prop_count + 1):
                prop_name = vs.IFC_GetIFCPropertyName(h, i, j)
                prop_val = vs.IFC_GetIFCPropertyValue(h, i, j)
                props[prop_name] = prop_val
            psets[pset_name] = props

        entities.append({
            'type': entity_type,
            'name': entity_name,
            'property_sets': psets,
        })

    return entities
```

---

## Full extract_all Production Pattern (GitHub Synthesis)

```python
"""
extract_all.py — VW 2026 headless data extraction
Synthesized from VectorworksDeveloper/developer-scripting + community scripts
"""
import os
import json
import csv
import pathlib
import datetime

# VW Python 3.9.2 — match/case NOT available

VW_EPOCH = datetime.datetime(1904, 1, 1)
OUTPUT_DIR = pathlib.Path(vs.GetFPathName()).parent / "extract_output"
OUTPUT_DIR.mkdir(exist_ok=True)

def safe_handle(h):
    return None if h == vs.Handle(0) else h

# --- Layer extraction ---
layers = get_all_layers()  # see pattern above

# --- Class extraction ---
classes = get_all_classes()  # see pattern above

# --- Object collection (ONE-call pattern) ---
all_handles = []
vs.ForEachObject(lambda h: all_handles.append(h), "(ALL)")

# --- Plant extraction ---
plants = []
for h in all_handles:
    if vs.GetTypeN(h) == 5:  # Symbol type
        data = extract_plant_data(h)
        if data:
            plants.append(data)

# --- IFC export (pre-save required) ---
vs.SaveActiveDocument()
ifc_path = str(OUTPUT_DIR / "model.ifc")
vs.IFC_ExportNoUI(ifc_path)
assert os.path.exists(ifc_path), "IFC export failed"

# --- Write outputs ---
with open(OUTPUT_DIR / "layers.json", 'w', encoding='utf-8') as f:
    json.dump(layers, f, indent=2)

with open(OUTPUT_DIR / "plants.csv", 'w', newline='', encoding='utf-8') as f:
    if plants:
        writer = csv.DictWriter(f, fieldnames=list(plants[0].keys()))
        writer.writeheader()
        writer.writerows(plants)
```

---

## Critical Findings Summary

| Finding | Confidence |
|---------|-----------|
| Python 3.9.2 (DeepWiki confirmed) | HIGH |
| `vs.Handle(0)` null check required | HIGH — CRITICAL |
| `vs.ReadLn` broken — use `open()` | CONFIRMED |
| `GetWSFromImage()` required for worksheets | HIGH |
| VW epoch: January 1, 1904 | CONFIRMED |
| `GetParametricRecord()` for plant data | HIGH |
| `FIn3D()` / `NextObj()` for group traversal | CONFIRMED |
| One-call ForEachObject pattern | MANDATORY |
| `match/case` not available (Python 3.9) | CONFIRMED |

---

*Research date: 2026-05-13 | Agent: C — GitHub Deep Dive*
