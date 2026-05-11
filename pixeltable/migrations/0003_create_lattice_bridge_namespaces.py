"""Create `lattice/bridge` and its 7 sub-namespaces.

Sub-namespaces (per spec §2):
    vw, ifc, itwin, marpa, semantic, evidence, health

Tables for each are created in the next set of migrations (0004-0010).
"""

from __future__ import annotations

from migrations._helpers import (
    OWNED_BRIDGE_SUBS,
    OWNED_PARENTS,
    assert_ownership,
    banner,
    ensure_namespace,
)

MIGRATION_ID = "0003_create_lattice_bridge_namespaces"


def apply(pxt, dry_run: bool) -> dict:
    banner("0003 lattice/bridge sub-namespaces", dry_run=dry_run)
    assert_ownership(pxt, OWNED_PARENTS + OWNED_BRIDGE_SUBS)

    out: dict = {}
    for ns in ("lattice/bridge", *OWNED_BRIDGE_SUBS):
        action = ensure_namespace(pxt, ns, dry_run)
        out[ns] = action
        print(f"  {ns:32s} -> {action}")
    return out
