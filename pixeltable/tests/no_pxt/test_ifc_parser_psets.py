"""IFC parser pure-Python helpers — pset classification.

These do NOT require ifcopenshell to be importable; we exercise only the
helpers that classify pset names against grammars/marpa_seed_psets.yaml.
"""

from __future__ import annotations

import pytest


def _load_helpers_or_skip():
    try:
        from service.ifc_parser import _classify_pset, _load_seed_config
    except ImportError as exc:
        pytest.skip(f"ifc_parser helpers unavailable: {exc}")
    return _classify_pset, _load_seed_config


def test_seed_config_loads():
    _classify_pset, _load_seed_config = _load_helpers_or_skip()
    cfg = _load_seed_config()
    assert isinstance(cfg, dict)
    # _load_seed_config always normalizes to the canonical nested shape.
    assert "seeds" in cfg
    assert "default_record_kind" in cfg
    assert isinstance(cfg["seeds"], dict)


def test_unknown_pset_falls_back_to_default():
    _classify_pset, _load_seed_config = _load_helpers_or_skip()
    cfg = _load_seed_config()
    is_seed, kind, sel_keys = _classify_pset("Pset_RandomVendorThing_Unrelated", cfg)
    assert is_seed is False
    assert isinstance(kind, str)
    assert sel_keys == []


def test_seed_pset_round_trip():
    """If the seed config defines any pset, we must classify it as a seed."""
    _classify_pset, _load_seed_config = _load_helpers_or_skip()
    cfg = _load_seed_config()
    seeds = cfg.get("seeds") or {}
    found_any = False
    for record_kind, group in seeds.items():
        for entry in (group or []):
            pset_name = entry.get("pset_name")
            if not pset_name:
                continue
            is_seed, kind, _ = _classify_pset(pset_name, cfg)
            assert is_seed is True
            assert kind == record_kind
            found_any = True
            break
        if found_any:
            break
    if not found_any:
        pytest.skip("seed config has no entries to round-trip")
