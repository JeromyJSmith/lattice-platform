#!/usr/bin/env python3
"""
Bulk-label MARPA Linear issues with Symphony agent-lane labels.

Usage:
    uv run python scripts/symphony-label-issues.py
    uv run python scripts/symphony-label-issues.py --commit

Environment:
    LINEAR_API_KEY must be set to a Linear personal API key.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


LINEAR_URL = "https://api.linear.app/graphql"
MARPA_TEAM_ID = "4d0b5918-13e2-4092-ad79-d5afa596529b"
DEFAULT_PAGE_SIZE = 100

LANE_LABELS = frozenset(
    {
        "codex",
        "copilot",
        "hermes",
        "claude-code",
        "warp-pi",
        "human-only",
    }
)

AREA_TO_LANE = {
    "data-layer": "codex",
    "itwin": "codex",
    "postgis": "codex",
    "georef": "codex",
    "devex": "copilot",
    "infra": "copilot",
    "docs": "copilot",
    "ci": "copilot",
    "meta-harness": "hermes",
    "knowledge-substrate": "hermes",
    "docs-harness": "hermes",
    "research": "hermes",
    "vw-bridge": "claude-code",
    "plant-geometry": "claude-code",
    "point-cloud": "claude-code",
    "3d-assets": "claude-code",
    "reality-capture": "claude-code",
    "3d-viewer": "claude-code",
    "analytics-layer": "claude-code",
    "agent-runtime": "claude-code",
    "rendering": "claude-code",
    "genai": "claude-code",
    "ddc": "hermes",
    "ddc-integration": "hermes",
    "admin": "hermes",
    "admin-dashboard": "hermes",
    "marpa-projects": "hermes",
}

FALLBACK_LANE = "claude-code"


@dataclass(frozen=True)
class LabelDecision:
    lane: str | None
    action: str
    reason: str
    matching_area_labels: tuple[str, ...]


def normalize_label(label: str) -> str:
    return label.strip().lower()


def linear_request(api_key: str, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = json.dumps({"query": query, "variables": variables or {}}).encode("utf-8")
    request = Request(
        LINEAR_URL,
        data=payload,
        headers={
            "Authorization": api_key,
            "Content-Type": "application/json",
        },
    )

    try:
        with urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Linear API HTTP {error.code}: {body}") from error
    except URLError as error:
        raise RuntimeError(f"Linear API request failed: {error.reason}") from error

    if data.get("errors"):
        raise RuntimeError(f"Linear GraphQL errors: {data['errors']}")
    return data.get("data", {})


def fetch_marpa_issues(
    api_key: str,
    team_id: str,
    page_size: int,
    limit: int | None,
) -> list[dict[str, Any]]:
    query = """
    query FetchMarpaIssues($teamId: ID!, $first: Int!, $after: String) {
      issues(
        filter: { team: { id: { eq: $teamId } } }
        first: $first
        after: $after
        orderBy: createdAt
      ) {
        nodes {
          id
          identifier
          title
          url
          state { name type }
          labels { nodes { id name } }
        }
        pageInfo { hasNextPage endCursor }
      }
    }
    """

    issues: list[dict[str, Any]] = []
    cursor: str | None = None

    while True:
        remaining = None if limit is None else limit - len(issues)
        if remaining is not None and remaining <= 0:
            break

        first = min(page_size, remaining) if remaining is not None else page_size
        data = linear_request(api_key, query, {"teamId": team_id, "first": first, "after": cursor})
        connection = data.get("issues", {})
        issues.extend(connection.get("nodes", []))

        page_info = connection.get("pageInfo", {})
        if not page_info.get("hasNextPage"):
            break
        cursor = page_info.get("endCursor")
        if not cursor:
            break

    return issues


def fetch_label_ids(api_key: str, team_id: str, required_labels: set[str]) -> dict[str, str]:
    query = """
    query FetchIssueLabels($teamId: ID!, $first: Int!, $after: String) {
      issueLabels(
        filter: { team: { id: { eq: $teamId } } }
        first: $first
        after: $after
      ) {
        nodes { id name }
        pageInfo { hasNextPage endCursor }
      }
    }
    """

    label_ids: dict[str, str] = {}
    cursor: str | None = None

    while True:
        data = linear_request(api_key, query, {"teamId": team_id, "first": 100, "after": cursor})
        connection = data.get("issueLabels", {})
        for label in connection.get("nodes", []):
            name = normalize_label(label.get("name", ""))
            if name in required_labels and name not in label_ids:
                label_ids[name] = label["id"]

        if required_labels <= label_ids.keys():
            break

        page_info = connection.get("pageInfo", {})
        if not page_info.get("hasNextPage"):
            break
        cursor = page_info.get("endCursor")
        if not cursor:
            break

    missing = sorted(required_labels - label_ids.keys())
    if missing:
        missing_text = ", ".join(missing)
        raise RuntimeError(f"Missing required Linear lane labels in MARPA team: {missing_text}")

    return label_ids


def decide_lane(label_names: list[str]) -> LabelDecision:
    normalized = sorted({normalize_label(name) for name in label_names})
    existing_lanes = tuple(label for label in normalized if label in LANE_LABELS)
    if existing_lanes:
        return LabelDecision(
            lane=None,
            action="skip",
            reason=f"already has lane label: {', '.join(existing_lanes)}",
            matching_area_labels=(),
        )

    matching_area_labels = tuple(label for label in normalized if label in AREA_TO_LANE)
    matching_lanes = sorted({AREA_TO_LANE[label] for label in matching_area_labels})

    if len(matching_lanes) == 1:
        return LabelDecision(
            lane=matching_lanes[0],
            action="label",
            reason=f"matched area labels: {', '.join(matching_area_labels)}",
            matching_area_labels=matching_area_labels,
        )

    if not matching_lanes:
        return LabelDecision(
            lane=FALLBACK_LANE,
            action="label",
            reason="no mapped area label; defaulted to claude-code",
            matching_area_labels=(),
        )

    return LabelDecision(
        lane=FALLBACK_LANE,
        action="label",
        reason=f"ambiguous mapped lanes {', '.join(matching_lanes)}; defaulted to claude-code",
        matching_area_labels=matching_area_labels,
    )


def add_issue_label(api_key: str, issue_id: str, label_id: str) -> None:
    mutation = """
    mutation AddIssueLabel($id: String!, $labelId: String!) {
      issueAddLabel(id: $id, labelId: $labelId) {
        success
      }
    }
    """
    data = linear_request(api_key, mutation, {"id": issue_id, "labelId": label_id})
    success = data.get("issueAddLabel", {}).get("success")
    if not success:
        raise RuntimeError(f"Linear issueAddLabel returned success={success!r}")


def build_rows(
    issues: list[dict[str, Any]],
    lane_label_ids: dict[str, str],
    api_key: str,
    dry_run: bool,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    for issue in issues:
        labels = issue.get("labels", {}).get("nodes", [])
        label_names = [label.get("name", "") for label in labels]
        decision = decide_lane(label_names)
        status = "dry-run" if dry_run else "committed"
        error = ""

        if decision.action == "label" and decision.lane and not dry_run:
            try:
                add_issue_label(api_key, issue["id"], lane_label_ids[decision.lane])
            except RuntimeError as exc:
                status = "error"
                error = str(exc)

        rows.append(
            {
                "identifier": issue.get("identifier", ""),
                "title": issue.get("title", ""),
                "state": issue.get("state", {}).get("name", ""),
                "current_labels": ", ".join(sorted(label_names)),
                "matching_area_labels": ", ".join(decision.matching_area_labels),
                "lane": decision.lane or "",
                "action": decision.action,
                "reason": decision.reason,
                "status": "skipped" if decision.action == "skip" else status,
                "error": error,
                "url": issue.get("url", ""),
            }
        )

        label = decision.lane or "none"
        print(f"{issue.get('identifier', 'UNKNOWN')}: {decision.action} {label} - {decision.reason}")

    return rows


def default_report_paths(repo_root: Path, date_text: str) -> tuple[Path, Path]:
    sessions_dir = repo_root / "meta" / "harness" / "docs" / "sessions"
    markdown = sessions_dir / f"{date_text}-lane-labeling-report.md"
    csv_path = sessions_dir / f"{date_text}-lane-labeling-report.csv"
    return markdown, csv_path


def write_csv(rows: list[dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "identifier",
        "title",
        "state",
        "current_labels",
        "matching_area_labels",
        "lane",
        "action",
        "reason",
        "status",
        "error",
        "url",
    ]
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(rows: list[dict[str, str]]) -> str:
    if not rows:
        return "_No issues found._\n"

    lines = [
        "| Issue | State | Action | Lane | Reason |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        issue = row["identifier"]
        if row["url"]:
            issue = f"[{issue}]({row['url']})"
        title = row["title"].replace("|", "\\|")
        reason = row["reason"].replace("|", "\\|")
        lane = row["lane"] or "-"
        action = row["action"]
        if row["status"] == "error":
            action = "error"
            reason = row["error"].replace("|", "\\|")
        lines.append(f"| {issue}: {title} | {row['state']} | {action} | {lane} | {reason} |")
    return "\n".join(lines) + "\n"


def write_markdown_report(
    rows: list[dict[str, str]],
    output_path: Path,
    csv_output_path: Path | None,
    dry_run: bool,
    team_id: str,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    counts = Counter(row["status"] for row in rows)
    lane_counts = Counter(row["lane"] for row in rows if row["lane"])
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lane_lines = ["| Lane | Count |", "|---|---:|"]
    for lane in sorted(lane_counts):
        lane_lines.append(f"| `{lane}` | {lane_counts[lane]} |")
    if not lane_counts:
        lane_lines.append("| _none_ | 0 |")

    summary = f"""---
