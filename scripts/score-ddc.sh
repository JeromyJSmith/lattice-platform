#!/usr/bin/env bash
# score-ddc.sh — fitness score for the ddc/ + .github/ sections.
#
# v1 formula:
#   50 pts — count of .github/workflows/*.yml files that do NOT contain `|| true`
#            (warning-bypass pattern; clean CI workflows score higher)
#   30 pts — meta/DDC_MAPPING.md exists and references both CWICR and Qdrant
#   20 pts — no forbidden strings in ddc/ source files
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
Usage: scripts/score-ddc.sh [--json]

Outputs the ddc/.github section fitness score (0-100) on stdout.
EOF
    exit 0 ;;
esac

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$REPO_ROOT"

# ---------- 1. Workflow cleanliness (no || true bypass) ---------------------
TOTAL_WORKFLOWS=$(find .github/workflows -maxdepth 1 -name '*.yml' 2>/dev/null | wc -l | tr -d ' ')
CLEAN_WORKFLOWS=0
DIRTY_WORKFLOWS=0
if [ "$TOTAL_WORKFLOWS" -gt 0 ]; then
  for f in .github/workflows/*.yml; do
    if grep -q '|| true' "$f" 2>/dev/null; then
      DIRTY_WORKFLOWS=$(( DIRTY_WORKFLOWS + 1 ))
    else
      CLEAN_WORKFLOWS=$(( CLEAN_WORKFLOWS + 1 ))
    fi
  done
fi

# ---------- 2. DDC_MAPPING.md with CWICR + Qdrant references ----------------
DDC_MAPPING_EXISTS=0
DDC_HAS_CWICR=0
DDC_HAS_QDRANT=0
if [ -f "meta/DDC_MAPPING.md" ]; then
  DDC_MAPPING_EXISTS=1
  grep -q 'CWICR' meta/DDC_MAPPING.md 2>/dev/null && DDC_HAS_CWICR=1
  grep -q 'Qdrant' meta/DDC_MAPPING.md 2>/dev/null && DDC_HAS_QDRANT=1
fi

# ---------- 3. Forbidden strings in ddc/ ------------------------------------
FORBIDDEN_HITS=0
if [ -d "ddc" ]; then
  for needle in 'pxt\.Geometry' 'pixeltable/service/migrations' '[Rr]evit' '[Mm]icro[Ss]tation' '@itwin/core-backend' 'SnapshotDb'; do
    HITS=$(grep -rE "$needle" ddc/ --include='*.py' --include='*.ts' --include='*.tsx' --include='*.json' --include='*.yml' 2>/dev/null \
      | grep -v -E '(GOAL\.md|MEMORY\.md|README\.md)' \
      | wc -l | tr -d ' ')
    FORBIDDEN_HITS=$(( FORBIDDEN_HITS + HITS ))
  done
fi

# ---------- 4. Compute score -------------------------------------------------
# 50 pts: workflow cleanliness (proportional: clean / total)
PTS_WORKFLOWS=0
if [ "$TOTAL_WORKFLOWS" -gt 0 ]; then
  PTS_WORKFLOWS=$(( 50 * CLEAN_WORKFLOWS / TOTAL_WORKFLOWS ))
fi

# 30 pts: DDC mapping doc quality
PTS_DDC=0
if [ "$DDC_MAPPING_EXISTS" -eq 1 ]; then
  PTS_DDC=$(( 10 + 10 * DDC_HAS_CWICR + 10 * DDC_HAS_QDRANT ))
fi

# 20 pts: no forbidden strings
if [ "$FORBIDDEN_HITS" -eq 0 ]; then
  PTS_FORBIDDEN=20
else
  PTS_FORBIDDEN=$(( 20 - FORBIDDEN_HITS * 5 ))
  [ "$PTS_FORBIDDEN" -lt 0 ] && PTS_FORBIDDEN=0
fi

SCORE=$(( PTS_WORKFLOWS + PTS_DDC + PTS_FORBIDDEN ))

# ---------- 5. Output -------------------------------------------------------
if [ "$JSON" -eq 1 ]; then
  cat <<EOF
{
  "section": "ddc",
  "score": $SCORE,
  "breakdown": {
    "workflow_cleanliness": {"points": $PTS_WORKFLOWS, "max": 50, "clean": $CLEAN_WORKFLOWS, "dirty": $DIRTY_WORKFLOWS, "total": $TOTAL_WORKFLOWS},
    "ddc_mapping_doc":      {"points": $PTS_DDC, "max": 30, "exists": $DDC_MAPPING_EXISTS, "has_cwicr": $DDC_HAS_CWICR, "has_qdrant": $DDC_HAS_QDRANT},
    "forbidden_strings":    {"points": $PTS_FORBIDDEN, "max": 20, "hits": $FORBIDDEN_HITS}
  }
}
EOF
else
  echo "score: $SCORE/100"
fi
exit 0
