# 3D Asset Pipeline — Photo → GLB → Vectorworks Plant Style

This folder is the canonical reference and script home for generating custom 3D plant assets
from photographs and ingesting them into the LATTICE platform.

---

## Workflow Overview

```
Photo (JPG/PNG/WEBP)
  │
  ▼
TRELLIS.2 on MPS  ──── trellis_server.py @ localhost:8766
  │
  ├── model.glb   (PBR baked, ~10-30 MB)
  └── model.obj   (mesh + UVs, ~15-90 MB)
  │
  ▼
scripts/convert_formats.py  (Blender headless)
  │
  ├── {species}.glb    → assets/plants/lod-300/
  ├── {species}.fbx    → exports/fbx/
  ├── {species}.usdc   → exports/usd/
  └── {species}.usdz   → exports/usdz/
  │
  ▼
scripts/ingest_trellis_glb.py
  │
  └── Pixeltable: lattice/bridge/plant_assets
        lod_300_glb    = "assets/plants/lod-300/{species}.glb"
        vw_style_name  = "{Vectorworks Plant Style name}"
        asset_source   = "trellis"
        species_code   = "{code}"
        ...
  │
  ▼
Vectorworks Plant Style Manager
  └── Match by vw_style_name → attach 3D symbol geometry from GLB
```

---

## Step 1 — Generate the GLB

**Server URL:** `http://127.0.0.1:8766`

1. Open `http://127.0.0.1:8766` in your browser.
2. Drag a photo onto the upload zone — JPG, PNG, or WEBP. Best results with a clean subject on
   a plain/white background. Square crop or background-removed PNG is ideal.
3. Set seed (default 42). Hit **Generate**.
4. Monitor the log. Three sampling stages run (~2–3 min each on M3 Max):
   - Sparse structure sampling (12 steps)
   - Shape SLat sampling (12 steps)
   - Texture SLat sampling (12 steps)
   Then silent mesh extraction + Metal PBR baking (~5–15 min depending on complexity).
5. When complete, `model.glb` appears in the gallery. Click to preview, or copy directly:

```
/Volumes/PixelTable/MARPA_918_JUNIPER/experiments/trees_sage/trellis_outputs/{job_id}/model.glb
/Volumes/PixelTable/MARPA_918_JUNIPER/experiments/trees_sage/trellis_outputs/{job_id}/model.obj
```

**Start the server (if not running):**
```bash
cd /Volumes/PixelTable/MARPA_918_JUNIPER/experiments/trees_sage
uv run trellis_server.py
```

The server uses `HF_HUB_CACHE=/Volumes/PixelTable/models/huggingface-cache` and
`HF_HUB_OFFLINE=1` — all inference is 100% local, no network calls.

---

## Step 2 — Convert Formats

Run the headless Blender converter to produce all export formats from a single GLB:

```bash
python scripts/convert_formats.py \
  --glb /path/to/model.glb \
  --species-code "PLAT_ACE" \
  --out-dir exports/
```

Outputs:
| File | Format | Use |
|------|--------|-----|
| `exports/fbx/PLAT_ACE.fbx` | FBX 7.4 binary | 3ds Max, Maya, Cinema 4D import |
| `exports/usd/PLAT_ACE.usdc` | USD crate | USD pipeline / Omniverse |
| `exports/usdz/PLAT_ACE.usdz` | USDZ | AR Quick Look on iOS/macOS |
| `assets/plants/lod-300/PLAT_ACE.glb` | GLB | iTwin viewer, Pixeltable, web |

Requires Blender on PATH:
```bash
which blender   # → /opt/homebrew/bin/blender
```

---

## Step 3 — Ingest into Pixeltable

```bash
PIXELTABLE_HOME=/Volumes/PixelTable/.pixeltable \
PYTHONPATH=/Volumes/PixelTable/schemas \
python scripts/ingest_trellis_glb.py \
  --glb exports/PLAT_ACE.glb \
  --species-code "PLAT_ACE" \
  --common-name "Sycamore" \
  --scientific-name "Platanus acerifolia" \
  --vw-style-name "Sycamore 40'" \
  --mature-height 12.0 \
  --crown-radius 5.0
```

This upserts a row into `lattice/bridge/plant_assets` with:
- `lod_300_glb` pointing to the GLB in `assets/plants/lod-300/`
- `vw_style_name` linking back to the VW Plant Style Manager entry
- `asset_source = "trellis"` — tracks provenance

---

## Step 4 — Vectorworks Plant Style Manager

