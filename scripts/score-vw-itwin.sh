#!/usr/bin/env bash
# score-vw-itwin.sh — fitness score for the vw-plugin/ + vw-python/ + itwin/ sections.
#
# v1 formula:
#   40 pts — vw-plugin/CMakeLists.txt exists AND vw-plugin/src/MCPBridge.cpp exists
#   30 pts — itwin/bis-schemas/ directory exists with at least one schema file
#   30 pts — no Revit/MicroStation forbidden strings in vw-plugin/, vw-python/, itwin/ source
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
Usage: scripts/score-vw-itwin.sh [--json]

Outputs the vw-plugin/vw-python/itwin section fitness score (0-100) on stdout.
EOF
    exit 0 ;;
esac

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$REPO_ROOT"

# ---------- 1. vw-plugin build scaffolding ----------------------------------
CMAKE_EXISTS=0
MCPBRIDGE_EXISTS=0
[ -f "vw-plugin/CMakeLists.txt" ] && CMAKE_EXISTS=1
[ -f "vw-plugin/src/MCPBridge.cpp" ] && MCPBRIDGE_EXISTS=1

# ---------- 2. iTwin BIS schemas directory ----------------------------------
BIS_DIR_EXISTS=0
BIS_SCHEMA_COUNT=0
if [ -d "itwin/bis-schemas" ]; then
  BIS_DIR_EXISTS=1
  BIS_SCHEMA_COUNT=$(find itwin/bis-schemas -type f -not -name '.gitkeep' -not -name 'README.md' 2>/dev/null | wc -l | tr -d ' ')
fi

# ---------- 3. Forbidden strings in vw-plugin/, vw-python/, itwin/ ----------
FORBIDDEN_HITS=0
for needle in '[Rr]evit' '[Mm]icro[Ss]tation' '@itwin/core-backend' 'SnapshotDb' 'BriefcaseDb' 'IModelHost' 'pxt\.Geometry'; do
  for dir in vw-plugin vw-python itwin; do
    [ -d "$dir" ] || continue
    HITS=$(grep -rE "$needle" "$dir/" --include='*.py' --include='*.ts' --include='*.tsx' --include='*.cpp' --include='*.h' --include='*.cmake' 2>/dev/null \
      | grep -v -E '(README\.md|GOAL\.md|MEMORY\.md)' \
      | wc -l | tr -d ' ')
    FORBIDDEN_HITS=$(( FORBIDDEN_HITS + HITS ))
  done
done

# ---------- 4. Compute score -------------------------------------------------
# 40 pts: vw-plugin build scaffold
PTS_PLUGIN=0
if [ "$CMAKE_EXISTS" -eq 1 ] && [ "$MCPBRIDGE_EXISTS" -eq 1 ]; then
  PTS_PLUGIN=40
elif [ "$CMAKE_EXISTS" -eq 1 ] || [ "$MCPBRIDGE_EXISTS" -eq 1 ]; then
  PTS_PLUGIN=20
fi

# 30 pts: iTwin BIS schemas (directory + at least 1 non-placeholder file)
PTS_BIS=0
if [ "$BIS_DIR_EXISTS" -eq 1 ] && [ "$BIS_SCHEMA_COUNT" -gt 0 ]; then
  PTS_BIS=30
elif [ "$BIS_DIR_EXISTS" -eq 1 ]; then
  # Directory exists but empty scaffold — partial
  PTS_BIS=15
fi

# 30 pts: no forbidden strings
if [ "$FORBIDDEN_HITS" -eq 0 ]; then
  PTS_FORBIDDEN=30
else
  PTS_FORBIDDEN=$(( 30 - FORBIDDEN_HITS * 6 ))
  [ "$PTS_FORBIDDEN" -lt 0 ] && PTS_FORBIDDEN=0
fi

SCORE=$(( PTS_PLUGIN + PTS_BIS + PTS_FORBIDDEN ))

# ---------- 5. Output -------------------------------------------------------
if [ "$JSON" -eq 1 ]; then
  cat <<EOF
{
  "section": "vw-itwin",
  "score": $SCORE,
  "breakdown": {
    "plugin_scaffold": {"points": $PTS_PLUGIN, "max": 40, "cmake_exists": $CMAKE_EXISTS, "mcpbridge_exists": $MCPBRIDGE_EXISTS},
    "bis_schemas":     {"points": $PTS_BIS, "max": 30, "dir_exists": $BIS_DIR_EXISTS, "schema_count": $BIS_SCHEMA_COUNT},
    "forbidden_strings": {"points": $PTS_FORBIDDEN, "max": 30, "hits": $FORBIDDEN_HITS}
  }
}
EOF
else
  echo "score: $SCORE/100"
fi
exit 0
