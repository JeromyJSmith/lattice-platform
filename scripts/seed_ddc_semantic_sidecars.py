#!/usr/bin/env -S uv run --script
"""Seed DDC SKILL.md corpus via sidecar semantic seeding endpoint."""

from __future__ import annotations

import json
import os
from urllib.error import HTTPError
from urllib.request import Request, urlopen

BASE_URL = os.environ.get("PIXELTABLE_SERVICE_URL", "http://127.0.0.1:7770")


def main() -> int:
    req = Request(
        f"{BASE_URL}/v1/semantic/seed-ddc-skills",
        data=b"{}",
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urlopen(req) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        err = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"seed request failed ({exc.code}): {err}") from exc

    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