1. In VW 2026, open **Resource Manager** → Plant Styles.
2. Find or create the style matching `vw_style_name` from Step 3.
3. In the style definition, go to **3D** tab → **3D Geometry** → **Import Symbol**.
4. Import `assets/plants/lod-300/{species_code}.glb`.
5. Set **Crown Radius** and **Height** to match the Pixeltable values.
6. The VW bridge MCP (`vw.get_record_data`) will read `vw_style_name` from
   `lattice/bridge/plant_assets` to match elements in the drawing back to this asset.

---

## Planned iTwin UI

A dedicated route `src/routes/assets/generate.tsx` will expose the full pipeline
as a first-class UI panel inside the iTwin app:

```
┌─────────────────────────────────────────────┐
│  3D Asset Generator                          │
│                                              │
│  [📷 Drop image here]                        │
│                                              │
│  Species code  [________]                    │
│  Common name   [________]                    │
│  VW Style      [________]                    │
│  Height (m)    [___]  Crown (m) [___]        │
│                                              │
│  [Generate]  ← calls POST /api/trellis/job   │
│                                              │
│  Progress log (live SSE stream)              │
│  ──────────────────────────────              │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░             │
│                                              │
│  Export  [GLB] [FBX] [USDZ] [OBJ]           │
│  [Ingest to Pixeltable]                      │
│  [Sync to VW Plant Style]                    │
│                                              │
│  ┌──────────────────────────────┐            │
│  │  ThatOpen 3D preview         │            │
│  │  (model.glb rendered live)   │            │
│  └──────────────────────────────┘            │
└─────────────────────────────────────────────┘
```

Backend endpoint: `pixeltable/service/routers/trellis.py` — proxies to the
TRELLIS server on port 8766, streams SSE log updates, triggers format conversion
and Pixeltable ingest on completion.

---

## Pixeltable Schema Reference

Table: `lattice/bridge/plant_assets`

| Column | Type | Notes |
|--------|------|-------|
| `asset_id` | String | UUID |
| `species_code` | String | Short code, e.g. `PLAT_ACE` |
| `common_name` | String | e.g. `Sycamore` |
| `scientific_name` | String | e.g. `Platanus acerifolia` |
| `lod_100_glb` | String | Path to spike geometry placeholder |
| `lod_300_glb` | String | Path to TRELLIS-generated realistic GLB |
| `lod_300_c4d` | String | Path to Cinema 4D file if it exists |
| `mature_height_m` | Float | Used by VW plugin and iTwin viewer |
| `crown_radius_m` | Float | Used by shadow calc and VW |
| `canopy_density` | Float | 0.0–1.0, shadow occlusion factor |
| `asset_source` | String | `trellis` / `comfyui` / `manual` / `laubwerk` |
| `vw_style_name` | String | Exact VW Plant Style Manager name |
| `comfyui_workflow_id` | String | FK → genai/comfyui_jobs if applicable |
| `is_custom` | Bool | True for site-specific assets |

---

## Asset Folder Layout

```
3d_assets/
├── README.md               ← this file
├── source_images/          ← drop reference photos here before generating
├── exports/
│   ├── fbx/               ← FBX exports by species code
│   ├── usd/               ← USDC exports
│   └── usdz/              ← USDZ for AR / iOS Quick Look
└── scripts/
    ├── convert_formats.py  ← Blender headless converter
    └── ingest_trellis_glb.py ← Pixeltable ingest
```

Actual GLBs for the iTwin viewer live in `../assets/plants/lod-300/`.

---

## MARPA Live Farber-Haines Palette

Target: ~20 GLBs for the full site palette. Generated via TRELLIS, ingested here.

| Species Code | Common Name | VW Style Name | GLB Done |
|---|---|---|---|
| `JUNI_VIR` | Eastern Red Cedar | Juniperus 12' | |
| `PLAT_ACE` | Sycamore | Sycamore 40' | |
| `QUER_ROB` | English Oak | Oak 30' | |
| `PRUN_CER` | Cherry | Cherry 20' | |
| `ACER_RUB` | Red Maple | Maple 25' | |
| `TAXO_DIS` | Bald Cypress | Bald Cypress 35' | |
| `MAGN_GRA` | Southern Magnolia | Magnolia 30' | |
| `ILEX_OPA` | American Holly | Holly 15' | |
| `CORN_FLO` | Flowering Dogwood | Dogwood 15' | |
| `FAGU_SYL` | European Beech | Beech 40' | |
