#!/usr/bin/env bash
# score-global.sh — LATTICE Meta-Harness aggregate fitness score.
#
# Calls all 7 section scoring scripts with --json, parses each `"score": N`,
# and emits an average score plus per-section breakdown.
#
# Output: `score: N/100` on stdout, exit 0.
# With --json: emits combined JSON with all section breakdowns.
#
# Budget: < 60s (sum of all section script runtimes, each < 10s).

set -uo pipefail

JSON=0
case "${1:-}" in
  --json) JSON=1 ;;
  --help|-h)
    cat <<EOF
Usage: scripts/score-global.sh [--json]

Runs all 7 LATTICE section scoring scripts and outputs an aggregate score.
Sections: schema, api, frontend, georef, genai, vw-itwin, ddc
EOF
    exit 0 ;;
esac

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$REPO_ROOT"

SCRIPTS_DIR="$REPO_ROOT/scripts"

# ---------- 1. Run each section script with --json --------------------------
run_section() {
  local script="$1"
  local label="$2"
  if [ -x "$SCRIPTS_DIR/$script" ]; then
    "$SCRIPTS_DIR/$script" --json 2>/dev/null || echo '{"section":"'"$label"'","score":0,"error":"script_failed"}'
  else
    echo '{"section":"'"$label"'","score":0,"error":"script_not_found"}'
  fi
}

SCHEMA_JSON=$(run_section "score-schema.sh"  "schema")
API_JSON=$(run_section    "score-api.sh"     "api")
FE_JSON=$(run_section     "score-frontend.sh" "frontend")
GEOREF_JSON=$(run_section "score-georef.sh"  "georef")
GENAI_JSON=$(run_section  "score-genai.sh"   "genai")
VWITWIN_JSON=$(run_section "score-vw-itwin.sh" "vw-itwin")
DDC_JSON=$(run_section    "score-ddc.sh"     "ddc")

# ---------- 2. Parse scores from JSON (portable: no jq dependency) ----------
parse_score() {
  # Extract the first "score": N from JSON output
  echo "$1" | grep -oE '"score"[[:space:]]*:[[:space:]]*[0-9]+' | head -1 | grep -oE '[0-9]+' || echo 0
}

SCORE_SCHEMA=$(parse_score "$SCHEMA_JSON")
SCORE_API=$(parse_score    "$API_JSON")
SCORE_FE=$(parse_score     "$FE_JSON")
SCORE_GEOREF=$(parse_score "$GEOREF_JSON")
SCORE_GENAI=$(parse_score  "$GENAI_JSON")
SCORE_VWITWIN=$(parse_score "$VWITWIN_JSON")
SCORE_DDC=$(parse_score    "$DDC_JSON")

# ---------- 3. Aggregate (integer average across 7 sections) ----------------
TOTAL=$(( SCORE_SCHEMA + SCORE_API + SCORE_FE + SCORE_GEOREF + SCORE_GENAI + SCORE_VWITWIN + SCORE_DDC ))
AGGREGATE=$(( TOTAL / 7 ))

# ---------- 4. Output -------------------------------------------------------
if [ "$JSON" -eq 1 ]; then
  cat <<EOF
{
  "aggregate_score": $AGGREGATE,
  "section_count": 7,
  "total_points": $TOTAL,
  "sections": {
    "schema":   $SCORE_SCHEMA,
    "api":      $SCORE_API,
    "frontend": $SCORE_FE,
    "georef":   $SCORE_GEOREF,
    "genai":    $SCORE_GENAI,
    "vw-itwin": $SCORE_VWITWIN,
    "ddc":      $SCORE_DDC
  },
  "section_details": {
    "schema":   $SCHEMA_JSON,
    "api":      $API_JSON,
    "frontend": $FE_JSON,
    "georef":   $GEOREF_JSON,
    "genai":    $GENAI_JSON,
    "vw-itwin": $VWITWIN_JSON,
    "ddc":      $DDC_JSON
  }
}
EOF
else
  echo "score: $AGGREGATE/100"
  echo ""
  echo "Section breakdown:"
  printf "  %-12s %3d/100\n" "schema"   "$SCORE_SCHEMA"
  printf "  %-12s %3d/100\n" "api"      "$SCORE_API"
  printf "  %-12s %3d/100\n" "frontend" "$SCORE_FE"
  printf "  %-12s %3d/100\n" "georef"   "$SCORE_GEOREF"
  printf "  %-12s %3d/100\n" "genai"    "$SCORE_GENAI"
  printf "  %-12s %3d/100\n" "vw-itwin" "$SCORE_VWITWIN"
  printf "  %-12s %3d/100\n" "ddc"      "$SCORE_DDC"
fi
exit 0
