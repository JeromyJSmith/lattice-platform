#!/usr/bin/env -S uv run --project pixeltable python
"""Validate the DDC estimation contract schemas."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from lib import check_all_schemas


def main() -> None:
    """Print schema validation results as JSON."""

    print(json.dumps(check_all_schemas(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
