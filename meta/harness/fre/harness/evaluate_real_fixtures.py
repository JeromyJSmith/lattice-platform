# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from lib import current_run_id
from lib import ensure_run_dir
from lib import write_input_manifest
from lib import write_normalized_source_summary
from lib import write_real_fixture_evaluation_artifacts


def main() -> None:
    ensure_run_dir()
    write_input_manifest()
    write_normalized_source_summary()
    write_real_fixture_evaluation_artifacts()


if __name__ == "__main__":
    main()
