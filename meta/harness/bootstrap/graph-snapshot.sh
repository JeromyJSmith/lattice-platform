#!/usr/bin/env bash
# graph-snapshot.sh — run graphify over the LATTICE repo and emit a graph snapshot.
#
# Used by:
#   - graphify cli-run (graphify-parisgroup registry)
#
# Usage:
#   bash meta/harness/bootstrap/graph-snapshot.sh [--dry]
#
# --dry  prints the command that would run without executing graphify.
#
# Output:
#   Writes graphify JSON output to analysis/graphify/snapshot-<date>.json
#   Symlinks analysis/graphify/latest.json to the new file.

set -uo pipefail

DRY=0
if [ "${1:-}" = "--dry" ]; then
  DRY=1
fi

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -z "$REPO_ROOT" ]; then
  echo "ERROR: Not inside a git repository" >&2
  exit 1
fi
cd "$REPO_ROOT"

OUT_DIR="analysis/graphify"
mkdir -p "$OUT_DIR"

STAMP=$(date +%Y-%m-%d)
OUT_FILE="$OUT_DIR/snapshot-${STAMP}.json"

CMD=(graphify run --output "$OUT_FILE" --format json)

if [ "$DRY" -eq 1 ]; then
  echo "[graph-snapshot] dry-run: ${CMD[*]}"
  exit 0
fi

if ! command -v graphify &>/dev/null; then
  echo "[graph-snapshot] graphify not installed — skipping snapshot" >&2
  exit 0
fi

echo "[graph-snapshot] Running: ${CMD[*]}"
"${CMD[@]}"

# Symlink latest
ln -sf "$(basename "$OUT_FILE")" "$OUT_DIR/latest.json"
echo "[graph-snapshot] Snapshot written to $OUT_FILE"
