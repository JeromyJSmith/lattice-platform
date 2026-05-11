# reality/mirror — Platform Sync State

The mirror enforces the LATTICE invariant: **one ground truth, everywhere, always in sync**. After any capture event (or VW design change, or BOQ refresh), every one of the 7 platform layers gets updated and `lattice/reality/mirror_state` records the result.

| Layer | What "synced" means |
|---|---|
| VW design | `vw_last_export_hash` matches latest IFC export |
| iTwin BIM | `bis_class` populated on every `ifc_elements` row |
| DDC ERP | `erp_boq_last_sync` is fresh (< 24 h) |
| Cesium globe | `cesium_globe_synced` true (pin colors current) |
| ThatOpen viewer | `thatopen_viewer_synced` true (Fragment cache current) |
| deck.gl analytics | `deckgl_layer_synced` true (Parquet exports current) |
| Potree tiles | `potree_tiles_synced` true (octree current) |

| File | Purpose |
|---|---|
| `sync-checker.py` | One-shot: compute all 7 flags for a project, write to mirror_state |
| `divergence-report.py` | CloudComPy C2C between design mesh + reality scan → `design_reality_divergence_m` |
| `platform-broadcaster.py` | After any capture event, POST SSE notifications to each subscribed layer |

The broadcaster is the fan-out hub. It writes one `lattice/execution/evidence` row per layer notified, so the operator can audit who got what when.

Tracked in the DIGITAL TWIN MIRROR section of [`meta/FEATURE_BACKLOG.md`](../../meta/FEATURE_BACKLOG.md).
