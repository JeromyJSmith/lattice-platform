#!/usr/bin/env bash
# run-autoresearch.sh — run one autoresearch cycle for a given section.
#
# Usage:
#   bash meta/harness/bootstrap/run-autoresearch.sh <section>
#   bash meta/harness/bootstrap/run-autoresearch.sh --dry <section>
#   bash meta/harness/bootstrap/run-autoresearch.sh --help
#
# Sections: schema | api | frontend | georef | genai | vw-itwin | ddc
#
# --dry  skips the llm router proposal call and emits a no-op diff so all
#        wiring (sandbox, scoring, ratchet gate) can be verified without
#        requiring claude availability.
#
# Exit codes:
#   0  cycle completed (accepted or cleanly rejected — not an error)
#   1  hard error (unknown section, flock busy, sandbox setup failed)

set -uo pipefail

# ---------- --help early exit ------------------------------------------------
if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
  cat <<EOF
Usage: bash meta/harness/bootstrap/run-autoresearch.sh [--dry] <section>

Run one autoresearch cycle for a section of the LATTICE platform.

Sections: schema | api | frontend | georef | genai | vw-itwin | ddc

Options:
  --dry    Skip the llm router proposal call. Emit a no-op diff that scores
           identically, verifying all harness wiring without AI involvement.
  --help   Show this message and exit.

The cycle:
  1. Acquire /tmp/harness-loop.lock (single-writer across all sections).
  2. Score the section before the proposal (score_before).
  3. Create a git worktree sandbox at /tmp/harness-sandbox.
  4. Call claude -p to generate a unified diff proposal (skipped with --dry).
  5. Apply and score the diff in the sandbox (score_after).
  6. Accept (git apply to working tree) only if score_after > score_before.
  7. Clean up sandbox and lock.

All steps emit events. In Wave 2 these will be written to lattice/harness/section_events via Pixeltable.
EOF
  exit 0
fi

# ---------- parse args -------------------------------------------------------
DRY=0
if [ "${1:-}" = "--dry" ]; then
  DRY=1
  shift
fi

SECTION="${1:-schema}"

# ---------- section -> scoring script map ------------------------------------
case "$SECTION" in
  schema)    SCORE_SCRIPT="scripts/score-schema.sh" ;;
  api)       SCORE_SCRIPT="scripts/score-api.sh" ;;
  frontend)  SCORE_SCRIPT="scripts/score-frontend.sh" ;;
  georef)    SCORE_SCRIPT="scripts/score-georef.sh" ;;
  genai)     SCORE_SCRIPT="scripts/score-genai.sh" ;;
  vw-itwin)  SCORE_SCRIPT="scripts/score-vw-itwin.sh" ;;
  ddc)       SCORE_SCRIPT="scripts/score-ddc.sh" ;;
  *)
    echo "ERROR: Unknown section: $SECTION" >&2
    echo "Valid sections: schema api frontend georef genai vw-itwin ddc" >&2
    exit 1
    ;;
esac

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -z "$REPO_ROOT" ]; then
  echo "ERROR: Not inside a git repository" >&2
  exit 1
fi
cd "$REPO_ROOT"

# ---------- single-writer lock (portable: mkdir is atomic on POSIX + macOS) --
LOCKDIR=/tmp/harness-loop.lockdir
if ! mkdir "$LOCKDIR" 2>/dev/null; then
  # Check if the owning PID is still alive; if not, steal the lock
  LOCK_PID=$(cat "$LOCKDIR/pid" 2>/dev/null || echo "")
  if [ -n "$LOCK_PID" ] && kill -0 "$LOCK_PID" 2>/dev/null; then
    echo "ERROR: Another autoresearch run is active (PID $LOCK_PID). Exiting." >&2
    exit 1
  else
    echo "[harness] Stale lock detected — stealing from PID ${LOCK_PID:-unknown}"
    rm -rf "$LOCKDIR"
    mkdir "$LOCKDIR" || { echo "ERROR: Could not acquire lock" >&2; exit 1; }
  fi
fi
echo $$ > "$LOCKDIR/pid"
# Release lock on exit (normal or error)
trap 'rm -rf "$LOCKDIR"' EXIT

echo "[harness] section=$SECTION dry=$DRY"

# ---------- pre-flight: clean stale sandbox ----------------------------------
SANDBOX=/tmp/harness-sandbox
git worktree remove --force "$SANDBOX" 2>/dev/null || true
rm -rf "$SANDBOX"

# ---------- check scoring script exists --------------------------------------
if [ ! -f "$SCORE_SCRIPT" ]; then
  echo "[harness] WARNING: $SCORE_SCRIPT not found — scoring unavailable for section=$SECTION"
  echo "[harness] Emitting event_type=ratchet.error and halting."
  # Wave 2: insert row into lattice/harness/section_events here
  exit 0  # Non-fatal for harness — section script will be added later
fi

# ---------- 1. score_before --------------------------------------------------
SCORE_BEFORE=$(bash "$SCORE_SCRIPT" 2>/dev/null | grep -oE '[0-9]+' | head -1 || echo 0)
echo "[harness] score_before=$SCORE_BEFORE"

