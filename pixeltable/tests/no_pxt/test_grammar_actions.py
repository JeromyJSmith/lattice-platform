"""marpa.landscape.v1 actions are pure Python; test directly."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_ACTIONS_PATH = (
    Path(__file__).resolve().parents[2] / "grammars" / "marpa.landscape.v1.actions.py"
)
_MODULE_NAME = "marpa_actions_v1_test"


def _load_actions():
    """Load grammars/marpa.landscape.v1.actions.py for testing.

    Must register the module in `sys.modules` before `exec_module`, otherwise
    `@dataclass` inside the file fails with `'NoneType' object has no
    attribute '__dict__'` because CPython's dataclass machinery probes
    `sys.modules[cls.__module__]` for KW_ONLY detection.
    """
    cached = sys.modules.get(_MODULE_NAME)
    if cached is not None:
        return cached
    spec = importlib.util.spec_from_file_location(_MODULE_NAME, _ACTIONS_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[_MODULE_NAME] = mod
    try:
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
    except Exception:
        sys.modules.pop(_MODULE_NAME, None)
        raise
    return mod


@pytest.fixture(scope="module")
def actions():
    return _load_actions()


def test_planting_success(actions):
    res = actions.parse_record(
        ["planting", "Quercus", "agrifolia", "24-inch-box", "1", "'Heritage'", "notes:", "drought-tolerant"]
    )
    assert res.parse_status == "success"
    assert res.record["botanical_name"] == "Quercus agrifolia"
    assert res.record["cultivar"] == "Heritage"
    assert res.record["container_size"] == "24-inch-box"
    assert res.record["quantity"] == 1
    assert res.record["notes"] == "drought-tolerant"


def test_planting_partial_when_short(actions):
    res = actions.parse_record(["planting", "Quercus", "agrifolia"])
    assert res.parse_status == "partial"
    assert res.record == {"raw": ["planting", "Quercus", "agrifolia"]}


def test_irrigation_success(actions):
    res = actions.parse_record(["irrigation", "Z1", "12", "1.0GPH", "in-line"])
    assert res.parse_status == "success"
    assert res.record == {
        "kind": "irrigation",
        "zone": "Z1",
        "emitter_count": 12,
        "flow_rate": "1.0GPH",
        "drip_type": "in-line",
    }


def test_topography_success(actions):
    res = actions.parse_record(["topography", "3:1", "10.0", "13.0", "decomposed-granite"])
    assert res.parse_status == "success"
    assert res.record["slope"] == "3:1"
    assert res.record["material"] == "decomposed-granite"


def test_hardscape_success(actions):
    res = actions.parse_record(["hardscape", "concrete", "4.0", "8.0", "impermeable"])
    assert res.parse_status == "success"
    assert res.record["surface_type"] == "concrete"
    assert res.record["permeability"] == "impermeable"


def test_unknown_head_fails(actions):
    res = actions.parse_record(["nonsense", "a", "b", "c", "d"])
    assert res.parse_status == "fail"
    assert "unknown rule head" in res.error_message


def test_empty_tokens_fail(actions):
    res = actions.parse_record([])
    assert res.parse_status == "fail"
    assert "empty token stream" in res.error_message
