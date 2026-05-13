#!/usr/bin/env bash
# score-ddc.sh — fitness score for the ddc section (0-100).
#
# Scoring formula (spec v2):
#   +25  meta/ has any file mentioning "DDC" (grep -rl)
#   +25  analysis/capabilities/ has a registry yaml with "ddc" in the filename
#   +25  meta/ARCHITECTURE.md mentions "DDC"
#   +25  meta/capability-research/ has any file mentioning "CWICR" or "OpenConstruction"
#
# Output: single integer on stdout (first number — grep -oE '[0-9]+' | head -1).
# Compatible with run-autoresearch.sh SCORE_BEFORE/SCORE_AFTER extraction.

set -uo pipefail

REPO=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$REPO"

SCORE=0

# +25 if meta/ has any file mentioning "DDC"
DDC_META=$(grep -rl 'DDC' meta/ 2>/dev/null | wc -l | tr -d ' ')
if [ "$DDC_META" -ge 1 ]; then
  SCORE=$(( SCORE + 25 ))
fi

# +25 if analysis/capabilities/ has a registry yaml with "ddc" in the filename
DDC_YAML=$(find analysis/capabilities -maxdepth 3 \( -name '*ddc*.yaml' -o -name '*ddc*.yml' \) 2>/dev/null | wc -l | tr -d ' ')
if [ "$DDC_YAML" -ge 1 ]; then
  SCORE=$(( SCORE + 25 ))
fi

# +25 if meta/ARCHITECTURE.md mentions "DDC"
if grep -q 'DDC' meta/ARCHITECTURE.md 2>/dev/null; then
  SCORE=$(( SCORE + 25 ))
fi

# +25 if meta/capability-research/ has any file mentioning "CWICR" or "OpenConstruction"
CWICR_HITS=$(grep -rl 'CWICR\|OpenConstruction' meta/capability-research/ 2>/dev/null | wc -l | tr -d ' ')
if [ "$CWICR_HITS" -ge 1 ]; then
  SCORE=$(( SCORE + 25 ))
fi

echo "$SCORE"
