#!/usr/bin/env bash
# score-georef.sh — fitness score for the georef/ + reality/ sections.
#
# v1 formula:
#   40 pts — converter implementation rate in georef/converters/
#            (heuristic: files > 1 KB are implemented, not stubs)
#   30 pts — project_georef schema present with 67-column declaration in meta/SCHEMA.md
#   30 pts — no forbidden strings in georef/ or reality/ source files
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
Usage: scripts/score-georef.sh [--json]

Outputs the georef/reality section fitness score (0-100) on stdout.
EOF
    exit 0 ;;
esac

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$REPO_ROOT"

# ---------- 1. Converter implementation rate --------------------------------
TOTAL_CONVERTERS=$(find georef/converters -maxdepth 1 -name '*.py' -not -name '__init__.py' 2>/dev/null | wc -l | tr -d ' ')
IMPLEMENTED_CONVERTERS=0
if [ "$TOTAL_CONVERTERS" -gt 0 ]; then
  for f in georef/converters/*.py; do
    [ "$(basename "$f")" = "__init__.py" ] && continue
    SIZE=$(wc -c < "$f" 2>/dev/null || echo 0)
    if [ "$SIZE" -gt 1024 ]; then
      IMPLEMENTED_CONVERTERS=$(( IMPLEMENTED_CONVERTERS + 1 ))
    fi
  done
fi

# ---------- 2. project_georef 67-column declaration in meta/SCHEMA.md -------
GEOREF_SCHEMA_OK=0
if grep -qE 'project_georef.*67' meta/SCHEMA.md 2>/dev/null; then
  GEOREF_SCHEMA_OK=1
fi

# ---------- 3. Forbidden strings in georef/ and reality/ --------------------
FORBIDDEN_HITS=0
for needle in 'pxt\.Geometry' 'pixeltable/service/migrations' '[Rr]evit' '[Mm]icro[Ss]tation' '@itwin/core-backend' 'SnapshotDb'; do
  HITS=$(grep -rE "$needle" georef/ reality/ --include='*.py' --include='*.ts' --include='*.tsx' --include='*.cpp' --include='*.h' 2>/dev/null \
    | grep -v -E '(GOAL\.md|MEMORY\.md|README\.md)' \
    | wc -l | tr -d ' ')
  FORBIDDEN_HITS=$(( FORBIDDEN_HITS + HITS ))
done

# ---------- 4. Compute score -------------------------------------------------
# 40 pts: converter implementation rate (proportional)
PTS_CONVERTERS=0
if [ "$TOTAL_CONVERTERS" -gt 0 ]; then
  PTS_CONVERTERS=$(( 40 * IMPLEMENTED_CONVERTERS / TOTAL_CONVERTERS ))
elif [ "$TOTAL_CONVERTERS" -eq 0 ]; then
  PTS_CONVERTERS=0
fi

# 30 pts: schema declaration
if [ "$GEOREF_SCHEMA_OK" -eq 1 ]; then
  PTS_SCHEMA=30
else
  PTS_SCHEMA=0
fi

# 30 pts: no forbidden strings
if [ "$FORBIDDEN_HITS" -eq 0 ]; then
  PTS_FORBIDDEN=30
else
  PTS_FORBIDDEN=$(( 30 - FORBIDDEN_HITS * 6 ))
  [ "$PTS_FORBIDDEN" -lt 0 ] && PTS_FORBIDDEN=0
fi

SCORE=$(( PTS_CONVERTERS + PTS_SCHEMA + PTS_FORBIDDEN ))

# ---------- 5. Output -------------------------------------------------------
if [ "$JSON" -eq 1 ]; then
  cat <<EOF
{
  "section": "georef",
  "score": $SCORE,
  "breakdown": {
    "converter_implementation": {"points": $PTS_CONVERTERS, "max": 40, "implemented": $IMPLEMENTED_CONVERTERS, "total": $TOTAL_CONVERTERS},
    "project_georef_schema":    {"points": $PTS_SCHEMA, "max": 30, "schema_ok": $GEOREF_SCHEMA_OK},
    "forbidden_strings":        {"points": $PTS_FORBIDDEN, "max": 30, "hits": $FORBIDDEN_HITS}
  }
}
EOF
else
  echo "score: $SCORE/100"
fi
exit 0
