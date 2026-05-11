"""Load mini fixtures into the live (or ephemeral) PXT home.

Reads `pixeltable/fixtures/*.json[l]` and writes them via in-process
upsert helpers. This is the same path CI smoke tests take, so it does not
require the FastAPI sidecar to be running.

Usage:
    uv run scripts/load_fixtures.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

from scripts._pxt_env import get_client  # noqa: E402

FIXTURES = _HERE.parent / "fixtures"


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        out.append(json.loads(line))
    return out


def load_runtime_events(pxt) -> int:
    from service.upsert import upsert_runtime_event

    path = FIXTURES / "runtime-run-mini.jsonl"
    if not path.exists():
        print(f"  skip {path.name}: not present")
        return 0
    events = _load_jsonl(path)
    for evt in events:
        upsert_runtime_event(pxt, evt)
    print(f"  loaded {len(events)} runtime events from {path.name}")
    return len(events)


def load_sidecar(pxt) -> int:
    from service.upsert import upsert_vw_sidecar

    path = FIXTURES / "vwx-sidecar-mini.json"
    if not path.exists():
        print(f"  skip {path.name}: not present")
        return 0
    payload = json.loads(path.read_text())
    upsert_vw_sidecar(pxt, payload)
    print(f"  loaded sidecar {payload.get('vw_export_hash')!r}")
    return 1


def load_itwin_sync(pxt) -> int:
    from service.upsert import upsert_itwin_sync_job

    path = FIXTURES / "itwin-sync-job-mini.json"
    if not path.exists():
        print(f"  skip {path.name}: not present")
        return 0
    payload = json.loads(path.read_text())
    upsert_itwin_sync_job(pxt, payload)
    print(f"  loaded itwin sync job {payload.get('sync_run_id')!r}")
    return 1


def load_itwin_changed_elements(pxt) -> int:
    from service.upsert import upsert_itwin_changed_elements

    path = FIXTURES / "itwin-changed-elements-mini.json"
    if not path.exists():
        print(f"  skip {path.name}: not present")
        return 0
    payload = json.loads(path.read_text())
    out = upsert_itwin_changed_elements(pxt, payload)
    n = int(out.get("inserted", 0))
    print(f"  loaded {n} changed elements from {path.name}")
    return n


def load_marpa_parse_run(pxt) -> int:
    from service.marpa_runner import run_marpa
    from service.upsert import upsert_marpa_parse_run

    path = FIXTURES / "marpa-parse-run-mini.json"
    if not path.exists():
        print(f"  skip {path.name}: not present")
        return 0
    payload = json.loads(path.read_text())
    tokens = payload.get("input_tokens") or []
    res = run_marpa(tokens)
    upsert_marpa_parse_run(
        pxt,
        {
            "vw_export_hash": payload.get("vw_export_hash", ""),
            "source_element_id": payload.get("source_element_id", ""),
            "pset_name": payload.get("pset_name", ""),
            "record_kind": payload.get("record_kind", ""),
            "input_tokens": tokens,
            "parse_status": res.parse_status,
            "ambiguity_score": res.ambiguity_score,
            "marpa_record": res.record or {},
            "error_message": res.error_message,
            "harness_run_id": payload.get("harness_run_id", ""),
            "runner_kind": res.runner_kind,
            "grammar_version": "marpa.landscape.v1.0.0",
        },
    )
    print(f"  loaded marpa parse run status={res.parse_status} runner={res.runner_kind}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--direct",
        action="store_true",
        default=True,
        help="write via in-process upsert helpers (default)",
    )
    parser.parse_args()

    pxt = get_client()
    print("loading fixtures...")
    load_runtime_events(pxt)
    load_sidecar(pxt)
    load_itwin_sync(pxt)
    load_itwin_changed_elements(pxt)
    load_marpa_parse_run(pxt)
    print("done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
