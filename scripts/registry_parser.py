#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "pyyaml>=6.0",
# ]
# ///
"""Capability registry parser — single source of truth for downstream tooling.

Used by:
  - scripts/generate-capability-landscape.py (HTML report generator)
  - manual review of "potentially stale" paths in ACTIVE rows

NOT wired into audit-dead-dna.sh as a hard fail, because path-existence is
the wrong test for several legitimate evidence types:

  Evidence kind        Where it lives                Audit treatment
  -------------------  ----------------------------  ----------------------
  Static (in-repo)     git working tree              MUST exist
  Proof of run         git, state/ or docs/sessions  MUST exist
  Install evidence     outside git (global tool,     verified by command,
                       daemon, OS state)              NOT file existence
  Branch-conditional   exists only after a sibling   not stale, just absent
                       PR merges                      on this branch

This parser categorizes claims into:
  - probably_static   — looks like an in-repo path; existence checked
  - probably_install  — points outside repo; SKIPPED
  - probably_branch   — points at a path under a directory that exists in
                        another worktree but not here; SKIPPED with note
  - non_path          — URL, command invocation, prose; SKIPPED

Only `probably_static` paths get a stale-check. Everything else is reported
as "advisory: review when convenient" for the HTML report to visualize.

Usage
-----
    # Dump the full parsed model as JSON.
    uv run scripts/registry_parser.py

    # Print a human summary and exit 0/1 based on stale-row count.
    uv run scripts/registry_parser.py --verify

    # Just show stale-row report.
    uv run scripts/registry_parser.py --stale-only
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_GLOB = "analysis/capabilities/*-capability-registry.yaml"


# Path extraction: strip ` (...)` annotations and trailing `:suffix` (line
# numbers, function names, or symbol refs), skip URLs and prose descriptions.
# The colon-suffix regex strips anything after the LAST colon that doesn't
# contain a slash — handles `foo.py:42`, `foo.py:42-58`, `foo.py:my_function`.
_LINE_SUFFIX_RE = re.compile(r":[^/\s]+$")
_PAREN_ANNOTATION_RE = re.compile(r"\s*\([^)]*\)\s*$")

# Install-evidence prefixes: paths that point outside the repo at globally
# installed tools, system locations, or user-local installs. These are
# install-evidence (verified by running a command), not file-existence claims.
_INSTALL_EVIDENCE_PREFIXES = (
    "~/",
    "/Applications/",
    "/opt/",
    "/usr/",
    "/Volumes/PixelTable/",      # User-owned global volume; outside this repo
    "/Users/",                   # Any user-home reference
    "/Library/",
)

# Common "looks like a command, not a file" patterns that the harvester
# sometimes leaks into wired_at fields.
_COMMAND_HEAD_TOKENS = ("npm", "bun", "uv", "brew", "ollama", "pip", "npx", "cargo")


def is_url(s: str) -> bool:
    """Return True if the string looks like a URL we should skip."""
    s = s.strip()
    return (
        s.startswith("http://")
        or s.startswith("https://")
        or s.startswith("github.com/")
        or s.startswith("www.")
    )


def looks_like_path(s: str) -> bool:
    """Heuristic: does this string look like a filesystem path?

    Paths don't contain spaces. Prose descriptions like "Phase 1 install step"
    do — they're not path claims even if the harvester put them in wired_at.
    Command-style refs ("POST /v1/foo", "uv run scripts/foo.py") aren't paths
    to check either; they describe an invocation surface.
    """
    s = s.strip()
    if not s:
        return False
    if is_url(s):
        return False
    # Anything with internal whitespace is a description, not a path.
    if any(ch.isspace() for ch in s):
        return False
    return True


def classify_claim(s: str) -> tuple[str, str | None]:
    """Categorize a wired_at/proof claim into (kind, normalized_path).

    Returns one of:
      ("non_path",         None)   — URL, prose, or unrecognized
      ("probably_install", path)   — install-evidence (outside repo, etc.)
      ("probably_static",  path)   — in-repo file path; existence-checkable
    """
    if not isinstance(s, str):
        return ("non_path", None)
    raw = s.strip()
    if not raw:
        return ("non_path", None)
    if is_url(raw):
        return ("non_path", None)
    # Whitespace-bearing strings are prose, not paths.
    if any(ch.isspace() for ch in raw):
        return ("non_path", None)

    # Strip annotations + colon suffixes (line numbers, function names, etc.)
    s = _PAREN_ANNOTATION_RE.sub("", raw).strip()
    s = _LINE_SUFFIX_RE.sub("", s).strip()
    if not s:
        return ("non_path", None)

    # Install-evidence (outside repo, global installs, system paths)
    if s.startswith(_INSTALL_EVIDENCE_PREFIXES):
        return ("probably_install", s)

    # Bare command tokens like "ollama", "uv", "bun" — no slash, looks like
    # a binary name; treat as install-evidence.
    if "/" not in s and "." not in s:
        if s in _COMMAND_HEAD_TOKENS or len(s) < 24:
            return ("probably_install", s)

    return ("probably_static", s)


# Back-compat shim — old callers expected (str | None).
def extract_path(s: str) -> str | None:
    """Return the path if classify_claim says probably_static, else None.

    Kept for callers that only want strictly-checkable in-repo paths.
    """
    kind, path = classify_claim(s)
    return path if kind == "probably_static" else None


def collect_path_claims(row: dict[str, Any]) -> list[tuple[str, str, str]]:
    """Return [(field_label, path, kind)] for every path-like claim in an ACTIVE row.

    kind is one of "probably_static", "probably_install", "non_path".
    Callers should only existence-check probably_static.

    Covers wired_at (str or list), proof.evidence (str), proof_evidence (str | dict).
    """
    out: list[tuple[str, str, str]] = []

    def add(label: str, raw: Any) -> None:
        """Helper: classify one raw claim string and append if it's a path."""
        if not isinstance(raw, str):
            return
        kind, p = classify_claim(raw)
        if p is not None:
            out.append((label, p, kind))

    wired = row.get("wired_at")
    if isinstance(wired, str):
        add("wired_at", wired)
    elif isinstance(wired, list):
        for i, item in enumerate(wired):
            add(f"wired_at[{i}]", item)

    proof = row.get("proof")
    if isinstance(proof, dict):
        add("proof.evidence", proof.get("evidence"))

    pe = row.get("proof_evidence")
    if isinstance(pe, str):
        add("proof_evidence", pe)
    elif isinstance(pe, dict):
        for key, val in pe.items():
            add(f"proof_evidence.{key}", val)

    return out


