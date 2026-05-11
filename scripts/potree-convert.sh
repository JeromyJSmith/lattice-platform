#!/usr/bin/env bash
# Wrap PotreeConverter to produce a Potree octree from a .las/.laz file.
#
# Tracked in meta/FEATURE_BACKLOG.md § POINT CLOUD → "PotreeConverter integration".
#
# Usage:
#   ./scripts/potree-convert.sh <input.las> <project_id>
#
# Output:
#   public/potree/<project_id>/         (octree, hierarchy.bin, metadata.json)
#
# Requires PotreeConverter on PATH. On Apple Silicon, build from source per
# https://github.com/potree/PotreeConverter (no official ARM64 binary).

set -euo pipefail

INPUT="${1:-}"
PROJECT_ID="${2:-}"

if [[ -z "$INPUT" || -z "$PROJECT_ID" ]]; then
  echo "usage: $0 <input.las> <project_id>" >&2
  exit 1
fi

if [[ ! -f "$INPUT" ]]; then
  echo "error: input file not found: $INPUT" >&2
  exit 1
fi

if ! command -v PotreeConverter >/dev/null 2>&1; then
  echo "error: PotreeConverter not on PATH" >&2
  echo "  build from https://github.com/potree/PotreeConverter and ensure ARM64 build on Apple Silicon" >&2
  exit 1
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$REPO_ROOT/public/potree/$PROJECT_ID"

mkdir -p "$OUT_DIR"
echo "converting $INPUT -> $OUT_DIR"
PotreeConverter "$INPUT" -o "$OUT_DIR" --generate-page "$PROJECT_ID"
echo "done. open public/potree/$PROJECT_ID/$PROJECT_ID.html to verify locally."
