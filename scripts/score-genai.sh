#!/usr/bin/env bash
# score-genai.sh — fitness score for the genai/ + assets/ sections.
#
# v1 formula:
#   50 pts — assets/plants/lod-*/ directories exist and contain non-placeholder files
#            (Phase 3: lod-100/ and lod-300/ scaffolded but empty = partial credit)
#   30 pts — ComfyUI workflow JSON file count under genai/comfyui/
#   20 pts — no forbidden strings in genai/ or assets/ source
#
# NOTE: This section is Phase 3. Low scores are expected and not regressions.
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
Usage: scripts/score-genai.sh [--json]

Outputs the genai/assets section fitness score (0-100) on stdout.
Note: Phase 3 section — low baseline score is expected.
EOF
    exit 0 ;;
esac

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$REPO_ROOT"

# ---------- 1. LOD directory presence and population ------------------------
LOD_DIRS_EXIST=0
LOD_POPULATED=0
LOD_MANIFEST_COUNT=0

for lod_dir in assets/plants/lod-100 assets/plants/lod-300; do
  if [ -d "$lod_dir" ]; then
    LOD_DIRS_EXIST=$(( LOD_DIRS_EXIST + 1 ))
    # Count non-placeholder files (not .gitkeep)
    REAL_FILES=$(find "$lod_dir" -type f -not -name '.gitkeep' 2>/dev/null | wc -l | tr -d ' ')
    if [ "$REAL_FILES" -gt 0 ]; then
      LOD_POPULATED=$(( LOD_POPULATED + 1 ))
    fi
    # Count manifest-style json files
    JSON_FILES=$(find "$lod_dir" -name '*.json' -o -name 'manifest*' 2>/dev/null | wc -l | tr -d ' ')
    LOD_MANIFEST_COUNT=$(( LOD_MANIFEST_COUNT + JSON_FILES ))
  fi
done

# ---------- 2. ComfyUI workflow JSON count ----------------------------------
COMFYUI_JSON_COUNT=$(find genai/comfyui -name '*.json' 2>/dev/null | wc -l | tr -d ' ')

# ---------- 3. Forbidden strings in genai/ and assets/ ----------------------
FORBIDDEN_HITS=0
for needle in 'pxt\.Geometry' 'pixeltable/service/migrations' '[Rr]evit' '[Mm]icro[Ss]tation' '@itwin/core-backend' 'SnapshotDb'; do
  HITS=$(grep -rE "$needle" genai/ assets/ --include='*.py' --include='*.ts' --include='*.tsx' --include='*.json' 2>/dev/null \
    | grep -v -E '(GOAL\.md|MEMORY\.md|README\.md)' \
    | wc -l | tr -d ' ')
  FORBIDDEN_HITS=$(( FORBIDDEN_HITS + HITS ))
done

# ---------- 4. Compute score -------------------------------------------------
# 50 pts: LOD directory scaffold + population
# lod dirs exist but empty = 20 pts (scaffold in place)
# lod dirs exist and populated = 50 pts
# no lod dirs = 0 pts
PTS_LOD=0
if [ "$LOD_DIRS_EXIST" -ge 2 ]; then
  if [ "$LOD_POPULATED" -ge 1 ]; then
    # Partial proportional for population
    PTS_LOD=$(( 20 + 30 * LOD_POPULATED / 2 ))
  else
    # Scaffold exists but Phase 3 content not yet landed — expected
    PTS_LOD=20
  fi
fi

# 30 pts: ComfyUI workflow JSONs (proportional up to 5 = full marks)
PTS_COMFYUI=0
if [ "$COMFYUI_JSON_COUNT" -ge 5 ]; then
  PTS_COMFYUI=30
elif [ "$COMFYUI_JSON_COUNT" -gt 0 ]; then
  PTS_COMFYUI=$(( 30 * COMFYUI_JSON_COUNT / 5 ))
fi

# 20 pts: no forbidden strings
if [ "$FORBIDDEN_HITS" -eq 0 ]; then
  PTS_FORBIDDEN=20
else
  PTS_FORBIDDEN=$(( 20 - FORBIDDEN_HITS * 5 ))
  [ "$PTS_FORBIDDEN" -lt 0 ] && PTS_FORBIDDEN=0
fi

SCORE=$(( PTS_LOD + PTS_COMFYUI + PTS_FORBIDDEN ))

# ---------- 5. Output -------------------------------------------------------
if [ "$JSON" -eq 1 ]; then
  cat <<EOF
{
  "section": "genai",
  "score": $SCORE,
  "phase": 3,
  "note": "Phase 3 section — low baseline score is expected",
  "breakdown": {
    "lod_assets": {"points": $PTS_LOD, "max": 50, "lod_dirs_exist": $LOD_DIRS_EXIST, "lod_populated": $LOD_POPULATED, "manifest_count": $LOD_MANIFEST_COUNT},
    "comfyui_workflows": {"points": $PTS_COMFYUI, "max": 30, "json_count": $COMFYUI_JSON_COUNT},
    "forbidden_strings": {"points": $PTS_FORBIDDEN, "max": 20, "hits": $FORBIDDEN_HITS}
  }
}
EOF
else
  echo "score: $SCORE/100"
fi
exit 0
