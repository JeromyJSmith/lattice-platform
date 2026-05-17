# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from lib import current_run_id
from lib import write_determinism_check
from lib import ensure_run_dir
from lib import evaluate_data
from lib import propose_repairs_data
from lib import write_input_manifest
from lib import write_real_fixture_evaluation_artifacts
from lib import write_research_grounding_summary
from lib import write_session_summary
from lib import write_normalized_source_summary
from lib import write_text
from lib import write_yaml


def write_report_artifacts(payload: dict, repairs: list[dict]) -> None:
    decision = payload["promotion_decision"]
    lines = [
        f"# Report {current_run_id()}",
        "",
        "## Gate Results",
        "",
    ]
    for gate in payload["gate_results"]:
        lines.append(f"- `{gate['gate_id']}`: `{gate['status']}` — {gate['reason']}")
    lines.extend(
        [
            "",
            "## Repair Tasks",
            "",
        ]
    )
    if repairs:
        for task in repairs:
            lines.append(f"- `{task['id']}`: {task['title']}")
    else:
        lines.append("- No repair tasks generated.")
    lines.extend(
        [
            "",
            "## Promotion Decision",
            "",
            f"- Status: `{decision['status']}`",
            f"- Total score: `{decision['total_score']}`",
            f"- Summary: {decision['summary']}",
            "",
        ]
    )
    write_text(ensure_run_dir() / "report.md", "\n".join(lines) + "\n")
    write_text(
        ensure_run_dir() / "promotion-decision.md",
        (
            f"# Promotion Decision {current_run_id()}\n\n"
            f"- Status: `{decision['status']}`\n"
            f"- Total score: `{decision['total_score']}`\n"
            f"- Summary: {decision['summary']}\n"
        ),
    )


def main() -> None:
    ensure_run_dir()
    write_input_manifest()
    write_normalized_source_summary()
    write_research_grounding_summary()
    write_determinism_check()
    write_real_fixture_evaluation_artifacts()
    initial_payload = evaluate_data()
    initial_repairs = propose_repairs_data(initial_payload["gate_results"])
    write_session_summary(initial_payload, initial_repairs)
    write_report_artifacts(initial_payload, initial_repairs)

    final_payload = evaluate_data()
    final_repairs = propose_repairs_data(final_payload["gate_results"])
    final_payload["scorecard"]["metrics"]["repair_task_count"] = len(final_repairs)
    write_yaml(ensure_run_dir() / "scorecard.yaml", final_payload["scorecard"])
    write_yaml(ensure_run_dir() / "repair-tasks.yaml", {"repair_tasks": final_repairs})
    write_session_summary(final_payload, final_repairs)
    write_report_artifacts(final_payload, final_repairs)
    write_text(
        ensure_run_dir() / "promotion-decision.md",
        (
            f"# Promotion Decision {current_run_id()}\n\n"
            f"- Status: `{final_payload['promotion_decision']['status']}`\n"
            f"- Total score: `{final_payload['promotion_decision']['total_score']}`\n"
            f"- Summary: {final_payload['promotion_decision']['summary']}\n"
        ),
    )


if __name__ == "__main__":
    main()
