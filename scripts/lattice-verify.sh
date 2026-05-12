#!/usr/bin/env bash
# LATTICE repo-wide verification entrypoint.
# Intended for humans, CI, and Pi-backed verifier personas.

set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$REPO_ROOT"

BASE_REF="${1:-origin/main}"

fail=0

echo "lattice-verify: repo=$REPO_ROOT"
echo "lattice-verify: base_ref=$BASE_REF"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "❌ Not inside a git worktree"
  exit 1
fi

if git rev-parse --verify "$BASE_REF" >/dev/null 2>&1; then
  CHANGED=$(
    {
      git diff --name-status "$BASE_REF"...HEAD || true
      git diff --name-status --cached || true
      git diff --name-status || true
    } | awk 'NF' | sort -u
  )
else
  echo "⚠️  Base ref '$BASE_REF' not found; falling back to working tree diff"
  CHANGED=$(git status --short | sed -E 's/^(.{2})[[:space:]]+/\1\t/' || true)
fi

echo ""
echo "── Protected-path tripwires ─────────────────────────────"

if [ -n "$CHANGED" ]; then
  if echo "$CHANGED" | awk '{print $NF}' | grep -qE '(^|/)\.env($|[.])'; then
    echo "❌ .env* files are human-only and must not be changed by agents"
    echo "$CHANGED" | awk '{print $NF}' | grep -E '(^|/)\.env($|[.])'
    fail=1
  fi

  if echo "$CHANGED" | awk '{print $NF}' | grep -qE '^pixeltable/migrations/00(0[1-9]|1[0-6])_.*\.py$'; then
    echo "❌ Landed migrations 0001-0016 are write-once and cannot be edited"
    echo "$CHANGED" | awk '{print $NF}' | grep -E '^pixeltable/migrations/00(0[1-9]|1[0-6])_.*\.py$'
    fail=1
  fi

  if echo "$CHANGED" | awk '$1 ~ /^D/ {print $NF}' | grep -qE '^pixeltable/migrations/.*\.py$'; then
    echo "❌ Migration deletions are human-only"
    echo "$CHANGED" | awk '$1 ~ /^D/ {print $NF}' | grep -E '^pixeltable/migrations/.*\.py$'
    fail=1
  fi
else
  echo "No changed files detected against $BASE_REF"
fi

if [ "$fail" -eq 0 ]; then
  echo "✅ Protected-path tripwires passed"
fi

echo ""
echo "── Git hygiene ───────────────────────────────────────────"
if ! git diff --check; then
  fail=1
fi

echo ""
echo "── Capability registry audit ─────────────────────────────"
if ! bash scripts/audit-dead-dna.sh; then
  fail=1
fi

echo ""
echo "── Python docstring audit ────────────────────────────────"
if ! uv run python scripts/check-python-docstrings.py --base "$BASE_REF"; then
  fail=1
fi

echo ""
echo "── Docs/pre-commit check ─────────────────────────────────"
if ! bash scripts/pre-commit-docs-check.sh; then
  fail=1
fi

if [ "$fail" -ne 0 ]; then
  echo ""
  echo "❌ lattice-verify failed"
  exit 1
fi

echo ""
echo "✅ lattice-verify passed"
