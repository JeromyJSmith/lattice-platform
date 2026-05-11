"""Create the top-level `lattice` namespace if absent.

`lattice` is shared with other bodies (e.g., `lattice/source` is owned
elsewhere). We only ensure the root exists; we never touch any sibling
sub-namespace not in OWNED_PARENTS / OWNED_BRIDGE_SUBS.
"""

from __future__ import annotations

from migrations._helpers import banner, ensure_namespace

MIGRATION_ID = "0001_create_lattice_root"


def apply(pxt, dry_run: bool) -> dict:
    banner("0001 lattice root", dry_run=dry_run)
    action = ensure_namespace(pxt, "lattice", dry_run)
    print(f"  lattice -> {action}")
    return {"lattice": action}
