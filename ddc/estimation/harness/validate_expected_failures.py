#!/usr/bin/env -S uv run --project pixeltable python
"""Validate the DDC estimation expected-failure registry."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from lib import validate_expected_failures_data


def main() -> None:
    """Print expected-failure validation results as JSON."""

    print(json.dumps(validate_expected_failures_data(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
