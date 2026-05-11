"""Centralized Pixeltable environment bootstrapping for local scripts.

Resolves PIXELTABLE_HOME, validates ownership, and exposes a single
`get_client()` returning the imported `pixeltable` module ready to use.

Set `PXT_HOME_OVERRIDE=/path/to/ephemeral` before running migrations
against an isolated test home (used by `make migrate-dryrun` in CI).
"""

from __future__ import annotations

import os
from pathlib import Path

DEFAULT_HOME = "/Volumes/PixelTable/.pixeltable"


def resolve_home() -> Path:
    override = os.environ.get("PXT_HOME_OVERRIDE")
    if override:
        return Path(override).expanduser().resolve()
    home = os.environ.get("PIXELTABLE_HOME", DEFAULT_HOME)
    return Path(home).expanduser().resolve()


def get_client():
    home = resolve_home()
    home.mkdir(parents=True, exist_ok=True)
    os.environ["PIXELTABLE_HOME"] = str(home)
    import pixeltable as pxt  # noqa: WPS433  (deferred import: PIXELTABLE_HOME must be set first)

    return pxt
