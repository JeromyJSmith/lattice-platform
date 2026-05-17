# Farber-Haines Georef Evidence Register

Date: 2026-05-16

Farber-Haines should not rely on one georef source. The project needs a stacked
evidence model:

- survey corners and stake coordinates
- parcel boundary geometry
- OSM context
- plan image overlays
- IFC and iTwin / three.js visual checks
- eventual Gaussian splat alignment

To support that, we now generate:

- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/georef/converters/build_farber_haines_georef_evidence_register.py`

Default output:

- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/projects/farber-haines-2521/georef.evidence.register.json`

This is not a replacement for `georef.config.json`. It is the broader source
register that tracks which coordinate evidence exists, which is provisional,
and which still needs to be collected.

Recommended truth priority for this project:

1. survey corners and stake coordinates
2. parcel boundary shapefile / GeoJSON / KML
3. IFC and image overlay visual verification in iTwin / three.js
4. OSM context
5. Gaussian splat alignment as a later reality layer
