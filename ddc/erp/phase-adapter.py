#!/usr/bin/env python3
"""Bridge: `lattice/bridge/ifc/ifc_elements` + Linear schedule → OpenConstructionERP 4D/5D phases.

For each project, read the current Linear schedule (start/end dates per phase),
join with the elements in that phase, and POST to the ERP's phase endpoint so
the 4D timeline view reflects current project state.

Tracked in meta/FEATURE_BACKLOG.md § DDC INTEGRATION → "OpenConstructionERP 4D/5D".
"""

from __future__ import annotations

import sys


def sync_phases(project_id: str) -> dict:
    raise NotImplementedError(
        "phase-adapter stub. See ddc/erp/README.md and "
        "meta/DDC_MAPPING.md § Repo 2."
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: phase-adapter.py <project_id>", file=sys.stderr)
        raise SystemExit(1)
    print(sync_phases(sys.argv[1]))
