# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from lib import ensure_run_dir
from lib import evaluate_data
from lib import write_determinism_check
from lib import write_input_manifest
from lib import write_json
from lib import write_real_fixture_evaluation_artifacts
from lib import write_research_grounding_summary
from lib import write_normalized_source_summary
from lib import write_yaml


def main() -> None:
    ensure_run_dir()
    write_input_manifest()
    write_normalized_source_summary()
    write_research_grounding_summary()
    write_determinism_check()
    write_real_fixture_evaluation_artifacts()
    payload = evaluate_data()
    write_json(ensure_run_dir() / "gate-results.json", payload["gate_results"])
    write_yaml(ensure_run_dir() / "scorecard.yaml", payload["scorecard"])


if __name__ == "__main__":
    main()
