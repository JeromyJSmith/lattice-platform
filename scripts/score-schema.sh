#!/usr/bin/env bash
# score-schema.sh — fitness score for the schema section (0-100).
#
# Scoring formula (spec v2):
#   +20  migrations dir has >=13 .py files matching [0-9]{4}_*.py
#   +20  pixeltable/schemas/.schema-snapshot.yaml exists
#   +20  meta/SCHEMA.md mentions "36 tables" or a number >=30
#   +20  pixeltable/migrations/_helpers.py exists
#   +20  pixeltable/service/routes/ has >=8 .py files
#
# Output: single integer on stdout (first number — grep -oE '[0-9]+' | head -1).
# Compatible with run-autoresearch.sh SCORE_BEFORE/SCORE_AFTER extraction.

set -uo pipefail

REPO=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$REPO"

SCORE=0

# +20 if migrations dir has >=13 .py files matching [0-9]{4}_*.py
MIGRATION_COUNT=$(find pixeltable/migrations -maxdepth 1 -name '[0-9][0-9][0-9][0-9]_*.py' 2>/dev/null | wc -l | tr -d ' ')
if [ "$MIGRATION_COUNT" -ge 13 ]; then
  SCORE=$(( SCORE + 20 ))
fi

# +20 if pixeltable/schemas/.schema-snapshot.yaml exists
if [ -f "pixeltable/schemas/.schema-snapshot.yaml" ]; then
  SCORE=$(( SCORE + 20 ))
fi

# +20 if meta/SCHEMA.md mentions "36 tables" or a number >=30
TABLE_NUM=$(grep -oE '[0-9]+ tables?' meta/SCHEMA.md 2>/dev/null | grep -oE '[0-9]+' | head -1 || echo 0)
if [ "$TABLE_NUM" -ge 30 ] 2>/dev/null; then
  SCORE=$(( SCORE + 20 ))
fi

# +20 if pixeltable/migrations/_helpers.py exists
if [ -f "pixeltable/migrations/_helpers.py" ]; then
  SCORE=$(( SCORE + 20 ))
fi

# +20 if pixeltable/service/routes/ has >=8 .py files
ROUTE_COUNT=$(find pixeltable/service/routes -maxdepth 1 -name '*.py' 2>/dev/null | wc -l | tr -d ' ')
if [ "$ROUTE_COUNT" -ge 8 ]; then
  SCORE=$(( SCORE + 20 ))
fi

echo "$SCORE"
