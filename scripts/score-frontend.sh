#!/usr/bin/env bash
# score-frontend.sh — fitness score for the frontend section (0-100).
#
# Scoring formula (spec v2):
#   +25  src/routes/ has >=3 files
#   +25  src/server/runtime/ exists
#   +25  bun.lockb or package.json exists at repo root
#   +25  src/db/collections.ts exists
#
# Output: single integer on stdout (first number — grep -oE '[0-9]+' | head -1).
# Compatible with run-autoresearch.sh SCORE_BEFORE/SCORE_AFTER extraction.

set -uo pipefail

REPO=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$REPO"

SCORE=0

# +25 if src/routes/ has >=3 files
ROUTE_COUNT=$(find src/routes -maxdepth 2 -type f 2>/dev/null | wc -l | tr -d ' ')
if [ "$ROUTE_COUNT" -ge 3 ]; then
  SCORE=$(( SCORE + 25 ))
fi

# +25 if src/server/runtime/ exists
if [ -d "src/server/runtime" ]; then
  SCORE=$(( SCORE + 25 ))
fi

# +25 if bun.lockb or package.json exists at repo root
if [ -f "bun.lockb" ] || [ -f "package.json" ]; then
  SCORE=$(( SCORE + 25 ))
fi

# +25 if src/db/collections.ts exists
if [ -f "src/db/collections.ts" ]; then
  SCORE=$(( SCORE + 25 ))
fi

echo "$SCORE"
