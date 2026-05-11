"""Walk all Plant Style instances in the active document and dump their records to JSON.

Output is appended to ~/.lattice/vw-records-{timestamp}.json so it can be
ingested by the sidecar's /v1/vw/sidecars endpoint.

Reference: vs.GetRecord, vs.GetParametricRecord, vs.GetCustomObjectProfileGroup.
"""

import json
import os
import time

import vs  # type: ignore[import]


PLANT_RECORD_NAME = "Plant Record"


def main() -> None:
    out = []
    h = vs.FSObject(vs.ActLayer())
    while h:
        rec = vs.GetRecord(h, vs.NumRecords(h))  # walks all attached records
        if rec and vs.GetName(rec) == PLANT_RECORD_NAME:
            out.append({
                "handle":   vs.GetEntityType(h),
                "x":        vs.GetEntPenLoc3D(h)[0],
                "y":        vs.GetEntPenLoc3D(h)[1],
                "z":        vs.GetEntPenLoc3D(h)[2],
                "species":  vs.GetRField(h, PLANT_RECORD_NAME, "LatinName"),
                "common":   vs.GetRField(h, PLANT_RECORD_NAME, "CommonName"),
            })
        h = vs.NextSObj(h)

    target_dir = os.path.expanduser("~/.lattice")
    os.makedirs(target_dir, exist_ok=True)
    path = os.path.join(target_dir, f"vw-records-{int(time.time())}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    vs.Message(f"wrote {len(out)} plant records to {path}")


if __name__ == "__main__":
    main()
