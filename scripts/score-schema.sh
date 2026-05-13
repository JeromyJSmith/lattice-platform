#!/usr/bin/env bash
# score-schema.sh — fitness score for the pixeltable/ (schema) section.
#
# v1 formula:
#   50 pts — table count declared in meta/SCHEMA.md matches actual table count
#            (computed by counting ensure_table() calls in pixeltable/migrations/00*.py).
#   30 pts — migration trail header in meta/SCHEMA.md matches latest migration.
#   20 pts — no forbidden strings in pixeltable/ source tree
#            (pxt.Geometry, pixeltable/service/migrations, Revit, etc.)
#            with allowlist mirroring docs-sync-check.yml.
#
# Output: `score: N/100` on stdout, exit 0.
# With --json: emits a JSON breakdown to stdout instead.
#
# Budget: < 10s on a warm `uv` env.

set -uo pipefail

JSON=0
case "${1:-}" in
  --json) JSON=1 ;;
  --help|-h)
    cat <<EOF
Usage: scripts/score-schema.sh [--json]

Outputs the schema section fitness score (0-100) on stdout.
EOF
    exit 0 ;;
esac

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$REPO_ROOT"

# ---------- 1. Migration count + last-migration number ----------------------
ACTUAL_COUNT=$(find pixeltable/migrations -maxdepth 1 -name '0*.py' -not -name '__init__.py' 2>/dev/null | wc -l | tr -d ' ')
LAST_NUM=$(printf "%04d" "$ACTUAL_COUNT")

# ---------- 2. Tables declared in meta/SCHEMA.md ----------------------------
DECLARED_TABLES=$(grep -oE '\*\*[0-9]+ tables?\*\*' meta/SCHEMA.md 2>/dev/null | head -1 | grep -oE '[0-9]+' || echo 0)

# ---------- 3. Actual table count via ensure_table() calls ------------------
ACTUAL_TABLES=$(grep -hE 'ensure_table\s*\(' pixeltable/migrations/00*.py 2>/dev/null | wc -l | tr -d ' ')

# ---------- 4. Migration trail in meta/SCHEMA.md ----------------------------
if grep -qE "Migration trail.*0001[–-]${LAST_NUM}" meta/SCHEMA.md 2>/dev/null; then
  TRAIL_OK=1
else
  TRAIL_OK=0
fi

# ---------- 5. Forbidden strings in pixeltable/ -----------------------------
# Allowlist mirrors docs-sync-check.yml: GOAL.md / MEMORY.md may reference
# forbidden patterns as guardrail text.
FORBIDDEN_HITS=0
for needle in 'pxt\.Geometry' 'pixeltable/service/migrations' '[Rr]evit' '[Mm]icro[Ss]tation' '@itwin/core-backend' 'SnapshotDb'; do
  HITS=$(grep -rE "$needle" pixeltable/ --include='*.py' --include='*.ts' --include='*.tsx' 2>/dev/null \
    | grep -v -E '(GOAL\.md|MEMORY\.md|^pixeltable/\.)' \
    | wc -l | tr -d ' ')
  FORBIDDEN_HITS=$(( FORBIDDEN_HITS + HITS ))
done

# ---------- 6. Compute score ------------------------------------------------
PTS_TABLES=0
if [ "$DECLARED_TABLES" -gt 0 ] && [ "$DECLARED_TABLES" = "$ACTUAL_TABLES" ]; then
  PTS_TABLES=50
elif [ "$DECLARED_TABLES" -gt 0 ] && [ "$ACTUAL_TABLES" -gt 0 ]; then
  if [ "$DECLARED_TABLES" -gt "$ACTUAL_TABLES" ]; then
    DIFF=$(( DECLARED_TABLES - ACTUAL_TABLES ))
  else
    DIFF=$(( ACTUAL_TABLES - DECLARED_TABLES ))
  fi
  PTS_TABLES=$(( 50 - DIFF * 5 ))
  [ "$PTS_TABLES" -lt 0 ] && PTS_TABLES=0
fi

if [ "$TRAIL_OK" -eq 1 ]; then
  PTS_TRAIL=30
else
  PTS_TRAIL=0
fi

if [ "$FORBIDDEN_HITS" -eq 0 ]; then
  PTS_FORBIDDEN=20
else
  PTS_FORBIDDEN=$(( 20 - FORBIDDEN_HITS * 4 ))
  [ "$PTS_FORBIDDEN" -lt 0 ] && PTS_FORBIDDEN=0
fi

SCORE=$(( PTS_TABLES + PTS_TRAIL + PTS_FORBIDDEN ))

# ---------- 7. Output -------------------------------------------------------
if [ "$JSON" -eq 1 ]; then
  cat <<EOF
{
  "section": "schema",
  "score": $SCORE,
  "breakdown": {
    "table_count_match": {"points": $PTS_TABLES, "max": 50, "declared": $DECLARED_TABLES, "actual": $ACTUAL_TABLES},
    "migration_trail":   {"points": $PTS_TRAIL, "max": 30, "last_migration": "$LAST_NUM", "trail_ok": $TRAIL_OK},
    "forbidden_strings": {"points": $PTS_FORBIDDEN, "max": 20, "hits": $FORBIDDEN_HITS}
  },
  "migration_count": $ACTUAL_COUNT
}
EOF
else
  echo "score: $SCORE/100"
fi
exit 0
