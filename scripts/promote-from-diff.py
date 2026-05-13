#!/usr/bin/env python3
"""Promote DEFERRED capability registry rows to ACTIVE when their wired_at paths appear in a diff.

Usage:
  git diff HEAD~1 | python3 scripts/promote-from-diff.py
  python3 scripts/promote-from-diff.py path/to/proposal.diff
  python3 scripts/promote-from-diff.py --dry < proposal.diff   # print only, no writes
"""

import os
import sys
import re
import glob
from datetime import date
import yaml

CAPABILITIES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "analysis",
    "capabilities",
)
PROMOTED_AT = date.today().isoformat()
PROMOTED_BY = "autoresearch-ratchet"


def collect_added_paths(diff_text):
    """Extract file paths that are newly added (via +wired_at: or +    - <path>) from a unified diff."""
    added = set()

    # Match +wired_at: "some/path" (string form)
    for m in re.finditer(r'^\+\s*wired_at:\s*["\']?([^\s\'"]+)["\']?', diff_text, re.MULTILINE):
        path = m.group(1).strip()
        if path:
            added.add(path)

    # Match +wired_at: [path1, path2] (inline list form)
    for m in re.finditer(r'^\+\s*wired_at:\s*\[([^\]]+)\]', diff_text, re.MULTILINE):
        for item in m.group(1).split(","):
            path = item.strip().strip("'\"")
            if path:
                added.add(path)

    # Match +    - <path> (block list items that follow wired_at)
    # We track whether we're inside a wired_at block
    in_wired_at = False
    for line in diff_text.splitlines():
        if re.match(r'^\+\s*wired_at:', line):
            in_wired_at = True
            continue
        if in_wired_at:
            m = re.match(r'^\+\s+-\s+["\']?([^\s\'"#]+)["\']?', line)
            if m:
                path = m.group(1).strip()
                if path:
                    added.add(path)
            elif line.startswith('+') and re.match(r'^\+\s{0,4}\S', line):
                # A non-list line — wired_at block ended
                in_wired_at = False

    # Also pick up +++ b/<path> file additions (entirely new files added by the diff)
    for m in re.finditer(r'^\+\+\+\s+b/(.+)', diff_text, re.MULTILINE):
        path = m.group(1).strip()
        if path and path != "/dev/null":
            added.add(path)

    return added


def normalise_wired_at(value):
    """Return wired_at as a list of strings regardless of whether it is a string or list."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(v) for v in value]
    return [str(value)]


def all_paths_exist(paths, repo_root):
    """Return True only when every path in the list exists on disk."""
    for p in paths:
        full = os.path.join(repo_root, p)
        if not os.path.exists(full):
            return False
    return True


def load_registry(yaml_path):
    """Load a capability registry YAML file and return the parsed document."""
    with open(yaml_path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def save_registry(yaml_path, doc):
    """Write the capability registry document back to disk preserving block style."""
    with open(yaml_path, "w", encoding="utf-8") as fh:
        yaml.dump(doc, fh, default_flow_style=False, allow_unicode=True, sort_keys=False)


def find_registry_files():
    """Return all *.yaml files in the capabilities directory."""
    pattern = os.path.join(CAPABILITIES_DIR, "*.yaml")
    return sorted(glob.glob(pattern))


def promote_from_diff(diff_text, dry_run, repo_root):
    """Scan diff, find matching DEFERRED rows, promote them. Return list of (registry, id) tuples."""
    added_paths = collect_added_paths(diff_text)
    if not added_paths:
        return []

    promoted = []

    for yaml_path in find_registry_files():
        doc = load_registry(yaml_path)
        if not isinstance(doc, dict):
            continue
        caps = doc.get("capabilities")
        if not isinstance(caps, list):
            continue

        modified = False
        for cap in caps:
            if not isinstance(cap, dict):
                continue
            if cap.get("state") != "DEFERRED":
                continue

            wired_at = normalise_wired_at(cap.get("wired_at"))
            if not wired_at:
                continue

            # Only promote if the diff adds at least one of the wired_at paths
            # AND every wired_at path now exists on disk.
            wired_set = set(wired_at)
            if not (wired_set & added_paths):
                continue
            if not all_paths_exist(wired_at, repo_root):
                continue

            cap["state"] = "ACTIVE"
            cap["promoted_at"] = PROMOTED_AT
            cap["promoted_by"] = PROMOTED_BY
            modified = True

            rel_registry = os.path.relpath(yaml_path, repo_root)
            promoted.append((rel_registry, cap.get("id", "<unknown>")))

        if modified and not dry_run:
            save_registry(yaml_path, doc)

    return promoted


def read_diff(args):
    """Read unified diff from a file argument or stdin."""
    # Strip leading --dry from args
    clean = [a for a in args if a != "--dry"]
    if clean:
        path = clean[0]
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    return sys.stdin.read()


def main():
    """Entry point: parse args, run promotion, print summary."""
    args = sys.argv[1:]
    dry_run = "--dry" in args

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    try:
        diff_text = read_diff(args)
    except (OSError, IOError) as exc:
        print(f"[promote-from-diff] ERROR reading diff: {exc}", file=sys.stderr)
        sys.exit(1)

    promoted = promote_from_diff(diff_text, dry_run, repo_root)

    if not promoted:
        print("0 rows promoted.")
        return

    label = "(dry-run) " if dry_run else ""
    print(f"{label}{len(promoted)} row(s) promoted to ACTIVE:")
    for registry, cap_id in promoted:
        print(f"  {registry}  →  {cap_id}")


if __name__ == "__main__":
    main()