type: session
date: {datetime.now(timezone.utc).strftime("%Y-%m-%d")}
phase: C
stage: "MARPA-378 lane labeling"
status: {"dry-run" if dry_run else "committed"}
---

# Symphony Lane Labeling Report

Generated by `scripts/symphony-label-issues.py` at {generated_at}.

## Summary

| Metric | Count |
|---|---:|
| Total issues processed | {len(rows)} |
| Dry-run rows | {counts.get("dry-run", 0)} |
| Committed rows | {counts.get("committed", 0)} |
| Skipped rows | {counts.get("skipped", 0)} |
| Error rows | {counts.get("error", 0)} |

## Lane assignments

{chr(10).join(lane_lines)}

## Run details

| Field | Value |
|---|---|
| Team ID | `{team_id}` |
| Mode | `{"dry-run" if dry_run else "commit"}` |
| CSV report | `{csv_output_path if csv_output_path else "disabled"}` |

## Issues

{markdown_table(rows)}
"""

    output_path.write_text(summary, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bulk-label MARPA Linear issues with Symphony lane labels.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", default=True, help="Preview changes without mutating Linear.")
    mode.add_argument("--commit", action="store_true", help="Apply lane labels in Linear.")
    parser.add_argument("--team-id", default=MARPA_TEAM_ID, help=argparse.SUPPRESS)
    parser.add_argument("--page-size", type=int, default=DEFAULT_PAGE_SIZE, help="Linear GraphQL page size.")
    parser.add_argument("--limit", type=int, default=None, help="Maximum number of issues to process.")
    parser.add_argument("--output", default=None, help="Markdown report path.")
    parser.add_argument("--csv-output", default=None, help="CSV report path. Use 'none' to disable CSV output.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    dry_run = not args.commit

    if args.page_size < 1 or args.page_size > 250:
        print("ERROR: --page-size must be between 1 and 250.", file=sys.stderr)
        return 2
    if args.limit is not None and args.limit < 1:
        print("ERROR: --limit must be greater than zero.", file=sys.stderr)
        return 2

    api_key = os.environ.get("LINEAR_API_KEY")
    if not api_key:
        print("ERROR: LINEAR_API_KEY environment variable not set.", file=sys.stderr)
        return 1

    repo_root = Path(__file__).resolve().parents[1]
    date_text = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    default_markdown, default_csv = default_report_paths(repo_root, date_text)
    output_path = Path(args.output).resolve() if args.output else default_markdown

    csv_output_path: Path | None
    if args.csv_output and args.csv_output.lower() == "none":
        csv_output_path = None
    elif args.csv_output:
        csv_output_path = Path(args.csv_output).resolve()
    else:
        csv_output_path = default_csv

    print(f"Mode: {'DRY RUN' if dry_run else 'COMMIT'}")
    print(f"Team ID: {args.team_id}")
    print("Resolving lane label IDs from Linear...")
    lane_label_ids = fetch_label_ids(api_key, args.team_id, set(LANE_LABELS))

    print("Fetching MARPA issues from Linear...")
    issues = fetch_marpa_issues(api_key, args.team_id, args.page_size, args.limit)
    print(f"Found {len(issues)} issues.")

    rows = build_rows(issues, lane_label_ids, api_key, dry_run)
    if csv_output_path:
        write_csv(rows, csv_output_path)
        print(f"CSV report written to: {csv_output_path}")
    write_markdown_report(rows, output_path, csv_output_path, dry_run, args.team_id)
    print(f"Markdown report written to: {output_path}")

    errors = sum(1 for row in rows if row["status"] == "error")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
