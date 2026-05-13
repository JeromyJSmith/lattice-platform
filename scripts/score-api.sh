#!/usr/bin/env bash
# score-api.sh — fitness score for the pixeltable/service/ (FastAPI sidecar) section.
#
# v1 formula:
#   50 pts — endpoint count in code matches declared count in meta/API.md
#            (@router.* in routes/ + @app.* in main.py vs **N endpoints** in API.md)
#   30 pts — every router file imports APIRouter AND has at least one decorated function
#   20 pts — no bare `import Anthropic` in any .ts/.tsx under pixeltable/service/
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
Usage: scripts/score-api.sh [--json]

Outputs the FastAPI sidecar section fitness score (0-100) on stdout.
EOF
    exit 0 ;;
esac

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$REPO_ROOT"

# ---------- 1. Actual endpoint count ----------------------------------------
ROUTER_ENDPOINTS=$(grep -rhE '^@router\.(get|post|put|delete|patch)' pixeltable/service/routes/ 2>/dev/null | wc -l | tr -d ' ')
APP_ENDPOINTS=$(grep -cE '^@app\.(get|post|put|delete|patch)' pixeltable/service/main.py 2>/dev/null || true)
APP_ENDPOINTS=${APP_ENDPOINTS:-0}
[ -z "$APP_ENDPOINTS" ] && APP_ENDPOINTS=0
ACTUAL_ENDPOINTS=$(( ROUTER_ENDPOINTS + APP_ENDPOINTS ))

# ---------- 2. Declared endpoint count in meta/API.md -----------------------
DECLARED_ENDPOINTS=$(grep -oE '\*\*[0-9]+ endpoints?\*\*' meta/API.md 2>/dev/null | head -1 | grep -oE '[0-9]+' || echo 0)

# ---------- 3. Router file health -------------------------------------------
ROUTER_FILES=$(find pixeltable/service/routes -maxdepth 1 -name '*.py' -not -name '__init__.py' 2>/dev/null | wc -l | tr -d ' ')
ROUTER_HEALTHY=0
ROUTER_CHECKED=0
if [ "$ROUTER_FILES" -gt 0 ]; then
  for f in pixeltable/service/routes/*.py; do
    [ "$f" = "pixeltable/service/routes/__init__.py" ] && continue
    has_import=$(grep -c 'APIRouter' "$f" 2>/dev/null || true); has_import=${has_import:-0}
    has_route=$(grep -cE '@router\.(get|post|put|delete|patch)' "$f" 2>/dev/null || true); has_route=${has_route:-0}
    ROUTER_CHECKED=$(( ROUTER_CHECKED + 1 ))
    if [ "$has_import" -gt 0 ] && [ "$has_route" -gt 0 ]; then
      ROUTER_HEALTHY=$(( ROUTER_HEALTHY + 1 ))
    fi
  done
fi

# ---------- 4. Forbidden import Anthropic in .ts/.tsx under pixeltable/ -----
ANTHROPIC_HITS=$(grep -rE '^import Anthropic' pixeltable/ --include='*.ts' --include='*.tsx' 2>/dev/null | wc -l | tr -d ' ')

# ---------- 5. Compute score -------------------------------------------------
# 50 pts: endpoint count match (partial credit within ±5)
PTS_ENDPOINTS=0
if [ "$DECLARED_ENDPOINTS" -gt 0 ] && [ "$ACTUAL_ENDPOINTS" -eq "$DECLARED_ENDPOINTS" ]; then
  PTS_ENDPOINTS=50
elif [ "$DECLARED_ENDPOINTS" -gt 0 ] && [ "$ACTUAL_ENDPOINTS" -gt 0 ]; then
  if [ "$ACTUAL_ENDPOINTS" -gt "$DECLARED_ENDPOINTS" ]; then
    DIFF=$(( ACTUAL_ENDPOINTS - DECLARED_ENDPOINTS ))
  else
    DIFF=$(( DECLARED_ENDPOINTS - ACTUAL_ENDPOINTS ))
  fi
  PTS_ENDPOINTS=$(( 50 - DIFF * 5 ))
  [ "$PTS_ENDPOINTS" -lt 0 ] && PTS_ENDPOINTS=0
fi

# 30 pts: all router files healthy (proportional)
PTS_ROUTERS=0
if [ "$ROUTER_CHECKED" -gt 0 ]; then
  PTS_ROUTERS=$(( 30 * ROUTER_HEALTHY / ROUTER_CHECKED ))
fi

# 20 pts: no bare import Anthropic
if [ "$ANTHROPIC_HITS" -eq 0 ]; then
  PTS_ANTHROPIC=20
else
  PTS_ANTHROPIC=$(( 20 - ANTHROPIC_HITS * 5 ))
  [ "$PTS_ANTHROPIC" -lt 0 ] && PTS_ANTHROPIC=0
fi

SCORE=$(( PTS_ENDPOINTS + PTS_ROUTERS + PTS_ANTHROPIC ))

# ---------- 6. Output --------------------------------------------------------
if [ "$JSON" -eq 1 ]; then
  cat <<EOF
{
  "section": "api",
  "score": $SCORE,
  "breakdown": {
    "endpoint_count_match": {"points": $PTS_ENDPOINTS, "max": 50, "declared": $DECLARED_ENDPOINTS, "actual": $ACTUAL_ENDPOINTS},
    "router_health":        {"points": $PTS_ROUTERS, "max": 30, "healthy": $ROUTER_HEALTHY, "checked": $ROUTER_CHECKED},
    "no_bare_anthropic":    {"points": $PTS_ANTHROPIC, "max": 20, "hits": $ANTHROPIC_HITS}
  }
}
EOF
else
  echo "score: $SCORE/100"
fi
exit 0
