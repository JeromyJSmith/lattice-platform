# Farber-Haines Fit To Project Georef

Date: 2026-05-16

Once a real point-pair solve exists, the next step is to upgrade the live
`project_georef` row with the VW transform evidence. That is now handled by:

- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/pixeltable/scripts/apply_farber_haines_georef_fit.py`

Expected inputs:

- `/tmp/farber_haines_georef_fit.json`
- `/tmp/farber_haines_georef_binding_candidate.json` (optional but preferred)
- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/projects/farber-haines-2521/georef.config.seed.json`

What it updates in `lattice.bridge.project_georef`:

- `config_version` -> `farber-haines-fit-candidate-v1`
- `vw_origin_x`
- `vw_origin_y`
- `vw_scale`
- `vw_rotation_deg`
- `vw_units`
- `transform_vw_to_wgs84`
- `notes`
- `updated_at`

What it intentionally does not claim:

- that the binding is final
- that Cesium alignment is verified
- that IFC georef is solved

This is a review-first upgrade of the live row, not the final word. The row
still needs visual and export validation after the fit is applied.

Safety guard:

- the script now refuses to apply a fit candidate when quality thresholds fail
- default thresholds are:
  - `rmse <= 5.0`
  - `max_residual <= 15.0`
- bypass is explicit with `--force`

Recommended direct invocation:

```bash
/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/pixeltable/.venv/bin/python \
  /Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/pixeltable/scripts/apply_farber_haines_georef_fit.py
```
