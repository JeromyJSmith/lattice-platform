"""Numbered idempotent migrations.

Each module exports `MIGRATION_ID: str`, `apply(pxt, dry_run: bool) -> dict`
and is discovered by `scripts/bootstrap.py` in numerical order.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Protocol, cast
import importlib
import re

_NUMERIC = re.compile(r"^(\d{4})_[a-z0-9_]+\.py$")


class MigrationModule(Protocol):
    def apply(self, pxt: Any, dry_run: bool) -> dict[str, Any]:
        ...


def discover() -> list[tuple[str, str]]:
    """Return [(migration_id, dotted_module)] sorted by numeric prefix."""
    here = Path(__file__).parent
    out: list[tuple[str, str]] = []
    for path_entry in sorted(here.iterdir()):
        m = _NUMERIC.match(path_entry.name)
        if m:
            mod = f"migrations.{path_entry.stem}"
            out.append((m.group(1), mod))
    return out


def load_all() -> Iterable[tuple[str, MigrationModule]]:
    for mig_id, dotted in discover():
        module = importlib.import_module(dotted)
        apply_fn = getattr(module, "apply", None)
        if not callable(apply_fn):
            raise TypeError(f"{dotted} is missing callable apply(pxt, dry_run)")
        yield mig_id, cast(MigrationModule, module)
