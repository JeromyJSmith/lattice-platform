# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from lib import check_all_schemas
from lib import ensure_run_dir
from lib import write_input_manifest
from lib import write_json
from lib import write_research_grounding_summary
from lib import write_normalized_source_summary


def main() -> None:
    ensure_run_dir()
    write_input_manifest()
    write_normalized_source_summary()
    write_research_grounding_summary()
    write_json(ensure_run_dir() / "schema-validation.json", check_all_schemas())


if __name__ == "__main__":
    main()
