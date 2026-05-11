"""Pytest configuration shared across all bridge tests.

We intentionally split tests into two tiers:

* `tests/no_pxt/` — pure-Python tests that import the service modules but
  never touch the live Pixeltable volume. These run on every PR.

* `tests/pxt/`    — full integration tests that spin up an ephemeral
  PXT_HOME, run all migrations, and exercise upsert helpers against
  real tables. These run nightly + manually via `make test`.

Both tiers share fixtures defined here.
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
sys.path.insert(0, str(_ROOT))


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    """Path to pixeltable/fixtures/ where canonical mini fixtures live."""
    return _ROOT / "fixtures"


@pytest.fixture(scope="session")
def grammars_dir() -> Path:
    return _ROOT / "grammars"


@pytest.fixture()
def ephemeral_pxt_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Ephemeral PXT_HOME under pytest tmp; never touches live volume."""
    home = tmp_path / "pxt-home"
    home.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("PXT_HOME_OVERRIDE", str(home))
    monkeypatch.setenv("PIXELTABLE_HOME", str(home))
    return home


def pytest_collection_modifyitems(config, items):
    """Auto-mark tests by directory so `-m "not pxt"` skips integration tier.

    Anything under ``tests/pxt/`` gets ``@pytest.mark.pxt``; anything under
    ``tests/no_pxt/`` gets ``@pytest.mark.no_pxt``. Tests outside both
    directories are left untouched.
    """
    pxt_root = (_HERE / "pxt").resolve()
    no_pxt_root = (_HERE / "no_pxt").resolve()
    for item in items:
        try:
            p = Path(str(item.fspath)).resolve()
        except Exception:
            continue
        if pxt_root in p.parents or p == pxt_root:
            item.add_marker(pytest.mark.pxt)
        elif no_pxt_root in p.parents or p == no_pxt_root:
            item.add_marker(pytest.mark.no_pxt)
