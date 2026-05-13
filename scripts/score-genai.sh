#!/usr/bin/env bash
# score-genai.sh — fitness score for the genai section (0-100).
#
# Scoring formula (spec v2):
#   +25  meta/harness/bin/llama-swap/ exists
#   +25  meta/harness/in-tab-llm/bonsai-host.html exists
#   +25  meta/harness/tools/sfa-eval/ has >=3 .py files
#   +25  analysis/capabilities/ has a registry yaml mentioning "genai"
#
# Output: single integer on stdout (first number — grep -oE '[0-9]+' | head -1).
# Compatible with run-autoresearch.sh SCORE_BEFORE/SCORE_AFTER extraction.

set -uo pipefail

REPO=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$REPO"

SCORE=0

# +25 if meta/harness/bin/llama-swap/ exists
if [ -d "meta/harness/bin/llama-swap" ]; then
  SCORE=$(( SCORE + 25 ))
fi

# +25 if meta/harness/in-tab-llm/bonsai-host.html exists
if [ -f "meta/harness/in-tab-llm/bonsai-host.html" ]; then
  SCORE=$(( SCORE + 25 ))
fi

# +25 if meta/harness/tools/sfa-eval/ has >=3 .py files
SFA_COUNT=$(find meta/harness/tools/sfa-eval -maxdepth 2 -name '*.py' 2>/dev/null | wc -l | tr -d ' ')
if [ "$SFA_COUNT" -ge 3 ]; then
  SCORE=$(( SCORE + 25 ))
fi

# +25 if analysis/capabilities/ has a registry yaml mentioning "genai"
GENAI_YAML=$(grep -rl 'genai' analysis/capabilities/ --include='*.yaml' --include='*.yml' 2>/dev/null | wc -l | tr -d ' ')
if [ "$GENAI_YAML" -ge 1 ]; then
  SCORE=$(( SCORE + 25 ))
fi

echo "$SCORE"
