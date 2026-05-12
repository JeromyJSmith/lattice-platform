#!/usr/bin/env python3
"""
LATTICE Linear Bootstrap (Stages 4 + 5a + 5b in one pass)

Creates the full Linear project structure and imports all GitHub issues
without touching the Linear web UI. Uses Linear GraphQL API + gh CLI.

Idempotent: safe to re-run. Existing teams/projects/milestones/labels
are detected and reused; issues are skipped if already present (detected
by github_issue_id in description).

Usage:
    export LINEAR_API_KEY=lin_api_…
    uv run python scripts/linear-bootstrap.py --dry-run
    uv run python scripts/linear-bootstrap.py --commit

Options:
    --dry-run       Print what would happen without writing (default)
    --commit        Apply all changes
    --skip-issues   Run project setup only, skip issue import
    --skip-setup    Run issue import only, skip project setup
    --limit N       Max GitHub issues to import per run (default: 250)
    --offset N      Skip first N GitHub issues (for resuming)
    --repo SLUG     GitHub repo (default: JeromyJSmith/lattice-platform)

Requirements:
    LINEAR_API_KEY  env var (Linear → Settings → API → Personal API keys)
    gh CLI          authenticated (gh auth status)
    python 3.11+    (stdlib only, no external deps)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any

# ── Constants ──────────────────────────────────────────────────────────────

LINEAR_URL = "https://api.linear.app/graphql"
REPO = "JeromyJSmith/lattice-platform"

TEAM_NAME = "LATTICE"
TEAM_KEY = "LAT"
PROJECT_NAME = "Lattice"

MILESTONES = [
    # (name, target_date_iso)  — None = rolling / no fixed date
    ("Phase A — Foundation", "2026-05-11"),           # complete
    ("Phase A.5 — Doctrine", "2026-05-20"),
    ("Phase B — M3 Max Bootstrap", "2026-06-15"),
    ("Phase C — Project Infrastructure", "2026-05-30"),
    ("Phase D — VW Bridge", "2026-07-31"),
    ("Phase E — iTwin OSS Self-Hosted", "2026-09-15"),
    ("Phase F — 3D Viewer (Context A)", "2026-09-30"),
    ("Phase G — Analytics Layer (Context B)", "2026-10-15"),
    ("Phase H — Plant Geometry LOD Pipeline", "2026-11-01"),
    ("Phase I — Point Cloud", "2026-11-15"),
    ("Phase J — Agent Runtime", "2026-12-01"),
    ("Phase K — Cesium 3D Tiles + Reality Capture", "2026-12-15"),
    ("Phase L — Production Hardening", "2026-12-31"),
    ("Phase M — DDC Skills Library", "2026-09-30"),
    ("Phase N — Knowledge Substrate Production Ops", "2026-08-15"),
    ("Phase O — Outreach + Partnership Execution", None),
    ("Phase P — MARPA Pilot Execution", None),
]

LABELS: list[dict[str, str]] = [
    {"name": "agent-ready",        "color": "#4CAF50"},
    {"name": "meta-harness",       "color": "#9C27B0"},
    {"name": "docs-harness",       "color": "#673AB7"},
    {"name": "knowledge-substrate","color": "#3F51B5"},
    {"name": "copilot",            "color": "#2196F3"},
    {"name": "claude-code",        "color": "#FF9800"},
    {"name": "codex",              "color": "#009688"},
    {"name": "warp-pi",            "color": "#F44336"},
    {"name": "hermes",             "color": "#E91E63"},
    {"name": "human-only",         "color": "#607D8B"},
    {"name": "vw-bridge",          "color": "#8BC34A"},
    {"name": "3d-viewer",          "color": "#00BCD4"},
    {"name": "analytics-layer",    "color": "#FFEB3B"},
    {"name": "plant-geometry",     "color": "#4CAF50"},
    {"name": "point-cloud",        "color": "#795548"},
    {"name": "agent-runtime",      "color": "#FF5722"},
    {"name": "cesium",             "color": "#9E9E9E"},
    {"name": "ddc-skills",         "color": "#CDDC39"},
    {"name": "knowledge-ops",      "color": "#00BCD4"},
    {"name": "outreach",           "color": "#FFC107"},
    {"name": "pilot",              "color": "#FF9800"},
    {"name": "blocked",            "color": "#F44336"},
    {"name": "triage",             "color": "#9E9E9E"},
]

# GitHub label → canonical Linear label (for import mapping)
GH_LABEL_MAP: dict[str, str] = {
    "agent-ready": "agent-ready",
    "meta-harness": "meta-harness",
    "docs-harness": "docs-harness",
    "knowledge-substrate": "knowledge-substrate",
    "vw-bridge": "vw-bridge",
    "3d-viewer": "3d-viewer",
    "analytics-layer": "analytics-layer",
    "plant-geometry": "plant-geometry",
    "point-cloud": "point-cloud",
    "agent-runtime": "agent-runtime",
    "cesium": "cesium",
    "ddc-skills": "ddc-skills",
    "knowledge-ops": "knowledge-ops",
    "outreach": "outreach",
    "pilot": "pilot",
    "blocked": "blocked",
    "bug": "triage",
    "enhancement": "triage",
    "help wanted": "agent-ready",
    "good first issue": "agent-ready",
}

# GitHub label → milestone name heuristic
GH_LABEL_MILESTONE: dict[str, str] = {
    "meta-harness": "Phase A.5 — Doctrine",
    "docs-harness": "Phase A.5 — Doctrine",
    "knowledge-substrate": "Phase B — M3 Max Bootstrap",
    "vw-bridge": "Phase D — VW Bridge",
    "ifc": "Phase D — VW Bridge",
    "3d-viewer": "Phase F — 3D Viewer (Context A)",
    "analytics-layer": "Phase G — Analytics Layer (Context B)",
    "plant-geometry": "Phase H — Plant Geometry LOD Pipeline",
    "point-cloud": "Phase I — Point Cloud",
    "agent-runtime": "Phase J — Agent Runtime",
    "cesium": "Phase K — Cesium 3D Tiles + Reality Capture",
    "ddc-skills": "Phase M — DDC Skills Library",
    "knowledge-ops": "Phase N — Knowledge Substrate Production Ops",
    "outreach": "Phase O — Outreach + Partnership Execution",
    "pilot": "Phase P — MARPA Pilot Execution",
}

GH_LABEL_PRIORITY: dict[str, int] = {
    "blocked": 1,
    "human-only": 2,
    "agent-ready": 3,
}

PROJECT_DESCRIPTION = """\
AI-native AEC digital twin for landscape architecture.
Vectorworks → IFC4.3 → iTwin OSS → deck.gl + Cesium 3D Tiles → Pixeltable knowledge substrate.
Claude CLI runtime.