def parse_registries(root: Path = REPO_ROOT) -> list[dict[str, Any]]:
    """Parse every capability registry and return a flat list of rows.

    Each row dict includes:
      registry: short name from filename
      registry_path: relative path to the YAML file
      tool: from the registry header
      id, surface, name, state, description: from the row
      stale_paths: [(field, path)] for paths that don't exist (ACTIVE rows only)
      all_paths: [(field, path)] for every path claim (ACTIVE rows only)
      raw: the raw row dict
    """
    rows: list[dict[str, Any]] = []
    for yaml_path in sorted(root.glob(REGISTRY_GLOB)):
        try:
            data = yaml.safe_load(yaml_path.read_text())
        except yaml.YAMLError as e:
            print(f"WARN: failed to parse {yaml_path}: {e}", file=sys.stderr)
            continue
        if not isinstance(data, dict):
            continue
        tool = data.get("tool", "?")
        caps = data.get("capabilities") or []
        registry_name = yaml_path.name.removesuffix("-capability-registry.yaml")
        for cap in caps:
            if not isinstance(cap, dict):
                continue
            state = cap.get("state", "?")
            row = {
                "registry": registry_name,
                "registry_path": str(yaml_path.relative_to(root)),
                "tool": tool,
                "id": cap.get("id", "?"),
                "surface": cap.get("surface", "?"),
                "name": cap.get("name", "?"),
                "state": state,
                "description": cap.get("description", ""),
                "reason": cap.get("reason"),  # DEFERRED
                "target_phase": cap.get("target_phase"),
                "blocker": cap.get("blocker"),  # BLOCKED
                "stale_paths": [],
                "all_paths": [],
                "raw": cap,
            }
            # Always populate evidence-kind buckets so the HTML report can
            # show what kind of claim each row makes.
            row["install_evidence_paths"] = []
            row["static_paths_present"] = []
            row["static_paths_advisory_stale"] = []
            if state == "ACTIVE":
                # source_repo rows intentionally point at EXTERNAL upstream
                # paths — they describe what to harvest from another repo,
                # not what LATTICE wired locally. Skip categorization.
                if cap.get("surface") != "source_repo":
                    claims = collect_path_claims(cap)
                    row["all_paths"] = [(f, p, k) for f, p, k in claims]
                    for field, p, kind in claims:
                        if kind == "probably_install":
                            row["install_evidence_paths"].append((field, p))
                        elif kind == "probably_static":
                            if (root / p).exists():
                                row["static_paths_present"].append((field, p))
                            else:
                                # Advisory only — not a hard fail. Could be
                                # branch-conditional (e.g., file lands when a
                                # sibling PR merges) or aspirational. Human
                                # review decides.
                                row["static_paths_advisory_stale"].append((field, p))
                                row["stale_paths"].append((field, p))  # legacy alias
            rows.append(row)
    return rows


def summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute aggregate counts across the row set."""
    by_state: dict[str, int] = {}
    by_surface: dict[str, int] = {}
    by_registry: dict[str, dict[str, int]] = {}
    advisory_stale_rows: list[dict[str, Any]] = []
    install_evidence_rows: list[dict[str, Any]] = []
    for r in rows:
        by_state[r["state"]] = by_state.get(r["state"], 0) + 1
        by_surface[r["surface"]] = by_surface.get(r["surface"], 0) + 1
        reg = r["registry"]
        if reg not in by_registry:
            by_registry[reg] = {"ACTIVE": 0, "DEFERRED": 0, "BLOCKED": 0}
        if r["state"] in by_registry[reg]:
            by_registry[reg][r["state"]] += 1
        if r.get("static_paths_advisory_stale"):
            advisory_stale_rows.append({
                "registry": r["registry"],
                "id": r["id"],
                "name": r["name"],
                "surface": r["surface"],
                "advisory_stale_paths": r["static_paths_advisory_stale"],
            })
        if r.get("install_evidence_paths"):
            install_evidence_rows.append({
                "registry": r["registry"],
                "id": r["id"],
                "install_evidence_paths": r["install_evidence_paths"],
            })
    return {
        "total_rows": len(rows),
        "by_state": by_state,
        "by_surface": by_surface,
        "by_registry": by_registry,
        # ADVISORY (human review required): in-repo paths that the parser
        # could not verify on disk. Could be branch-conditional, aspirational,
        # or legitimately stale. The audit doesn't fail on these.
        "advisory_stale_rows": advisory_stale_rows,
        # Rows that have at least one install-evidence claim (paths outside
        # the repo or bare command names). These were SKIPPED by path-check
        # because they're not file-existence claims.
        "install_evidence_rows": install_evidence_rows,
        # Legacy alias for old callers; same content as advisory_stale_rows.
        "stale_rows": advisory_stale_rows,
    }


def main() -> int:
    """Entry point — parse, render, and optionally verify."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--verify", action="store_true",
                        help="Print summary + stale rows; exit 1 if any stale row found")
    parser.add_argument("--stale-only", action="store_true",
                        help="Print only the stale-rows report")
    parser.add_argument("--json", action="store_true",
                        help="Emit full parsed model as JSON to stdout")
    args = parser.parse_args()

    rows = parse_registries()
    s = summary(rows)

    if args.json:
        # Strip the raw dict (it's bulky) before JSON emit
        for r in rows:
            r.pop("raw", None)
        print(json.dumps({"rows": rows, "summary": s}, indent=2, default=str))
        return 0

    if args.stale_only:
        rows_with_stale = s["advisory_stale_rows"]
        if not rows_with_stale:
            print("registry_parser: no advisory-stale ACTIVE-row paths")
            return 0
        print(f"registry_parser: {len(rows_with_stale)} ACTIVE rows have advisory-stale paths:")
        print("(advisory only — could be branch-conditional, aspirational, or legitimately stale; human review decides)")
        for sr in rows_with_stale:
            print(f"  {sr['registry']} / {sr['id']}  [surface={sr['surface']}]")
            for field, p in sr["advisory_stale_paths"]:
                print(f"    {field}: {p}")
        # Exit 0 — advisory, not error. Use --verify to make it fail.
        return 1 if args.verify else 0

    # Default: human summary
    print(f"registry_parser: {s['total_rows']} rows across {len(s['by_registry'])} registries")
    print(f"  by_state:   {s['by_state']}")
    print(f"  by_surface (top 5): {dict(sorted(s['by_surface'].items(), key=lambda x: -x[1])[:5])}")
    print(f"  install-evidence ACTIVE rows: {len(s['install_evidence_rows'])}  (paths outside repo — skipped)")
    if s["advisory_stale_rows"]:
        print(f"  advisory-stale ACTIVE rows: {len(s['advisory_stale_rows'])}  (human review)")
        for sr in s["advisory_stale_rows"]:
            print(f"    {sr['registry']} / {sr['id']} [{sr['surface']}] — {len(sr['advisory_stale_paths'])} unverifiable paths")
        if args.verify:
            return 1
    else:
        print(f"  advisory-stale ACTIVE rows: 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
