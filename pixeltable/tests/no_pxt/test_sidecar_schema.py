"""The sidecar JSON fixture must validate against contracts/sidecar.schema.json."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = _ROOT / "contracts" / "sidecar.schema.json"
FIXTURE_PATH = _ROOT / "fixtures" / "vwx-sidecar-mini.json"


def test_schema_file_is_valid_json():
    schema = json.loads(SCHEMA_PATH.read_text())
    assert schema.get("$schema")
    assert schema.get("title")


def test_fixture_validates_against_schema():
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(SCHEMA_PATH.read_text())
    payload = json.loads(FIXTURE_PATH.read_text())
    jsonschema.validate(payload, schema)


def test_fixture_has_required_top_level_keys():
    payload = json.loads(FIXTURE_PATH.read_text())
    for k in ("schema_version", "vw_export_hash", "elements"):
        assert k in payload, f"missing {k!r} in fixture"
    assert isinstance(payload["elements"], list) and len(payload["elements"]) > 0
