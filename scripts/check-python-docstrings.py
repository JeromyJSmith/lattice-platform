#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Check changed Python files for module, function, class, and method docstrings."""

from __future__ import annotations

import argparse
import ast
import subprocess
import sys
from pathlib import Path


EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "references",
    "benchy",
    "examples",
}

PROTECTED_MIGRATION_PATTERN = "pixeltable/migrations/00"


def repo_root() -> Path:
    """Return the git repository root or the current working directory."""
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return Path(result.stdout.strip())
    return Path.cwd()


def git_lines(root: Path, command: list[str]) -> list[str]:
    """Return stdout lines from a git command, or an empty list on failure."""
    result = subprocess.run(command, cwd=root, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def is_protected_landed_migration(root: Path, path: Path) -> bool:
    """Return true for write-once migration files 0001 through 0016."""
    try:
        rel = path.relative_to(root).as_posix()
    except ValueError:
        return False
    if not rel.startswith(PROTECTED_MIGRATION_PATTERN):
        return False
    name = path.name
    if len(name) < 4 or not name[:4].isdigit():
        return False
    return 1 <= int(name[:4]) <= 16


def ref_exists(root: Path, ref: str) -> bool:
    """Return true when a git ref can be resolved."""
    result = subprocess.run(
        ["git", "rev-parse", "--verify", ref],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def collect_python_files(root: Path, scan_all: bool, base_ref: str | None) -> list[Path]:
    """Return Python files to check for the selected scan mode."""
    if scan_all:
        commands = [["git", "ls-files", "*.py"]]
    else:
        commands = []
        if base_ref and ref_exists(root, base_ref):
            commands.append(["git", "diff", "--name-only", f"{base_ref}...HEAD"])
        commands.extend(
            [
                ["git", "diff", "--name-only", "HEAD"],
                ["git", "diff", "--name-only", "--cached"],
                ["git", "ls-files", "--others", "--exclude-standard", "*.py"],
            ]
        )
    files: set[Path] = set()
    for command in commands:
        for line in git_lines(root, command):
            path = root / line.strip()
            if (
                path.suffix == ".py"
                and path.exists()
                and not is_excluded(path)
                and not is_protected_landed_migration(root, path)
            ):
                files.add(path)
    return sorted(files)


def is_excluded(path: Path) -> bool:
    """Return true when a file lives in generated or dependency directories."""
    return any(part in EXCLUDED_PARTS for part in path.parts)


def public_functions(tree: ast.AST) -> list[ast.AST]:
    """Return public function, async function, class, and method nodes."""
    nodes: list[ast.AST] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name.startswith("_"):
                continue
            nodes.append(node)
    return nodes


def check_file(path: Path) -> list[str]:
    """Return docstring violations for one Python file."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        return [f"{path}: syntax error: {exc}"]

    errors: list[str] = []
    if ast.get_docstring(tree) is None:
        errors.append(f"{path}: missing module docstring")

    for node in public_functions(tree):
        if ast.get_docstring(node) is None:
            errors.append(f"{path}:{node.lineno}: {type(node).__name__} {node.name!r} missing docstring")

    return errors


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Require module and public symbol docstrings in changed Python files. "
            "Use --all for a deliberate full-repo baseline pass."
        )
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="scan every tracked Python file except write-once landed migrations",
    )
    parser.add_argument(
        "--base",
        help="optional git ref for PR-style changed-file detection, for example origin/main",
    )
    return parser.parse_args()


def main() -> int:
    """Run the docstring check and print violations."""
    args = parse_args()
    root = repo_root()
    files = collect_python_files(root, scan_all=args.all, base_ref=args.base)
    errors: list[str] = []
    for path in files:
        errors.extend(check_file(path))

    if errors:
        print("check-python-docstrings: violations found")
        for error in errors:
            print(f"  - {error}")
        return 1

    mode = "all tracked files" if args.all else "changed/new files"
    print(f"check-python-docstrings: OK ({len(files)} {mode})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
