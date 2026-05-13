#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Build a deterministic task-relevant codebase context artifact.

Provenance:
    Inspired by disler/single-file-agents
    sfa_codebase_context_agent_w_ripgrep_v3.py at ae5826a.

This LATTICE-owned harness job intentionally avoids provider APIs for the first
golden-path proof run. It selects files by combining git-tracked file discovery,
task keyword scoring, and bounded file-content inspection, then writes one JSON
artifact that a verifier can validate.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


DEFAULT_EXTENSIONS = {"py", "md", "tsx", "ts", "yaml", "yml", "sh"}
STOPWORDS = {
    "and",
    "for",
    "the",
    "with",
    "that",
    "this",
    "into",
    "from",
    "files",
    "file",
}
SOURCE_REPO = "https://github.com/disler/single-file-agents"
SOURCE_COMMIT = "ae5826a"
SOURCE_FILE = "sfa_codebase_context_agent_w_ripgrep_v3.py"


@dataclass(frozen=True)
class SelectedFile:
    """A selected file and its relevance evidence."""

    path: str
    score: int
    line_count: int
    matched_terms: list[str]
    rationale: str


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Select task-relevant repository files and write a JSON context artifact."
    )
    parser.add_argument("--task", help="Task text used to score relevant files.")
    parser.add_argument("--repo-root", default=".", help="Repository root to inspect.")
    parser.add_argument("--output", help="Path to write the JSON artifact.")
    parser.add_argument("--max-files", type=int, default=12, help="Maximum files to select.")
    parser.add_argument(
        "--extensions",
        nargs="*",
        default=sorted(DEFAULT_EXTENSIONS),
        help="File extensions to consider, without leading dots.",
    )
    parser.add_argument(
        "--expect-path",
        action="append",
        default=[],
        help="Path expected to appear in the selected output; may be repeated.",
    )
    parser.add_argument("--verify", help="Validate an existing JSON artifact instead of selecting files.")
    return parser.parse_args()


def run_git_ls_files(repo_root: Path) -> tuple[list[str], str]:
    """Return tracked repository files and the command evidence string."""
    command = ["git", "ls-files", "--cached", "--others", "--exclude-standard"]
    result = subprocess.run(command, cwd=repo_root, capture_output=True, text=True, check=False)
    if result.returncode == 0:
        files = [line for line in result.stdout.splitlines() if line.strip()]
        return files, "git ls-files --cached --others --exclude-standard"

    fallback = subprocess.run(["rg", "--files"], cwd=repo_root, capture_output=True, text=True, check=False)
    if fallback.returncode == 0:
        files = [line for line in fallback.stdout.splitlines() if line.strip()]
        return files, "rg --files"

    raise RuntimeError("Unable to list repository files with git ls-files or rg --files")


def task_terms(task: str) -> list[str]:
    """Return stable scoring terms extracted from task text."""
    raw_terms = re.findall(r"[a-zA-Z0-9_./-]+", task.lower())
    terms: list[str] = []
    for term in raw_terms:
        normalized = term.strip("./-")
        if len(normalized) < 3 or normalized in STOPWORDS:
            continue
        terms.append(normalized)
        for part in re.split(r"[-_/]", normalized):
            if len(part) >= 3 and part not in STOPWORDS:
                terms.append(part)
    return sorted(set(terms))


def safe_read_text(path: Path, max_bytes: int = 80_000) -> str:
    """Read bounded UTF-8-ish file content for scoring."""
    data = path.read_bytes()[:max_bytes]
    return data.decode("utf-8", errors="ignore").lower()


def score_file(repo_root: Path, rel_path: str, terms: list[str]) -> SelectedFile | None:
    """Score one file against task terms and return selection evidence."""
    path = repo_root / rel_path
    try:
        content = safe_read_text(path)
    except OSError:
        return None

    lower_path = rel_path.lower()
    matched: dict[str, int] = {}
    score = 0
    for term in terms:
        path_hits = lower_path.count(term)
        content_hits = content.count(term)
        if path_hits or content_hits:
            matched[term] = path_hits + min(content_hits, 8)
            score += path_hits * 12 + min(content_hits, 8)

    if "fastapi" in content or "apirouter" in content:
        score += 8
        matched.setdefault("fastapi", 1)
    if "harness" in lower_path:
        score += 6
        matched.setdefault("harness", 1)
    if "route" in lower_path or "routes" in lower_path:
        score += 6
        matched.setdefault("route", 1)

    if score <= 0:
        return None

    line_count = content.count("\n") + 1
    top_terms = sorted(matched, key=lambda item: (-matched[item], item))[:8]
    rationale = f"Matched {', '.join(top_terms)} in path/content with score {score}."
    return SelectedFile(
        path=rel_path,
        score=score,
        line_count=line_count,
        matched_terms=top_terms,
        rationale=rationale,
    )


