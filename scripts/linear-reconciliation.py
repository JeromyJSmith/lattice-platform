#!/usr/bin/env python3
"""
LATTICE Linear Reconciliation Script (Stage 5b)

After the bulk GitHub import via Linear's native importer (Stage 5a),
this script reconciles each imported issue:
  1. Maps GitHub labels → canonical Linear labels (per sync-contract.md)
  2. Assigns each issue to a phase milestone based on label heuristics
  3. Sets priority from label heuristics
  4. Writes a back-link comment on the GitHub issue with the Linear ID
  5. Outputs a CSV report to meta/harness/docs/sessions/<date>-linear-import-reconciliation.md

Usage:
    uv run python scripts/linear-reconciliation.py --dry-run
    uv run python scripts/linear-reconciliation.py --commit

Environment variables required:
    LINEAR_API_KEY   — Linear personal API key (Settings → API → Personal API keys)
    GITHUB_TOKEN     — GitHub personal token with issues:write scope

Options:
    --dry-run    Print proposed changes as CSV without writing anything (default)
    --commit     Apply changes to Linear and post GitHub comments
    --team LAT   Linear team key to reconcile (default: LAT)
    --limit N    Max issues to process in one run (default: 250)
    --output     Path for the markdown report (default: auto-generated)
"""

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime, timezone
from io import StringIO
from typing import Any

try:
    import urllib.request
    import urllib.error
except ImportError:
    pass


# ── Label → phase milestone heuristics ─────────────────────────────────────

LABEL_TO_MILESTONE: dict[str, str] = {
    # Phase A — Foundation (complete)
    "foundation": "Phase A — Foundation",
    # Phase A.5 — Doctrine
    "meta-harness": "Phase A.5 — Doctrine",
    "docs-harness": "Phase A.5 — Doctrine",
    "doctrine": "Phase A.5 — Doctrine",
    # Phase B — M3 Max Bootstrap
    "knowledge-substrate": "Phase B — M3 Max Bootstrap",
    "pixeltable": "Phase B — M3 Max Bootstrap",
    "bootstrap": "Phase B — M3 Max Bootstrap",
    # Phase C — Project Infrastructure
    "linear": "Phase C — Project Infrastructure",
    "ci": "Phase C — Project Infrastructure",
    "devex": "Phase C — Project Infrastructure",
    "infra": "Phase C — Project Infrastructure",
    # Phase D — VW Bridge
    "vw-bridge": "Phase D — VW Bridge",
    "ifc": "Phase D — VW Bridge",
    "vectorworks": "Phase D — VW Bridge",
    # Phase E — iTwin OSS
    "itwin": "Phase E — iTwin OSS",
    "bis": "Phase E — iTwin OSS",
    # Phase F — 3D Viewer
    "3d-viewer": "Phase F — 3D Viewer",
    "thatopen": "Phase F — 3D Viewer",
    "three-js": "Phase F — 3D Viewer",
    # Phase G — Analytics Layer
    "analytics-layer": "Phase G — Analytics Layer",
    "deck-gl": "Phase G — Analytics Layer",
    "duckdb": "Phase G — Analytics Layer",
    # Phase H — Plant Geometry
    "plant-geometry": "Phase H — Plant Geometry",
    "lod": "Phase H — Plant Geometry",
    # Phase I — Point Cloud
    "point-cloud": "Phase I — Point Cloud",
    "potree": "Phase I — Point Cloud",
    "pdal": "Phase I — Point Cloud",
    # Phase J — Agent Runtime
    "agent-runtime": "Phase J — Agent Runtime",
    "worker": "Phase J — Agent Runtime",
    "streaming": "Phase J — Agent Runtime",
    # Phase K — Cesium / Reality Capture
    "cesium": "Phase K — Cesium / Reality Capture",
    "reality-capture": "Phase K — Cesium / Reality Capture",
    "3d-tiles": "Phase K — Cesium / Reality Capture",
    # Phase L — Production Hardening
    "production": "Phase L — Production Hardening",
    "observability": "Phase L — Production Hardening",
    "performance": "Phase L — Production Hardening",
    # Phase M — DDC Skills
    "ddc-skills": "Phase M — DDC Skills Library",
    "ddc": "Phase M — DDC Skills Library",
    # Phase N — Knowledge Substrate Ops
    "knowledge-ops": "Phase N — Knowledge Substrate Production Ops",
    "ingest": "Phase N — Knowledge Substrate Production Ops",
    # Phase O — Outreach
    "outreach": "Phase O — Outreach + Partnership",
    "partner": "Phase O — Outreach + Partnership",
    # Phase P — MARPA Pilot
    "pilot": "Phase P — MARPA Pilot Execution",
    "marpa": "Phase P — MARPA Pilot Execution",
    "boulder": "Phase P — MARPA Pilot Execution",
}

