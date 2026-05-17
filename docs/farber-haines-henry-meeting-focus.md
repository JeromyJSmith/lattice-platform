# Farber-Haines Henry Meeting Focus

Date: 2026-05-16

## Core objective

We are building a Vectorworks-to-spreadsheet estimating loop for the
Farber-Haines project so designers and PMs can:

- work from the live model
- extract quantities by class/object
- attach price data from a budget workbook
- generate estimate outputs without rebuilding scope manually

## What is already working

- Vectorworks classes and objects have been mapped to budget pricing
- `Project Cost` record data is being written onto model objects
- class-level and object-level estimate exports are working
- estimate outputs are landing in Pixeltable
- the copied VWX file is now the safe destructive working surface:
  - `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/projects/vectorworks project files/_Farber-Haines [2521]__ESTIMATION_WORKING_COPY__2026-05-16.vwx`

## What is not yet solved

### 1. Document georeferencing

The current Farber-Haines document georef binding is unresolved.

Current evidence:

- `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/georef/document_georef_binding.json`
- `binding_status = unresolved`
- `allow_apply = false`

Meaning:

- a blind document-origin georef apply is known-bad
- we need a proper control-point-based binding for this file
- our georef automation is now intentionally fail-closed:
  - stale or synthetic selected-reference exports are rejected
  - bad fit candidates are blocked from writing into Pixeltable

### 2. IFC semantic richness

Headless IFC export now runs, but the current export is still semantically thin.

Current proof:

- `/tmp/farber_haines_ifc_probe/export_result.json`
- first successful probe IFC exists

But current exported entity coverage is still too shallow:

- `IfcProject = 1`
- `IfcSite = 1`
- `IfcSlab = 0`
- `IfcGeographicElement = 0`

Meaning:

- export mechanics are alive
- object/entity mapping for landscape content is not yet export-ready

## What we want from Henry

### On georeferencing

- best-practice method for binding a Landmark site file like this when the
  source geometry is early/schematic and the parcel/control truth is external
- whether Vectorworks expects this to be solved through document georef only,
  survey point workflow, layer georef workflow, or a combination

### On IFC export

- best-practice setup for exporting landscape objects so plants, hardscape,
  walls, edging, and site elements survive as meaningful IFC entities
- whether Data Manager is the intended production path for these object families
  in Landmark 2026, especially plant and geographic elements
- whether there are required export settings or layer-mapping behaviors that
  are easy to miss but necessary for semantic IFC output

### On estimating workflow

- recommended Vectorworks-native pattern for attaching external cost data to
  classes, plant styles, hardscape, and other site objects
- whether the preferred approach is:
  - worksheet reference plus lookup formulas
  - record formats
  - Data Manager mappings
  - or a hybrid

## The short version to say in the meeting

We already have the pricing loop working at the Vectorworks and Pixeltable
levels. The two blockers are georeference binding and richer IFC semantics.
The main thing we want from Vectorworks is the cleanest production-grade path
for:

1. document georeference setup for a landscape site file
2. Data Manager or export settings needed for meaningful IFC landscape output
3. best-practice attachment of external pricing data to model quantities