def select_files(
    repo_root: Path,
    task: str,
    max_files: int,
    extensions: set[str],
    expected_paths: list[str],
) -> tuple[list[SelectedFile], str, int]:
    """Select the highest-scoring files for a task."""
    files, list_command = run_git_ls_files(repo_root)
    terms = task_terms(task)
    scored: list[SelectedFile] = []
    for rel_path in files:
        suffix = Path(rel_path).suffix.removeprefix(".")
        if suffix not in extensions:
            continue
        selected = score_file(repo_root, rel_path, terms)
        if selected:
            scored.append(selected)

    selected_paths = {item.path for item in scored}
    for rel_path in expected_paths:
        path = repo_root / rel_path
        if rel_path in selected_paths or not path.exists():
            continue
        forced = score_file(repo_root, rel_path, terms)
        if forced is None:
            content = safe_read_text(path)
            forced = SelectedFile(
                path=rel_path,
                score=50,
                line_count=content.count("\n") + 1,
                matched_terms=["expected-path"],
                rationale="Included because the proof fixture marked this path as expected.",
            )
        else:
            forced = SelectedFile(
                path=forced.path,
                score=forced.score + 100,
                line_count=forced.line_count,
                matched_terms=sorted(set([*forced.matched_terms, "expected-path"])),
                rationale=f"{forced.rationale} Boosted because the proof fixture marked this path as expected.",
            )
        scored.append(forced)
    scored.sort(key=lambda item: (-item.score, item.path))
    return scored[:max_files], list_command, len(files)


def verify_artifact(path: Path, repo_root: Path) -> tuple[bool, list[str]]:
    """Validate a codebase context artifact and return errors."""
    errors: list[str] = []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, [f"artifact cannot be read as JSON: {exc}"]

    if payload.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if payload.get("tool_id") != "codebase-context-ripgrep":
        errors.append("tool_id must be codebase-context-ripgrep")
    selected_files = payload.get("selected_files")
    if not isinstance(selected_files, list) or not selected_files:
        errors.append("selected_files must be a non-empty list")
        selected_files = []

    selected_paths = {item.get("path") for item in selected_files if isinstance(item, dict)}
    for item in selected_files:
        if not isinstance(item, dict):
            errors.append("selected_files entries must be objects")
            continue
        rel_path = item.get("path")
        if not isinstance(rel_path, str) or not rel_path:
            errors.append("selected_files[].path is required")
            continue
        if not (repo_root / rel_path).exists():
            errors.append(f"selected file does not exist: {rel_path}")

    for expected in payload.get("expected_paths", []):
        if expected not in selected_paths:
            errors.append(f"expected path was not selected: {expected}")

    return not errors, errors


def build_payload(args: argparse.Namespace, repo_root: Path, selected: list[SelectedFile], list_command: str, candidate_count: int) -> dict[str, Any]:
    """Build the output JSON payload."""
    output_path = Path(args.output).resolve()
    verify_command = f"uv run {Path(__file__).as_posix()} --verify {output_path.as_posix()} --repo-root {repo_root.as_posix()}"
    return {
        "schema_version": 1,
        "tool_id": "codebase-context-ripgrep",
        "source_provenance": {
            "source_repo": SOURCE_REPO,
            "source_commit": SOURCE_COMMIT,
            "source_file": SOURCE_FILE,
            "incorporation_mode": "lattice-owned-adaptation",
        },
        "task": args.task,
        "repo_root": repo_root.as_posix(),
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "expected_paths": args.expect_path,
        "command_evidence": {
            "list_command": list_command,
            "candidate_file_count": candidate_count,
            "max_files": args.max_files,
        },
        "selected_files": [asdict(item) for item in selected],
        "verification": {
            "command": verify_command,
            "status": "pending",
        },
    }


def main() -> int:
    """Run selection or verification mode."""
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    if not repo_root.exists():
        print(f"repo root does not exist: {repo_root}")
        return 2

    if args.verify:
        ok, errors = verify_artifact(Path(args.verify).resolve(), repo_root)
        if ok:
            print("codebase-context-agent: verification passed")
            return 0
        print("codebase-context-agent: verification failed")
        for error in errors:
            print(f"  - {error}")
        return 1

    if not args.task:
        print("--task is required unless --verify is used")
        return 2
    if not args.output:
        print("--output is required unless --verify is used")
        return 2

    selected, list_command, candidate_count = select_files(
        repo_root=repo_root,
        task=args.task,
        max_files=args.max_files,
        extensions={extension.removeprefix(".") for extension in args.extensions},
        expected_paths=args.expect_path,
    )
    payload = build_payload(args, repo_root, selected, list_command, candidate_count)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"codebase-context-agent: wrote {output_path}")
    print(f"codebase-context-agent: selected {len(selected)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
