# Farber-Haines Record Export Matrix

Date: 2026-05-16

## Purpose

Clarify what the Vectorworks `Tools > Database` export surface is actually
showing in the Farber-Haines file, which record formats matter for the
estimating workflow, and which exports are noise for pricing/georef work.

This answers a narrower question than IFC export:

- which records can be exported as database tables
- which of those are relevant to pricing
- which are relevant to plant/site metadata
- which are mostly annotation or plug-in noise

## Verified Meaning Of The Menu

The screenshot menu is a **record format export surface**, not an IFC schema
version selector.

Official Vectorworks help says:

- `Tools > Database > Record Format Connection` opens a dialog listing the
  record formats available in the current file
- choosing `Export as Database Table` creates a database table where each
  record field becomes a database column

Source:

- `/Users/ojeromyo/.vectorworks-docs/docs/vw-help/2026_eng_VW2026_Guide_Database_Automatically_creating_a_database_table_from_a_record_format.htm.md`

Important distinction:

- `File > Export > Export IFC Project` = geometry + semantics + IFC schema
- `Tools > Database > Record Format Connection > Export as Database Table` =
  object-attached record fields exported to a relational table

## Farber-Haines Relevant Record Groups

### 1. Core estimating record

#### `Project Cost`

Why it matters:

- this is the main pricing payload our scripts write onto model objects
- it is the clearest export surface for proving that pricing is actually in the
  VWX and can be exported back out as tabular data

Expected fields from the current scripts:

- `Unit Cost`
- `Quantity`
- `Total Cost`
- `Description`
- `Unit`
- `Measure Basis`

Verified in:

- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/apply_estimation_mapping_csv.py`
- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/build_cost_estimate_from_xlsx.py`

Use:

- export for estimating and PM-facing cost tables
- export for Pixeltable ingest when the goal is price-per-object or
  grouped-class estimate rows

Priority: **export**

### 2. Plant and site source records

#### `Plant Record`

Why it matters:

- this is the native Vectorworks plant metadata record surface
- it is the best source for plant-specific object attributes already known to
  VW, separate from our custom pricing record

Verified reader script:

- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/read_plant_records.py`

Use:

- export when reconciling species/style/object metadata with pricing
- export when comparing native VW plant data against custom MARPA records

Priority: **export**

#### `Plant`

Why it matters:

- this is the plug-in parameter record for Plant objects
- useful for object-type parameters, but often more Vectorworks-internal than
  `Plant Record`

Use:

- export when debugging how plant instances are actually parameterized
- secondary to `Plant Record` for estimating

Priority: **optional**

#### `Existing Tree`

Why it matters:

- this is a real object family in the active Data Manager and IFC mapping work
- useful for site inventory, survey alignment, and tree-specific quantities

Verified in current mapping specs/docs:

- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/build_farber_haines_data_manager_spec.py`
- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/docs/farber-haines-current-project-settings-audit.md`

Use:

- export when reconciling existing-tree objects with survey/site inventory
- export when checking Data Manager / IFC mapping on tree objects

Priority: **export**

#### `Landscape Area`

Why it matters:

- this is a native landscape/site object family relevant to area-based
  quantities and planting coverage

Use:

- export if the estimate needs area-driven planting or ground-plane scope
- useful for landscape-area-based quantity checks

Priority: **export if used in file**

### 3. MARPA custom IFC/data-manager records

These are custom record-backed Pset surfaces we created to support object
metadata, source tracking, QA, and export alignment.

Verified bootstrap source:

- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/bootstrap_farber_haines_marpa_psets.py`

#### `VwPset_MARPA_Cost`

Use:

- cost-specific custom fields separate from native `Project Cost`
- useful when aligning Data Manager / IFC export with pricing semantics

Priority: **export**

#### `VwPset_MARPA_Object`

Use:

- object identity / traceability / metadata
- useful for downstream matching and QA

Priority: **export**

#### `VwPset_MARPA_Plant`

Use:

- custom plant metadata
- useful for plant-specific downstream mapping

Priority: **export**

#### `VwPset_MARPA_Source`

Use:

- provenance and source traceability
- useful for QA and explaining where price/object mappings came from

Priority: **export**

#### `VwPset_MARPA_ExportQA`

Use:

- export QA flags
- useful to prove what was ready, missing, or suspect at export time

Priority: **export**

#### `VwPset_MARPA_Maintenance`

Use:

- only if maintenance scope is being modeled

Priority: **optional**

### 4. Mostly non-estimating record noise

These are generally not the right first exports for the pricing loop:

- `North Arrow`
- `Title Block Border`
- `Data Tag`
- `Reference Marker`
- `Revision Cloud`
- `Drawing Label`
- `Callout`
- `Scale Bar`
- most `AC_*` entries

Why they are low value:

- annotation or title-block metadata
- drawing-sheet support objects
- not core cost, plant, survey, or site semantics

Priority: **ignore for first-pass estimating workflow**

## Recommended Export Set For Farber-Haines

If the goal is the Vectorworks-to-spreadsheet/pricing loop, export these first:

1. `Project Cost`
2. `Plant Record`
3. `Existing Tree`
4. `Landscape Area` if landscape areas are in active estimating scope
5. `VwPset_MARPA_Cost`
6. `VwPset_MARPA_Object`
7. `VwPset_MARPA_Plant`
8. `VwPset_MARPA_Source`
9. `VwPset_MARPA_ExportQA`

Secondary/debug exports:

1. `Plant`
2. `VwPset_MARPA_Maintenance`

Ignore on first pass:

1. annotation/tag/title-block records
2. `AC_*` records unless debugging a specific plug-in object

## Downstream Use In This Project

### For pricing and PM spreadsheet outputs

Primary export:

- `Project Cost`

Why:

- it already contains the object-level pricing payload we are writing and
  validating

### For plant/site reconciliation

Primary exports:

- `Plant Record`
- `Existing Tree`
- `Landscape Area`

Why:

- these capture native site/plant object data that complements custom cost
  records

### For IFC/Data Manager traceability

Primary exports:

- `VwPset_MARPA_Object`
- `VwPset_MARPA_Plant`
- `VwPset_MARPA_Cost`
- `VwPset_MARPA_Source`
- `VwPset_MARPA_ExportQA`

Why:

- these provide the custom metadata layer that bridges VW object data,
  downstream QA, and Pixeltable traceability

## Practical Conclusion

The screenshot is useful because it proves the Farber-Haines file already
contains the record surfaces we care about.

The highest-value export from that menu for the estimating workflow is:

- `Project Cost`

The next most useful exports are:

- `Plant Record`
- `Existing Tree`
- `Landscape Area`
- the `VwPset_MARPA_*` records

This menu should be treated as the **tabular record export lane**, not the IFC
lane. It is the right surface for exporting pricing and object metadata tables,
while IFC remains the right surface for geometry and semantic model exchange.
