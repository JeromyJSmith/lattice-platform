#!/usr/bin/env bash
# score-vw-itwin.sh — fitness score for the vw-itwin section (0-100).
#
# Scoring formula (spec v2):
#   +25  vw-plugin/src/ has >=1 .cpp or .h file
#   +25  grep for "ifcopenshell" in pixeltable/service/ finds >=1 match
#   +25  pixeltable/service/routes/ingest.py or any ingest file exists
#   +25  meta/capability-research/mapping/operator-workflow-map.md exists
#
# Output: single integer on stdout (first number — grep -oE '[0-9]+' | head -1).
# Compatible with run-autoresearch.sh SCORE_BEFORE/SCORE_AFTER extraction.

set -uo pipefail

REPO=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$REPO"

SCORE=0

# +25 if vw-plugin/src/ has >=1 .cpp or .h file
CPP_COUNT=$(find vw-plugin/src -maxdepth 3 \( -name '*.cpp' -o -name '*.h' \) 2>/dev/null | wc -l | tr -d ' ')
if [ "$CPP_COUNT" -ge 1 ]; then
  SCORE=$(( SCORE + 25 ))
fi

# +25 if grep for "ifcopenshell" in pixeltable/service/ finds >=1 match
IFC_MATCHES=$(grep -rl 'ifcopenshell' pixeltable/service/ 2>/dev/null | wc -l | tr -d ' ')
if [ "$IFC_MATCHES" -ge 1 ]; then
  SCORE=$(( SCORE + 25 ))
fi

# +25 if pixeltable/service/routes/ingest.py or any ingest file exists
INGEST_COUNT=$(find pixeltable/service -maxdepth 3 -name '*ingest*' 2>/dev/null | wc -l | tr -d ' ')
if [ "$INGEST_COUNT" -ge 1 ]; then
  SCORE=$(( SCORE + 25 ))
fi

# +25 if meta/capability-research/mapping/operator-workflow-map.md exists
if [ -f "meta/capability-research/mapping/operator-workflow-map.md" ]; then
  SCORE=$(( SCORE + 25 ))
fi

echo "$SCORE"