LABEL_TO_PRIORITY: dict[str, int] = {
    "blocked": 1,       # Urgent
    "human-only": 2,    # High
    "agent-ready": 3,   # Medium
    "triage": 0,        # No priority
}

CANONICAL_LABELS = {
    "agent-ready", "meta-harness", "docs-harness", "knowledge-substrate",
    "copilot", "claude-code", "codex", "warp-pi", "hermes", "human-only",
    "vw-bridge", "3d-viewer", "analytics-layer", "plant-geometry",
    "point-cloud", "agent-runtime", "cesium", "ddc-skills", "knowledge-ops",
    "outreach", "pilot", "blocked", "triage",
}

# ── Linear GraphQL helpers ──────────────────────────────────────────────────

LINEAR_URL = "https://api.linear.app/graphql"


def linear_request(api_key: str, query: str, variables: dict | None = None) -> dict:
    payload = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(
        LINEAR_URL,
        data=payload,
        headers={
            "Authorization": api_key,
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"Linear API {e.code}: {body}") from e
    if "errors" in data:
        raise RuntimeError(f"Linear GraphQL errors: {data['errors']}")
    return data.get("data", {})


def github_request(token: str, method: str, path: str, body: dict | None = None) -> dict:
    url = f"https://api.github.com{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"GitHub API {e.code}: {body}") from e


# ── Milestone resolution ─────────────────────────────────────────────────────

def assign_milestone(labels: list[str]) -> str:
    for label in labels:
        if label in LABEL_TO_MILESTONE:
            return LABEL_TO_MILESTONE[label]
    # Body-content heuristics would go here in a future pass
    return "Triage — Unassigned"


def assign_priority(labels: list[str]) -> int:
    for label in labels:
        if label in LABEL_TO_PRIORITY:
            return LABEL_TO_PRIORITY[label]
    return 0  # No priority


def canonical_labels_for(github_labels: list[str]) -> tuple[list[str], list[str]]:
    canonical = [lb for lb in github_labels if lb in CANONICAL_LABELS]
    unknown = [lb for lb in github_labels if lb not in CANONICAL_LABELS]
    return canonical, unknown


# ── Main reconciliation logic ─────────────────────────────────────────────────

def fetch_linear_issues(api_key: str, team_key: str, limit: int) -> list[dict]:
    query = """
    query($teamKey: String!, $first: Int!) {
      issues(
        filter: { team: { key: { eq: $teamKey } } }
        first: $first
        orderBy: createdAt
      ) {
        nodes {
          id
          identifier
          title
          description
          priority
          state { name }
          labels { nodes { name } }
          attachments { nodes { url title } }
        }
        pageInfo { hasNextPage endCursor }
      }
    }
    """
    data = linear_request(api_key, query, {"teamKey": team_key, "first": limit})
    return data.get("issues", {}).get("nodes", [])


def extract_github_issue_number(issue: dict) -> int | None:
    desc = issue.get("description") or ""
    import re
    # Look for "github_issue_id: 123" or "#123" patterns planted by importer
    match = re.search(r"github_issue_id[:\s]+(\d+)", desc)
    if match:
        return int(match.group(1))
    # Fallback: look for github.com/…/issues/NNN in attachments
    for att in issue.get("attachments", {}).get("nodes", []):
        url_match = re.search(r"/issues/(\d+)", att.get("url", ""))
        if url_match:
            return int(url_match.group(1))
    return None


def reconcile(
    linear_issues: list[dict],
    github_token: str,
    repo: str,
    dry_run: bool,
    api_key: str,
) -> list[dict]:
    rows: list[dict] = []

    for issue in linear_issues:
        linear_id = issue["identifier"]
        linear_uuid = issue["id"]
        title = issue["title"]
        current_labels = [n["name"] for n in issue.get("labels", {}).get("nodes", [])]
        current_priority = issue.get("priority", 0)

        github_num = extract_github_issue_number(issue)

        canonical, unknown = canonical_labels_for(current_labels)
        proposed_milestone = assign_milestone(current_labels)
        proposed_priority = assign_priority(current_labels)

        row = {
            "linear_id": linear_id,
            "linear_uuid": linear_uuid,
            "title": title[:80],
            "github_issue": f"#{github_num}" if github_num else "—",
            "current_labels": ", ".join(current_labels),
            "canonical_labels": ", ".join(canonical),
            "unknown_labels": ", ".join(unknown),
            "proposed_milestone": proposed_milestone,
            "proposed_priority": proposed_priority,
            "current_priority": current_priority,
            "action": "no-op" if not unknown and not github_num else "update",
            "dry_run": dry_run,
        }

        if not dry_run:
            # 1. Post back-link comment on GitHub issue
            if github_num and github_token:
                try:
                    github_request(
                        github_token,
                        "POST",
                        f"/repos/{repo}/issues/{github_num}/comments",
                        {"body": f"Imported to Linear as [{linear_id}](https://linear.app/issue/{linear_id}).\n\n_This comment was added by `scripts/linear-reconciliation.py` (Phase C Stage 5b)._"},
                    )
                    row["github_comment_posted"] = "yes"
                    time.sleep(0.5)  # respect GitHub rate limit
                except RuntimeError as e:
                    row["github_comment_posted"] = f"ERROR: {e}"

            # 2. Update Linear priority if it changed
            if proposed_priority != current_priority and proposed_priority > 0:
                try:
                    linear_request(
                        api_key,
                        "mutation($id: String!, $priority: Int!) { issueUpdate(id: $id, input: { priority: $priority }) { success } }",
                        {"id": linear_uuid, "priority": proposed_priority},
                    )
                    row["priority_updated"] = f"{current_priority} → {proposed_priority}"
                except RuntimeError as e:
                    row["priority_updated"] = f"ERROR: {e}"

            # Note: milestone assignment requires fetching milestone UUIDs
            # from Linear and is deferred to Phase C interactive step
            # (human reviews CSV, then runs a targeted milestone-assign pass)

        rows.append(row)
        print(f"  {'[DRY] ' if dry_run else ''}processed {linear_id}: {title[:60]}")

    return rows


def write_report(rows: list[dict], output_path: str) -> None:
    buf = StringIO()
    if not rows:
        buf.write("No issues found.\n")
    else:
        fieldnames = [
            "linear_id", "title", "github_issue", "current_labels",
            "canonical_labels", "unknown_labels", "proposed_milestone",
            "current_priority", "proposed_priority", "action",
        ]
        writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    csv_content = buf.getvalue()
    total = len(rows)
    needs_update = sum(1 for r in rows if r.get("action") == "update")
    unknown_label_issues = sum(1 for r in rows if r.get("unknown_labels"))

    report = f"""---
type: session
date: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}
phase: C
stage: "5b — Linear reconciliation"
status: {"dry-run" if rows and rows[0].get("dry_run") else "committed"}
---

# Linear Import Reconciliation — {datetime.now(timezone.utc).strftime('%Y-%m-%d')}

Generated by `scripts/linear-reconciliation.py` (Phase C Stage 5b).

## Summary

| Metric | Count |
|---|---|
| Total issues processed | {total} |
| Issues needing update | {needs_update} |
| Issues with unknown labels | {unknown_label_issues} |

## Action required before committing

1. Review the **unknown_labels** column — add missing labels to Linear taxonomy in `meta/sync-contract.md`.
2. Review the **proposed_milestone** column — override any mis-assignments manually in Linear.
3. Run `uv run python scripts/linear-reconciliation.py --commit` to apply priority updates and post GitHub back-links.
4. Run a second manual pass in Linear UI to assign milestones (API milestone assignment requires milestone UUIDs — use Linear's bulk-select UI for this step).

## CSV data

```csv
{csv_content}```
"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(report)
    print(f"\nReport written to: {output_path}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", default=True, help="Print changes without applying (default)")
    parser.add_argument("--commit", action="store_true", help="Apply changes to Linear and post GitHub comments")
    parser.add_argument("--team", default="LAT", help="Linear team key (default: LAT)")
    parser.add_argument("--limit", type=int, default=250, help="Max issues to process (default: 250)")
    parser.add_argument("--repo", default="JeromyJSmith/lattice-platform", help="GitHub repo slug")
    parser.add_argument("--output", default=None, help="Output path for markdown report")
    args = parser.parse_args()

    dry_run = not args.commit

    api_key = os.environ.get("LINEAR_API_KEY", "")
    github_token = os.environ.get("GITHUB_TOKEN", "")

    if not api_key:
        print("ERROR: LINEAR_API_KEY environment variable not set.", file=sys.stderr)
        print("  export LINEAR_API_KEY=lin_api_…", file=sys.stderr)
        sys.exit(1)

    if not dry_run and not github_token:
        print("ERROR: GITHUB_TOKEN required for --commit mode.", file=sys.stderr)
        sys.exit(1)

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = args.output or os.path.join(
        repo_root,
        f"meta/harness/docs/sessions/{date_str}-linear-import-reconciliation.md",
    )

    print(f"Mode: {'DRY RUN' if dry_run else 'COMMIT'}")
    print(f"Team: {args.team} | Limit: {args.limit}")
    print(f"Fetching issues from Linear…")

    issues = fetch_linear_issues(api_key, args.team, args.limit)
    print(f"Found {len(issues)} issues in team {args.team}.")

    if not issues:
        print("Nothing to reconcile. Did the bulk import (Stage 5a) run yet?")
        sys.exit(0)

    rows = reconcile(issues, github_token, args.repo, dry_run, api_key)
    write_report(rows, output_path)

    if dry_run:
        print("\nDry run complete. Review the report, then run with --commit to apply.")


if __name__ == "__main__":
    main()
