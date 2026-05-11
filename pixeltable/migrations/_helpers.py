"""Shared helpers for idempotent Pixeltable migrations.

Pinned against pixeltable==0.6.0. All public functions here mirror the
proven patterns used in MARPA_PLATFORM/scripts/init_pixeltable.py:

  - `ensure_namespace(pxt, path, dry_run)`
  - `ensure_table(pxt, path, schema, dry_run)`

Plus an ownership invariant guard so this body cannot accidentally touch
namespaces it does not own.
"""

from __future__ import annotations

from typing import Any

OWNED_PARENTS: tuple[str, ...] = (
    "lattice/execution",
    "lattice/bridge",
    "lattice/genai",
    "lattice/reality",
)

OWNED_BRIDGE_SUBS: tuple[str, ...] = (
    "lattice/bridge/vw",
    "lattice/bridge/ifc",
    "lattice/bridge/itwin",
    "lattice/bridge/marpa",
    "lattice/bridge/semantic",
    "lattice/bridge/evidence",
    "lattice/bridge/health",
)

# Namespaces that other bodies own; we must never write to them.
FORBIDDEN_PREFIXES: tuple[str, ...] = (
    "marpa/",
    "lattice/source",
    "lattice/qa",
    "lattice/budget",
    "lattice/worksheet",
)


def ensure_namespace(pxt, path: str, dry_run: bool) -> str:
    existing = set(pxt.list_dirs())
    if path in existing:
        return "exists"
    if dry_run:
        return "would create"
    pxt.create_dir(path, if_exists="ignore")
    return "created"


def ensure_table(pxt, path: str, schema: dict[str, Any], dry_run: bool) -> str:
    parent = "/".join(path.split("/")[:-1])
    name = path.split("/")[-1]
    try:
        existing = {t.split("/")[-1] for t in pxt.list_tables(parent)}
    except Exception:
        existing = set()
    if name in existing:
        return "exists"
    if dry_run:
        return "would create"
    pxt.create_table(path, schema, if_exists="ignore")
    return "created"


def ensure_column(pxt, table_path: str, col_name: str, col_type, dry_run: bool) -> str:
    """Idempotent column add. Pixeltable's `add_column(if_exists='ignore')`
    is the underlying primitive; we wrap it to return a status string that
    matches the rest of the migration vocabulary ('exists' / 'would add' /
    'added')."""
    t = pxt.get_table(table_path)
    md = t.get_metadata() if hasattr(t, "get_metadata") else {}
    existing_cols = set(md.get("columns", {}).keys()) if isinstance(md, dict) else set()
    if col_name in existing_cols:
        return "exists"
    if dry_run:
        return "would add"
    t.add_column(if_exists="ignore", **{col_name: col_type})
    return "added"


def assert_ownership(pxt, owned: tuple[str, ...]) -> None:
    """Hard fail if `owned` overlaps another body's namespace tree."""
    for ns in owned:
        for forbidden in FORBIDDEN_PREFIXES:
            if ns == forbidden.rstrip("/") or ns.startswith(forbidden):
                raise RuntimeError(
                    f"Ownership violation: this body owns {owned!r} "
                    f"but {ns!r} overlaps forbidden prefix {forbidden!r}"
                )


def banner(title: str, *, dry_run: bool) -> None:
    suffix = " (dry-run)" if dry_run else ""
    print(f"\n--- {title}{suffix} ---")
