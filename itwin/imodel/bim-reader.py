"""Read `.bim` (iModel SQLite) files directly via Pixeltable @pxt.udf.

Stub. The full implementation is tracked under iTwin → ".bim source
ingestion" in meta/FEATURE_BACKLOG.md.

Why this is the right shape:
- .bim is a SQLite file with a published ECDb schema.
- We never want a second SQLite stack inside the sidecar fighting Pixeltable
  for the lock — so @itwin/core-backend stays out.
- A small `sqlite3.connect()` reader is enough to walk the
  `bis_GeometricElement3d` view and produce dicts ready for upsert into
  `lattice/bridge/ifc/ifc_elements`.

Usage (once wired):
    import pixeltable as pxt
    @pxt.udf
    def bim_to_ifc_elements(bim_path: str) -> list[dict]:
        return list(read_bim(bim_path))
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterator


def read_bim(bim_path: str | Path) -> Iterator[dict]:
    """Yield one dict per GeometricElement3d in the .bim file.

    NOT YET IMPLEMENTED. The fields below match the columns expected by
    `pixeltable/service/upsert.py::upsert_ifc_elements`.
    """
    raise NotImplementedError(
        "bim-reader stub. See meta/FEATURE_BACKLOG.md § iTWIN OPEN-SOURCE LAYER "
        "→ '.bim source ingestion' for the acceptance criteria."
    )

    # Sketch (uncomment + flesh out when implementing):
    # con = sqlite3.connect(f"file:{bim_path}?mode=ro", uri=True)
    # try:
    #     cur = con.cursor()
    #     cur.execute("""
    #         SELECT ECInstanceId, ECClassId, UserLabel, JsonProperties,
    #                Origin_X, Origin_Y, Origin_Z, Yaw, Pitch, Roll
    #         FROM bis_GeometricElement3d
    #     """)
    #     for row in cur:
    #         yield {
    #             "source_element_id": str(row[0]),
    #             "bis_class":         _resolve_class_name(con, row[1]),
    #             "bis_subclass":      "",  # filled by IFC enrichment agent
    #             "user_label":        row[2] or "",
    #             "raw_properties":    row[3],   # JSON blob
    #             "origin_x":          row[4],
    #             "origin_y":          row[5],
    #             "origin_z":          row[6],
    #             "yaw":               row[7],
    #             "pitch":             row[8],
    #             "roll":              row[9],
    #         }
    # finally:
    #     con.close()