**Locked stack:** Bun · TanStack Start · React 19 · FastAPI · Pixeltable 0.6 · \
@thatopen/components · Three.js · deck.gl · DuckDB WASM · MapLibre · iTwin OSS (no core-backend).

**Doctrine refs:** meta/sync-contract.md · meta/agent-lanes.md · AGENTS.md · CLAUDE.md · \
meta/ARCHITECTURE.md · meta/SCHEMA.md · meta/API.md · .github/copilot-instructions.md

**Teams:** LATTICE (LAT-XX, platform Phases A–N) · MARPA (MAR-XX, Phases O–P)

**Phase targets:** Foundation ✅ · Doctrine 2026-05-20 · Bootstrap 2026-06-15 · \
VW Bridge 2026-07-31 · 3D Viewer 2026-09-30 · Production Hardening 2026-12-31
"""

# ── Linear API ─────────────────────────────────────────────────────────────

def gql(api_key: str, query: str, variables: dict | None = None) -> dict:
    payload = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(
        LINEAR_URL,
        data=payload,
        headers={"Authorization": api_key, "Content-Type": "application/json"},
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
            if "errors" in data:
                raise RuntimeError(f"GraphQL errors: {data['errors']}")
            return data.get("data", {})
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            if e.code == 429:
                wait = 2 ** attempt * 2
                print(f"  [rate-limit] waiting {wait}s…", file=sys.stderr)
                time.sleep(wait)
                continue
            raise RuntimeError(f"Linear {e.code}: {body}") from e
    raise RuntimeError("Max retries exceeded on Linear API")


def rate_sleep(n: float = 0.3) -> None:
    time.sleep(n)


# ── Team ───────────────────────────────────────────────────────────────────

def get_or_create_team(api_key: str, dry_run: bool) -> tuple[str, str]:
    """Returns (team_id, team_key). Creates team if missing."""
    data = gql(api_key, "{ teams { nodes { id key name } } }")
    for t in data["teams"]["nodes"]:
        if t["key"] == TEAM_KEY or t["name"] == TEAM_NAME:
            print(f"  ✓ Team exists: {t['name']} ({t['key']}) id={t['id']}")
            return t["id"], t["key"]

    print(f"  Team '{TEAM_NAME}' (key={TEAM_KEY}) not found.")
    if dry_run:
        print(f"  [dry-run] would create team {TEAM_NAME}")
        return "DRY_TEAM_ID", TEAM_KEY

    data = gql(api_key, """
        mutation($name: String!, $key: String!) {
          teamCreate(input: { name: $name, key: $key, timezone: "America/Denver" }) {
            success team { id key name }
          }
        }
    """, {"name": TEAM_NAME, "key": TEAM_KEY})
    team = data["teamCreate"]["team"]
    print(f"  ✓ Created team: {team['name']} ({team['key']}) id={team['id']}")
    return team["id"], team["key"]


# ── Project ────────────────────────────────────────────────────────────────

def get_or_create_project(api_key: str, team_id: str, dry_run: bool) -> str:
    """Returns project_id."""
    data = gql(api_key, "{ projects { nodes { id name } } }")
    for p in data["projects"]["nodes"]:
        if p["name"] == PROJECT_NAME:
            print(f"  ✓ Project exists: {p['name']} id={p['id']}")
            return p["id"]

    print(f"  Project '{PROJECT_NAME}' not found.")
    if dry_run:
        print(f"  [dry-run] would create project {PROJECT_NAME}")
        return "DRY_PROJECT_ID"

    data = gql(api_key, """
        mutation($name: String!, $teamIds: [String!]!, $description: String,
                 $startDate: TimelessDate, $targetDate: TimelessDate) {
          projectCreate(input: {
            name: $name, teamIds: $teamIds, description: $description,
            startDate: $startDate, targetDate: $targetDate
          }) {
            success project { id name }
          }
        }
    """, {
        "name": PROJECT_NAME,
        "teamIds": [team_id],
        "description": PROJECT_DESCRIPTION,
        "startDate": "2026-05-11",
        "targetDate": "2026-12-31",
    })
    proj = data["projectCreate"]["project"]
    print(f"  ✓ Created project: {proj['name']} id={proj['id']}")
    return proj["id"]


# ── Milestones ─────────────────────────────────────────────────────────────

def get_or_create_milestones(api_key: str, project_id: str, dry_run: bool) -> dict[str, str]:
    """Returns {milestone_name: milestone_id}."""
    data = gql(api_key, """
        query($projectId: String!) {
          project(id: $projectId) {
            projectMilestones { nodes { id name } }
          }
        }
    """, {"projectId": project_id})
    existing = {m["name"]: m["id"] for m in data["project"]["projectMilestones"]["nodes"]}
    result: dict[str, str] = dict(existing)

    for name, target_date in MILESTONES:
        if name in existing:
            print(f"  ✓ Milestone exists: {name}")
            continue
        print(f"  + Milestone: {name}")
        if dry_run:
            result[name] = f"DRY_{name[:8]}"
            continue
        vars_: dict[str, Any] = {"projectId": project_id, "name": name}
        if target_date:
            vars_["targetDate"] = target_date
        data2 = gql(api_key, """
            mutation($projectId: String!, $name: String!, $targetDate: TimelessDate) {
              projectMilestoneCreate(input: {
                projectId: $projectId, name: $name, targetDate: $targetDate
              }) {
                success projectMilestone { id name }
              }
            }
        """, vars_)
        m = data2["projectMilestoneCreate"]["projectMilestone"]
        result[m["name"]] = m["id"]
        rate_sleep()

    return result


# ── Labels ─────────────────────────────────────────────────────────────────

def get_or_create_labels(api_key: str, team_id: str, dry_run: bool) -> dict[str, str]:
    """Returns {label_name: label_id}."""
    data = gql(api_key, """
        query($teamId: String!) {
          team(id: $teamId) {
            labels { nodes { id name } }
          }
        }
    """, {"teamId": team_id})
    existing = {lb["name"]: lb["id"] for lb in data["team"]["labels"]["nodes"]}
    result: dict[str, str] = dict(existing)

    for lb in LABELS:
        if lb["name"] in existing:
            continue
        print(f"  + Label: {lb['name']}")
        if dry_run:
            result[lb["name"]] = f"DRY_LBL_{lb['name'][:8]}"
            continue
        data2 = gql(api_key, """
            mutation($teamId: String!, $name: String!, $color: String!) {
              issueLabelCreate(input: { teamId: $teamId, name: $name, color: $color }) {
                success issueLabel { id name }
              }
            }
        """, {"teamId": team_id, "name": lb["name"], "color": lb["color"]})
        new_lb = data2["issueLabelCreate"]["issueLabel"]
        result[new_lb["name"]] = new_lb["id"]
        rate_sleep()

    print(f"  ✓ Labels ready: {len(result)} total")
    return result


# ── GitHub issue fetch ─────────────────────────────────────────────────────

def fetch_github_issues(repo: str, limit: int, offset: int) -> list[dict]:
    print(f"  Fetching GitHub issues (limit={limit}, offset={offset})…")
    result = subprocess.run(
        [
            "gh", "issue", "list",
            "--repo", repo,
            "--state", "open",
            "--limit", str(limit + offset),
            "--json", "number,title,body,labels,createdAt,assignees,url",
        ],
        capture_output=True, text=True, check=True,
    )
    all_issues = json.loads(result.stdout)
    sliced = all_issues[offset:]
    print(f"  Got {len(sliced)} GitHub issues (total fetched: {len(all_issues)})")
    return sliced


def already_imported(api_key: str, team_id: str, gh_number: int) -> str | None:
    """Returns Linear issue ID if already imported, else None."""
    needle = f"github_issue_id: {gh_number}"
    data = gql(api_key, """
        query($teamId: ID!, $desc: String!) {
          issues(
            filter: {
              team: { id: { eq: $teamId } }
              description: { contains: $desc }
            }
            first: 1
          ) {
            nodes { id description }
          }
        }
    """, {"teamId": team_id, "desc": needle})
    nodes = data.get("issues", {}).get("nodes", [])
    if nodes:
        return nodes[0]["id"]
    return None


def resolve_labels(gh_labels: list[str], label_map: dict[str, str]) -> list[str]:
    ids = []
    for gh_lb in gh_labels:
        canonical = GH_LABEL_MAP.get(gh_lb)
        if canonical and canonical in label_map:
            ids.append(label_map[canonical])
    return ids


def resolve_milestone(gh_labels: list[str], milestone_map: dict[str, str]) -> str | None:
    for gh_lb in gh_labels:
        ms_name = GH_LABEL_MILESTONE.get(gh_lb)
        if ms_name and ms_name in milestone_map:
            return milestone_map[ms_name]
    return milestone_map.get("Phase C — Project Infrastructure")


def resolve_priority(gh_labels: list[str]) -> int:
    for lb in gh_labels:
        if lb in GH_LABEL_PRIORITY:
            return GH_LABEL_PRIORITY[lb]
    return 0


# ── Issue import ───────────────────────────────────────────────────────────

def import_issues(
    api_key: str,
    team_id: str,
    project_id: str,
    label_map: dict[str, str],
    milestone_map: dict[str, str],
    gh_issues: list[dict],
    dry_run: bool,
    repo: str,
) -> list[dict]:
    results = []
    total = len(gh_issues)

    for idx, gh in enumerate(gh_issues, 1):
        gh_num = gh["number"]
        gh_title = gh["title"]
        gh_body = gh.get("body") or ""
        gh_labels = [lb["name"] for lb in gh.get("labels", [])]
        gh_url = gh.get("url", f"https://github.com/{repo}/issues/{gh_num}")

        prefix = f"  [{idx}/{total}] #{gh_num}"

        if not dry_run:
            existing_id = already_imported(api_key, team_id, gh_num)
            if existing_id:
                print(f"{prefix} — already imported ({existing_id}), skipping")
                results.append({"gh": gh_num, "linear": existing_id, "action": "skipped"})
                continue

        label_ids = resolve_labels(gh_labels, label_map)
        milestone_id = resolve_milestone(gh_labels, milestone_map)
        priority = resolve_priority(gh_labels)

        description = (
            f"github_issue_id: {gh_num}\n"
            f"GitHub: {gh_url}\n\n"
            + gh_body
        )

        print(f"{prefix} — {gh_title[:60]}  labels={gh_labels[:3]} prio={priority}")

        if dry_run:
            results.append({"gh": gh_num, "linear": "DRY", "action": "would-create"})
            continue

        vars_: dict[str, Any] = {
            "teamId": team_id,
            "projectId": project_id,
            "title": gh_title,
            "description": description,
            "priority": priority,
            "labelIds": label_ids,
        }
        if milestone_id:
            vars_["projectMilestoneId"] = milestone_id

        try:
            data = gql(api_key, """
                mutation(
                  $teamId: String!, $projectId: String!, $title: String!,
                  $description: String, $priority: Int, $labelIds: [String!],
                  $projectMilestoneId: String
                ) {
                  issueCreate(input: {
                    teamId: $teamId, projectId: $projectId, title: $title,
                    description: $description, priority: $priority,
                    labelIds: $labelIds, projectMilestoneId: $projectMilestoneId
                  }) {
                    success issue { id identifier url }
                  }
                }
            """, vars_)
            issue = data["issueCreate"]["issue"]
            linear_id = issue["identifier"]
            linear_url = issue["url"]
            print(f"    ✓ Created {linear_id} — {linear_url}")

            # Post back-link comment on GitHub issue
            comment_body = (
                f"Imported to Linear as [{linear_id}]({linear_url}).\n\n"
                "_Added by `scripts/linear-bootstrap.py` (Phase C Stage 5)._"
            )
            subprocess.run(
                ["gh", "issue", "comment", str(gh_num),
                 "--repo", repo, "--body", comment_body],
                capture_output=True, check=False,
            )

            results.append({"gh": gh_num, "linear": linear_id, "action": "created"})
            rate_sleep(0.4)

        except RuntimeError as e:
            print(f"    ✗ ERROR: {e}", file=sys.stderr)
            results.append({"gh": gh_num, "linear": "ERROR", "action": str(e)[:80]})

    return results


# ── Report ─────────────────────────────────────────────────────────────────

def write_report(results: list[dict], output_path: str, dry_run: bool) -> None:
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    created = sum(1 for r in results if r["action"] == "created")
    skipped = sum(1 for r in results if r["action"] == "skipped")
    errors = sum(1 for r in results if r["action"] not in ("created", "skipped", "would-create"))
    would = sum(1 for r in results if r["action"] == "would-create")

    lines = [
        f"---",
        f"type: session",
        f"date: {date_str}",
        f"phase: C",
        f"stage: '5 — Linear bootstrap'",
        f"status: {'dry-run' if dry_run else 'committed'}",
        f"---",
        f"",
        f"# Linear Bootstrap Report — {date_str}",
        f"",
        f"Generated by `scripts/linear-bootstrap.py`.",
        f"",
        f"## Summary",
        f"",
        f"| Metric | Count |",
        f"|---|---|",
        f"| GitHub issues processed | {len(results)} |",
        f"| Created in Linear | {created + would} |",
        f"| Already imported (skipped) | {skipped} |",
        f"| Errors | {errors} |",
        f"",
        f"## Issue map",
        f"",
        f"| GitHub | Linear | Action |",
        f"|---|---|---|",
    ]
    for r in results:
        lines.append(f"| #{r['gh']} | {r['linear']} | {r['action']} |")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nReport: {output_path}")


# ── CLI ───────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--commit", action="store_true")
    parser.add_argument("--skip-issues", action="store_true")
    parser.add_argument("--skip-setup", action="store_true")
    parser.add_argument("--limit", type=int, default=250)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--repo", default=REPO)
    parser.add_argument("--team-key", default=None,
                        help="Use existing team by key instead of creating (e.g. MARPA)")
    parser.add_argument("--project-id", default=None,
                        help="Use existing project UUID instead of creating")
    args = parser.parse_args()

    dry_run = not args.commit

    api_key = os.environ.get("LINEAR_API_KEY", "")
    if not api_key:
        print("ERROR: LINEAR_API_KEY not set.", file=sys.stderr)
        print("  1. Go to: Linear → Settings → API → Personal API keys", file=sys.stderr)
        print("  2. Create key named 'lattice-bootstrap'", file=sys.stderr)
        print("  3. export LINEAR_API_KEY=lin_api_…", file=sys.stderr)
        sys.exit(1)

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output_path = os.path.join(
        repo_root,
        f"meta/harness/docs/sessions/{date_str}-linear-bootstrap-report.md",
    )

    print(f"Mode: {'DRY RUN' if dry_run else 'COMMIT'}")
    print(f"Repo: {args.repo}  Limit: {args.limit}  Offset: {args.offset}")
    print()

    team_id = project_id = ""
    label_map: dict[str, str] = {}
    milestone_map: dict[str, str] = {}

    # Resolve team: --team-key takes precedence over auto-create
    if args.team_key:
        data = gql(api_key, "{ teams { nodes { id key name } } }")
        matched = next((t for t in data["teams"]["nodes"] if t["key"] == args.team_key), None)
        if not matched:
            print(f"ERROR: team with key '{args.team_key}' not found.", file=sys.stderr)
            print(f"  Available: {[t['key'] for t in data['teams']['nodes']]}", file=sys.stderr)
            sys.exit(1)
        team_id = matched["id"]
        print(f"Using existing team: {matched['name']} ({matched['key']}) id={team_id}")

    # Resolve project: --project-id takes precedence over auto-create
    if args.project_id:
        project_id = args.project_id
        print(f"Using existing project id={project_id}")

    if not args.skip_setup:
        print("── Stage 4: Project setup ──────────────────────────")

        if not team_id:
            print("\n[1/4] Team…")
            team_id, _ = get_or_create_team(api_key, dry_run)
        else:
            print("\n[1/4] Team… (using provided --team-key, skipping create)")

        if not project_id:
            print("\n[2/4] Project…")
            project_id = get_or_create_project(api_key, team_id, dry_run)
        else:
            print("\n[2/4] Project… (using provided --project-id, skipping create)")

        print("\n[3/4] Milestones…")
        milestone_map = get_or_create_milestones(api_key, project_id, dry_run)

        print("\n[4/4] Labels…")
        label_map = get_or_create_labels(api_key, team_id, dry_run)

        print(f"\n✓ Stage 4 complete. team={team_id} project={project_id}")
    else:
        # In skip-setup mode, fetch existing IDs
        print("── Fetching existing project state (--skip-setup) ──")
        if not team_id:
            team_id, _ = get_or_create_team(api_key, dry_run=True)
        if not project_id:
            project_id = get_or_create_project(api_key, team_id, dry_run=True)
        milestone_map = get_or_create_milestones(api_key, project_id, dry_run=True)
        label_map = get_or_create_labels(api_key, team_id, dry_run=True)

    results: list[dict] = []

    if not args.skip_issues:
        print("\n── Stage 5a+5b: Issue import ───────────────────────")
        gh_issues = fetch_github_issues(args.repo, args.limit, args.offset)

        if not gh_issues:
            print("No GitHub issues found.")
        else:
            results = import_issues(
                api_key, team_id, project_id,
                label_map, milestone_map,
                gh_issues, dry_run, args.repo,
            )

        write_report(results, output_path, dry_run)

    print()
    if dry_run:
        print("Dry run complete. Review output, then run with --commit to apply.")
        print(f"  uv run python scripts/linear-bootstrap.py --commit")
    else:
        created = sum(1 for r in results if r["action"] == "created")
        print(f"Done. {created} issues created in Linear.")

    # Stage 3 reminder
    print()
    print("── Stage 3 (browser-only step, do once) ───────────────")
    print("  Linear → Settings → Integrations → GitHub:")
    print(f"  1. Connect repo '{args.repo}' to the LATTICE team")
    print("  2. Enable: auto-link PRs, auto-update status, sync labels")
    print("  3. Copy the webhook URL, then:")
    print(f"     gh secret set LINEAR_WEBHOOK_URL --repo {args.repo} --body '<url>'")
    print(f"     gh secret set LINEAR_API_KEY --repo {args.repo} --body '$LINEAR_API_KEY'")


if __name__ == "__main__":
    main()
