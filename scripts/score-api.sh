#!/usr/bin/env bash
# score-api.sh — fitness score for the api section (0-100).
#
# Scoring formula (spec v2):
#   +25  pixeltable/service/main.py exists
#   +25  grep for "router" in pixeltable/service/routes/ finds >=8 matches
#   +25  meta/API.md mentions >=30 endpoints (a number >=30 near "endpoint")
#   +25  pixeltable/service/routes/harness_health.py exists
#
# Output: single integer on stdout (first number — grep -oE '[0-9]+' | head -1).
# Compatible with run-autoresearch.sh SCORE_BEFORE/SCORE_AFTER extraction.

set -uo pipefail

REPO=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$REPO"

SCORE=0

# +25 if pixeltable/service/main.py exists
if [ -f "pixeltable/service/main.py" ]; then
  SCORE=$(( SCORE + 25 ))
fi

# +25 if grep for "router" in pixeltable/service/routes/ finds >=8 matches
ROUTER_MATCHES=$(grep -rl 'router' pixeltable/service/routes/ 2>/dev/null | wc -l | tr -d ' ')
if [ "$ROUTER_MATCHES" -ge 8 ]; then
  SCORE=$(( SCORE + 25 ))
fi

# +25 if meta/API.md mentions >=30 endpoints (a number >=30 near "endpoint")
ENDPOINT_NUM=$(grep -oE '[0-9]+ endpoints?' meta/API.md 2>/dev/null | grep -oE '[0-9]+' | head -1 || echo 0)
if [ "$ENDPOINT_NUM" -ge 30 ] 2>/dev/null; then
  SCORE=$(( SCORE + 25 ))
fi

# +25 if pixeltable/service/routes/harness_health.py exists
if [ -f "pixeltable/service/routes/harness_health.py" ]; then
  SCORE=$(( SCORE + 25 ))
fi

echo "$SCORE"