# ---------- 2. create sandbox worktree ---------------------------------------
# Use detached HEAD at HEAD commit so we can add a worktree even when the
# current worktree already holds the branch (which is always the case here).
HEAD_SHA=$(git rev-parse HEAD)
if ! git worktree add --detach "$SANDBOX" "$HEAD_SHA" 2>&1 | tail -3; then
  echo "[harness] ERROR: Failed to create sandbox worktree at $SANDBOX" >&2
  exit 1
fi

# ---------- 3. generate proposal ---------------------------------------------
PROPOSAL_FILE=$(mktemp /tmp/harness-proposal-XXXXXX.diff)

if [ "$DRY" -eq 1 ]; then
  echo "[harness] --dry mode: emitting no-op proposal (empty diff)"
  # A syntactically valid but empty unified diff — applies cleanly, changes nothing
  printf "" > "$PROPOSAL_FILE"
else
  PROPOSAL_PROMPT="Read ${SECTION}/GOAL.md if it exists, else read pixeltable/GOAL.md. Read scripts/score-${SECTION}.sh. Propose ONE concrete change to the ${SECTION} section that would increase the fitness score. Output ONLY a unified diff applicable from the repo root. No explanation, no markdown fences, just the diff."

  # Route through the model router. Backend is decided by config:
  #   meta/harness/config/models.json — task `propose`
  # Override with HARNESS_BACKEND env var if you want to pin one explicitly.
  LLM=meta/harness/bin/llm
  echo "[harness] Calling model router (task=propose, timeout=120s)..."
  if [ -n "${HARNESS_BACKEND:-}" ]; then
    LLM_ARGS=(--backend="$HARNESS_BACKEND" --timeout=120)
  else
    LLM_ARGS=(--task=propose --timeout=120)
  fi
  if ! "$LLM" "${LLM_ARGS[@]}" "$PROPOSAL_PROMPT" > "$PROPOSAL_FILE" 2>&1; then
    echo "[harness] llm router failed across all fallbacks — no proposal this cycle"
    # Wave 2: log event_type=rejected with error_log='all-backends-failed' to section_events
    rm -f "$PROPOSAL_FILE"
    git worktree remove --force "$SANDBOX" 2>/dev/null || true
    exit 0  # Harness stays healthy — just no progress this cycle
  fi
fi

# Reject clearly empty proposals early (no diff lines at all)
DIFF_LINES=$(grep -cE '^\+\+\+|^---' "$PROPOSAL_FILE" 2>/dev/null || echo 0)
if [ "$DRY" -eq 0 ] && [ "$DIFF_LINES" -eq 0 ]; then
  echo "[harness] Proposal is empty or contains no diff headers — rejected"
  rm -f "$PROPOSAL_FILE"
  git worktree remove --force "$SANDBOX" 2>/dev/null || true
  exit 0
fi

# ---------- 4. apply proposal in sandbox -------------------------------------
cd "$SANDBOX"

if [ -s "$PROPOSAL_FILE" ]; then
  if ! git apply --check < "$PROPOSAL_FILE" 2>/dev/null; then
    echo "[harness] Proposal does not apply cleanly — rejected (apply check failed)"
    cd "$REPO_ROOT"
    git worktree remove --force "$SANDBOX" 2>/dev/null || true
    rm -f "$PROPOSAL_FILE"
    exit 0
  fi
  git apply < "$PROPOSAL_FILE"
  echo "[harness] Proposal applied in sandbox"
else
  echo "[harness] Empty/no-op proposal applied in sandbox (no changes)"
fi

# ---------- 5. score in sandbox ----------------------------------------------
SCORE_AFTER=$(bash "$REPO_ROOT/$SCORE_SCRIPT" 2>/dev/null | grep -oE '[0-9]+' | head -1 || echo 0)
echo "[harness] score_after=$SCORE_AFTER"

# ---------- 6. ratchet gate --------------------------------------------------
cd "$REPO_ROOT"

if [ "$SCORE_AFTER" -gt "$SCORE_BEFORE" ]; then
  echo "[harness] ACCEPTED — score improved ($SCORE_BEFORE -> $SCORE_AFTER)"
  if [ -s "$PROPOSAL_FILE" ]; then
    git apply < "$PROPOSAL_FILE"
    echo "[harness] Proposal applied to working tree"
  fi
  # Wave 2: log event_type=accepted to section_events + harness_proposals
else
  echo "[harness] REJECTED — score did not improve ($SCORE_BEFORE -> $SCORE_AFTER)"
  # Wave 2: log event_type=rejected to section_events + harness_proposals
fi

# ---------- cleanup ----------------------------------------------------------
git worktree remove --force "$SANDBOX" 2>/dev/null || true
rm -f "$PROPOSAL_FILE"

echo "[harness] Cycle complete. section=$SECTION score_before=$SCORE_BEFORE score_after=$SCORE_AFTER"
exit 0
