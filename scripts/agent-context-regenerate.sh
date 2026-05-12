#!/usr/bin/env bash
# Idempotent regeneration of .github/agent-context.md from repo state.
# Run after any doctrine change (cardinal rules, locked stack, copilot-instructions).
# Safe to re-run: output is deterministic for the same input state.
#
# Usage: bash scripts/agent-context-regenerate.sh [--dry-run]
#
# Dry-run prints the would-be output without writing the file.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
OUTPUT="$REPO_ROOT/.github/agent-context.md"
COPILOT_INSTRUCTIONS="$REPO_ROOT/.github/copilot-instructions.md"
AGENT_ONBOARDING="$REPO_ROOT/meta/AGENT_ONBOARDING.md"
AGENTS_MD="$REPO_ROOT/AGENTS.md"
SYNC_CONTRACT="$REPO_ROOT/meta/sync-contract.md"
AGENT_LANES="$REPO_ROOT/meta/agent-lanes.md"

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
fi

# Verify required sources exist
for f in "$COPILOT_INSTRUCTIONS" "$AGENT_ONBOARDING" "$AGENTS_MD"; do
  if [[ ! -f "$f" ]]; then
    echo "ERROR: required source not found: $f" >&2
    exit 1
  fi
done

GENERATED_AT=$(date -u '+%Y-%m-%d (UTC)')
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
HEAD_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

# Extract locked stack table from copilot-instructions.md
# Assumes the table starts after "## Locked Stack" and ends before the next ##
LOCKED_STACK=$(awk '/^## Locked Stack/{found=1; next} found && /^## /{exit} found{print}' \
  "$COPILOT_INSTRUCTIONS" | sed '/^[[:space:]]*$/d')

# Extract cardinal rules section from copilot-instructions.md
CARDINAL_RULES=$(awk '/^## Cardinal Rules|^## CARDINAL RULES/{found=1; next} found && /^## /{exit} found{print}' \
  "$COPILOT_INSTRUCTIONS" | head -80)

# If copilot-instructions doesn't have these sections, fall back to agent-context sections
if [[ -z "$LOCKED_STACK" ]]; then
  LOCKED_STACK=$(awk '/^## Locked Stack/{found=1; next} found && /^## /{exit} found{print}' \
    "$OUTPUT" 2>/dev/null | sed '/^[[:space:]]*$/d' || echo "_Source not found — regenerate after Phase D docs site_")
fi

if [[ -z "$CARDINAL_RULES" ]]; then
  CARDINAL_RULES=$(awk '/^## Cardinal Rules/{found=1; next} found && /^## /{exit} found{print}' \
    "$OUTPUT" 2>/dev/null | head -80 || echo "_Source not found — regenerate after Phase D docs site_")
fi

# Build sync contract summary (team section only)
TEAM_SUMMARY=$(awk '/^## Teams/{found=1; next} found && /^---/{exit} found{print}' \
  "$SYNC_CONTRACT" 2>/dev/null | sed '/^[[:space:]]*$/d' || echo "_sync-contract.md not found_")

# Build agent lane summary (lane table only)
LANE_TABLE=$(awk '/^## Lane table/{found=1; next} found && /^---/{exit} found{print}' \
  "$AGENT_LANES" 2>/dev/null | sed '/^[[:space:]]*$/d' || echo "_agent-lanes.md not found_")

CONTENT="## LATTICE Agent Context (v1, static)

Generated: $GENERATED_AT
Branch: \`$BRANCH\` @ \`$HEAD_SHA\`
Source of truth: \`meta/harness/docs/\` on \`feature/meta-harness\`
Sourced from: \`.github/copilot-instructions.md\` (locked stack + cardinal rules),
  \`meta/sync-contract.md\` (teams + field directions),
  \`meta/agent-lanes.md\` (lane assignments)
Regeneration: \`bash scripts/agent-context-regenerate.sh\`

This file is a flat, generated-once context export for downstream agents
(Copilot, Cursor, Codex CLI, etc.) that cannot or should not traverse the full
\`meta/harness/\` tree. It is NOT a replacement for \`CLAUDE.md\` or \`AGENTS.md\`
— it is a snapshot of the rules in effect at generation time.

## Locked Stack

$LOCKED_STACK

## Cardinal Rules (1–23)

$CARDINAL_RULES

## Teams (Linear ↔ GitHub)

$TEAM_SUMMARY

## Agent Lane Assignments

$LANE_TABLE

## Key Doctrine References

- Sync contract (field directions, conflict policy, Magic Words): \`meta/sync-contract.md\`
- Agent lane definitions (scopes, branch prefixes, prohibited zones): \`meta/agent-lanes.md\`
- OSS self-hosted doctrine: \`.claude/rules/oss-self-hosted-doctrine.md\`
- Capability harvest protocol: \`.claude/rules/capability-harvest-protocol.md\`
- Zero Dead DNA: \`.claude/rules/zero-dead-dna.md\`
- Anti-amnesia rule: \`.claude/rules/anti-amnesia.md\`
- Pre-commit docs check (mandatory before every commit): \`bash scripts/pre-commit-docs-check.sh\`

## Phase B acknowledgement

Phase B M3 Max bootstrap has NOT run. The following Pixeltable query tools
return empty results until Phase B completes:
  \`search_tutorials\`, \`search_research\`, \`search_docs\`,
  \`search_api_reference\`, \`get_coverage_gaps\`

Do not write code that assumes these tools return data.

## Quick-start for new agents

1. Read \`CLAUDE.md\` (repo root) — mandatory schema and migration rules
2. Read \`meta/AGENT_ONBOARDING.md\` — 5-minute boot checklist
3. Read \`meta/agent-lanes.md\` — confirm your lane before touching files
4. Run \`curl -s http://localhost:8001/health\` — confirm FastAPI sidecar
5. Run \`bash scripts/pre-commit-docs-check.sh\` before every commit
"

if [[ "$DRY_RUN" == "true" ]]; then
  echo "--- DRY RUN: would write to $OUTPUT ---"
  echo "$CONTENT"
  echo "--- END DRY RUN ---"
  exit 0
fi

echo "$CONTENT" > "$OUTPUT"
echo "agent-context.md regenerated at $OUTPUT (branch=$BRANCH sha=$HEAD_SHA)"
