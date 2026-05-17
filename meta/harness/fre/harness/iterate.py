# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import contextlib
import json
import os
import subprocess
from pathlib import Path

from lib import current_run_dir
from lib import ensure_run_dir
from lib import evaluate_data
from lib import propose_repairs_data
from lib import read_yaml
from lib import session_summary_path
from lib import write_determinism_check
from lib import write_input_manifest
from lib import write_json
from lib import write_normalized_source_summary
from lib import write_real_fixture_evaluation_artifacts
from lib import write_research_grounding_summary
from lib import write_session_summary
from lib import write_text
from lib import write_yaml
from lib import check_all_schemas
from lib import validate_examples_data
from lib import FRE_ROOT

LOCK_PATH = "/tmp/fre-meta-harness.lock"
COMMIT_THRESHOLD = 3


@contextlib.contextmanager
def run_context(run_id: str):
    original = os.environ.get("FRE_RUN_ID")
    os.environ["FRE_RUN_ID"] = run_id
    try:
        yield
    finally:
        if original is None:
            os.environ.pop("FRE_RUN_ID", None)
        else:
            os.environ["FRE_RUN_ID"] = original


def next_run_id() -> str:
    runs_dir = FRE_ROOT / "runs"
    existing = sorted(path.name for path in runs_dir.iterdir() if path.is_dir() and path.name.startswith("RUN-"))
    last = existing[-1] if existing else "RUN-2026-05-16-0000"
    prefix, number = last.rsplit("-", 1)
    return f"{prefix}-{int(number) + 1:04d}"


def latest_scored_run() -> tuple[str | None, int]:
    latest_run = None
    latest_score = -1
    for path in sorted((FRE_ROOT / "runs").glob("RUN-*")):
        score_path = path / "scorecard.yaml"
        if not score_path.exists():
            continue
        payload = read_yaml(score_path)
        if int(payload.get("blocking_failed_gates", 0)) != 0:
            continue
        artifacts = payload.get("required_run_artifacts", {})
        if not artifacts or not all(bool(value) for value in artifacts.values()):
            continue
        score = int(payload.get("total_score", -1))
        latest_run = path.name
        latest_score = score
    return latest_run, latest_score


def write_reports(payload: dict, repairs: list[dict]) -> None:
    decision = payload["promotion_decision"]
    lines = [f"# Report {os.environ['FRE_RUN_ID']}", "", "## Gate Results", ""]
    for gate in payload["gate_results"]:
        lines.append(f"- `{gate['gate_id']}`: `{gate['status']}` — {gate['reason']}")
    lines.extend(["", "## Repair Tasks", ""])
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
    write_text(current_run_dir() / "report.md", "\n".join(lines) + "\n")
    write_text(
        current_run_dir() / "promotion-decision.md",
        (
            f"# Promotion Decision {os.environ['FRE_RUN_ID']}\n\n"
            f"- Status: `{decision['status']}`\n"
            f"- Total score: `{decision['total_score']}`\n"
            f"- Summary: {decision['summary']}\n"
        ),
    )


def execute_cycle(run_id: str) -> dict:
    with run_context(run_id):
        ensure_run_dir()
        write_input_manifest()
        write_normalized_source_summary()
        write_research_grounding_summary()
        write_determinism_check()
        write_real_fixture_evaluation_artifacts()
        write_json(current_run_dir() / "schema-validation.json", check_all_schemas())
        write_json(current_run_dir() / "example-validation.json", validate_examples_data())
        payload = evaluate_data()
        repairs = propose_repairs_data(payload["gate_results"])
        payload["scorecard"]["metrics"]["repair_task_count"] = len(repairs)
        write_json(current_run_dir() / "gate-results.json", payload["gate_results"])
        write_yaml(current_run_dir() / "scorecard.yaml", payload["scorecard"])
        write_yaml(current_run_dir() / "repair-tasks.yaml", {"repair_tasks": repairs})
        write_reports(payload, repairs)
        write_session_summary(payload, repairs)
        final_payload = evaluate_data()
        final_repairs = propose_repairs_data(final_payload["gate_results"])
        final_payload["scorecard"]["metrics"]["repair_task_count"] = len(final_repairs)
        write_yaml(current_run_dir() / "scorecard.yaml", final_payload["scorecard"])
        write_yaml(current_run_dir() / "repair-tasks.yaml", {"repair_tasks": final_repairs})
        write_reports(final_payload, final_repairs)
        write_session_summary(final_payload, final_repairs)
        return {
            "run_id": run_id,
            "total_score": final_payload["promotion_decision"]["total_score"],
            "blocking_failed_gates": final_payload["scorecard"]["blocking_failed_gates"],
            "decision": final_payload["promotion_decision"]["status"],
            "session_summary": session_summary_path(run_id).relative_to(FRE_ROOT).as_posix(),
        }


def maybe_commit() -> str | None:
    status = subprocess.run(
        ["git", "-C", str(FRE_ROOT.parents[2]), "status", "--short", "meta/harness/fre"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    if not status:
        return None
    subprocess.run(["bash", "scripts/pre-commit-docs-check.sh"], cwd=FRE_ROOT.parents[2], check=True)
    subprocess.run(["git", "-C", str(FRE_ROOT.parents[2]), "add", "meta/harness/fre"], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(FRE_ROOT.parents[2]),
            "commit",
            "-m",
            "feat(meta-harness): accept three consecutive fre kernel improvements",
        ],
        check=True,
    )
    head = subprocess.run(
        ["git", "-C", str(FRE_ROOT.parents[2]), "rev-parse", "--short", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    return head


def main() -> None:
    previous_run, previous_score = latest_scored_run()
    accepted_improvements = 0
    cycle_results = []
    with open(LOCK_PATH, "w", encoding="utf-8") as lock_file:
        if os.name == "posix":
            import fcntl

            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        for _ in range(COMMIT_THRESHOLD):
            run_id = next_run_id()
            result = execute_cycle(run_id)
            result["score_before"] = previous_score
            result["improved"] = result["total_score"] > previous_score and result["blocking_failed_gates"] == 0
            cycle_results.append(result)
            if result["improved"]:
                accepted_improvements += 1
                previous_run = run_id
                previous_score = result["total_score"]
            else:
                break
    commit_sha = maybe_commit() if accepted_improvements >= COMMIT_THRESHOLD else None
    print(
        json.dumps(
            {
                "baseline_run": previous_run,
                "accepted_improvements": accepted_improvements,
                "commit_threshold": COMMIT_THRESHOLD,
                "commit_sha": commit_sha,
                "cycle_results": cycle_results,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
