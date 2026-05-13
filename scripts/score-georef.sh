#!/usr/bin/env bash
# score-georef.sh — fitness score for the georef section (0-100).
#
# Scoring formula (spec v2):
#   +25  georef/converters/ has >=3 files
#   +25  grep for "EPSG" in pixeltable/migrations/ finds >=1 match
#   +25  lattice/reality/ dir exists in any migration file reference
#   +25  meta/capability-research/ has >=5 files (find -type f)
#
# Output: single integer on stdout (first number — grep -oE '[0-9]+' | head -1).
# Compatible with run-autoresearch.sh SCORE_BEFORE/SCORE_AFTER extraction.

set -uo pipefail

REPO=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$REPO"

SCORE=0

# +25 if georef/converters/ has >=3 files
CONVERTER_COUNT=$(find georef/converters -maxdepth 2 -type f 2>/dev/null | wc -l | tr -d ' ')
if [ "$CONVERTER_COUNT" -ge 3 ]; then
  SCORE=$(( SCORE + 25 ))
fi

# +25 if grep for "EPSG" in pixeltable/migrations/ finds >=1 match
EPSG_MATCHES=$(grep -rl 'EPSG' pixeltable/migrations/ 2>/dev/null | wc -l | tr -d ' ')
if [ "$EPSG_MATCHES" -ge 1 ]; then
  SCORE=$(( SCORE + 25 ))
fi

# +25 if lattice/reality/ dir exists in any migration file reference
REALITY_REF=$(grep -rl 'lattice/reality' pixeltable/migrations/ 2>/dev/null | wc -l | tr -d ' ')
if [ "$REALITY_REF" -ge 1 ]; then
  SCORE=$(( SCORE + 25 ))
fi

# +25 if meta/capability-research/ has >=5 files
CAPRES_COUNT=$(find meta/capability-research -type f 2>/dev/null | wc -l | tr -d ' ')
if [ "$CAPRES_COUNT" -ge 5 ]; then
  SCORE=$(( SCORE + 25 ))
fi

echo "$SCORE"
