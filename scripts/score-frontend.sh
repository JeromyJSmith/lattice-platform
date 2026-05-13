#!/usr/bin/env bash
# score-frontend.sh — fitness score for the src/ (TanStack Start frontend) section.
#
# v1 formula:
#   50 pts — every route file under src/routes/**/*.tsx uses createFileRoute
#            (heuristic: all non-root .tsx files contain createFileRoute)
#   30 pts — no bare `import Anthropic` in any .ts/.tsx under src/
#   20 pts — no `@itwin/core-backend` import anywhere in src/
#
# Output: `score: N/100` on stdout, exit 0.
# With --json: emits a JSON breakdown to stdout instead.
#
# Budget: < 10s on a warm system.

set -uo pipefail

JSON=0
case "${1:-}" in
  --json) JSON=1 ;;
  --help|-h)
    cat <<EOF
Usage: scripts/score-frontend.sh [--json]

Outputs the frontend section fitness score (0-100) on stdout.
EOF
    exit 0 ;;
esac

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$REPO_ROOT"

# ---------- 1. TanStack route convention check ------------------------------
# __root.tsx is exempt (no createFileRoute — it uses createRootRoute)
TOTAL_ROUTE_FILES=$(find src/routes -name '*.tsx' 2>/dev/null | grep -v '__root.tsx' | wc -l | tr -d ' ')
CONFORMING_FILES=$(find src/routes -name '*.tsx' 2>/dev/null | grep -v '__root.tsx' | xargs grep -l 'createFileRoute' 2>/dev/null | wc -l | tr -d ' ')

# ---------- 2. No bare import Anthropic in src/ -----------------------------
ANTHROPIC_HITS=$(grep -rE '^import Anthropic' src/ --include='*.ts' --include='*.tsx' 2>/dev/null | wc -l | tr -d ' ')

# ---------- 3. No @itwin/core-backend in src/ --------------------------------
ITWIN_BACKEND_HITS=$(grep -rE '@itwin/core-backend' src/ --include='*.ts' --include='*.tsx' --include='*.js' 2>/dev/null | wc -l | tr -d ' ')

# ---------- 4. Compute score -------------------------------------------------
# 50 pts: route file conformance (proportional)
PTS_ROUTES=0
if [ "$TOTAL_ROUTE_FILES" -gt 0 ]; then
  PTS_ROUTES=$(( 50 * CONFORMING_FILES / TOTAL_ROUTE_FILES ))
elif [ "$TOTAL_ROUTE_FILES" -eq 0 ]; then
  # No route files = no routes scaffold = 0
  PTS_ROUTES=0
fi

# 30 pts: no bare import Anthropic
if [ "$ANTHROPIC_HITS" -eq 0 ]; then
  PTS_ANTHROPIC=30
else
  PTS_ANTHROPIC=$(( 30 - ANTHROPIC_HITS * 10 ))
  [ "$PTS_ANTHROPIC" -lt 0 ] && PTS_ANTHROPIC=0
fi

# 20 pts: no @itwin/core-backend
if [ "$ITWIN_BACKEND_HITS" -eq 0 ]; then
  PTS_ITWIN=20
else
  PTS_ITWIN=$(( 20 - ITWIN_BACKEND_HITS * 5 ))
  [ "$PTS_ITWIN" -lt 0 ] && PTS_ITWIN=0
fi

SCORE=$(( PTS_ROUTES + PTS_ANTHROPIC + PTS_ITWIN ))

# ---------- 5. Output -------------------------------------------------------
if [ "$JSON" -eq 1 ]; then
  cat <<EOF
{
  "section": "frontend",
  "score": $SCORE,
  "breakdown": {
    "tanstack_route_convention": {"points": $PTS_ROUTES, "max": 50, "conforming": $CONFORMING_FILES, "total": $TOTAL_ROUTE_FILES},
    "no_bare_anthropic":        {"points": $PTS_ANTHROPIC, "max": 30, "hits": $ANTHROPIC_HITS},
    "no_itwin_core_backend":    {"points": $PTS_ITWIN, "max": 20, "hits": $ITWIN_BACKEND_HITS}
  }
}
EOF
else
  echo "score: $SCORE/100"
fi
exit 0
