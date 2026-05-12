#!/usr/bin/env bash
# Post a comment to Linear when a new commit references a LAT-XX or MAR-XX issue.
#
# Called by .claude/settings.json PostToolUse hook after every Bash tool call.
# Detects new commits by comparing HEAD SHA to a cached value in /tmp.
# Idempotent: skips if HEAD hasn't changed since last run.
#
# Requires: LINEAR_API_KEY in environment (lin_api_…)
# Optional: LATTICE_REPO_SLUG (default: JeromyJSmith/lattice-platform)

set -euo pipefail

REPO_SLUG="${LATTICE_REPO_SLUG:-JeromyJSmith/lattice-platform}"
CACHE_FILE="/tmp/lattice-linear-last-sha"

# Silently exit if not inside a git repo
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
CURRENT_SHA=$(git -C "$REPO_ROOT" rev-parse HEAD 2>/dev/null) || exit 0

# Exit if SHA hasn't changed (no new commit)
LAST_SHA=$(cat "$CACHE_FILE" 2>/dev/null || echo "")
if [[ "$CURRENT_SHA" == "$LAST_SHA" ]]; then
  exit 0
fi

# Update cache immediately to prevent duplicate runs
echo "$CURRENT_SHA" > "$CACHE_FILE"

# Exit if no API key configured
[[ -z "${LINEAR_API_KEY:-}" ]] && exit 0

# Get commit metadata
SHORT_SHA=$(git -C "$REPO_ROOT" rev-parse --short HEAD 2>/dev/null) || exit 0
COMMIT_SUBJECT=$(git -C "$REPO_ROOT" log -1 --format="%s" 2>/dev/null) || exit 0
COMMIT_BODY=$(git -C "$REPO_ROOT" log -1 --format="%b" 2>/dev/null) || true
COMMIT_AUTHOR=$(git -C "$REPO_ROOT" log -1 --format="%an" 2>/dev/null) || exit 0
COMMIT_URL="https://github.com/${REPO_SLUG}/commit/${CURRENT_SHA}"

# Extract MARPA-XX, LAT-XX, and MAR-XX identifiers from subject + body
# Note: MARPA-XX is the active prefix (free-plan; see meta/sync-contract.md §Teams)
FULL_MESSAGE="$COMMIT_SUBJECT
$COMMIT_BODY"
LINEAR_IDS=$(echo "$FULL_MESSAGE" | grep -oE '(MARPA|LAT|MAR)-[0-9]+' | sort -u) || true

[[ -z "$LINEAR_IDS" ]] && exit 0

COMMENT_BODY="Commit \`${SHORT_SHA}\` by ${COMMIT_AUTHOR}:

> ${COMMIT_SUBJECT}

[View on GitHub](${COMMIT_URL})

_Posted automatically by \`scripts/linear-notify-commit.sh\` via Claude Code hook._"

# For each referenced Linear issue, look up its UUID and post a comment
for LINEAR_ID in $LINEAR_IDS; do
  TEAM_KEY=$(echo "$LINEAR_ID" | cut -d- -f1)
  ISSUE_NUM=$(echo "$LINEAR_ID" | cut -d- -f2)

  # Look up issue UUID by team key + number
  LOOKUP_QUERY=$(cat <<GRAPHQL
{
  "query": "{ issues(filter: { team: { key: { eq: \"${TEAM_KEY}\" } }, number: { eq: ${ISSUE_NUM} } }) { nodes { id identifier } } }"
}
GRAPHQL
)

  RESP=$(curl -sS -X POST "https://api.linear.app/graphql" \
    -H "Authorization: ${LINEAR_API_KEY}" \
    -H "Content-Type: application/json" \
    --data-raw "$LOOKUP_QUERY" 2>/dev/null) || continue

  ISSUE_UUID=$(echo "$RESP" | python3 -c "
import sys, json
try:
    nodes = json.load(sys.stdin)['data']['issues']['nodes']
    print(nodes[0]['id'] if nodes else '')
except Exception:
    print('')
" 2>/dev/null) || continue

  [[ -z "$ISSUE_UUID" ]] && continue

  # Escape the comment body for JSON
  ESCAPED_BODY=$(echo "$COMMENT_BODY" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read()))")

  MUTATION=$(cat <<GRAPHQL
{
  "query": "mutation { commentCreate(input: { issueId: \"${ISSUE_UUID}\", body: ${ESCAPED_BODY} }) { success } }"
}
GRAPHQL
)

  curl -sS -X POST "https://api.linear.app/graphql" \
    -H "Authorization: ${LINEAR_API_KEY}" \
    -H "Content-Type: application/json" \
    --data-raw "$MUTATION" > /dev/null 2>&1 || true

  echo "linear-notify: posted commit ${SHORT_SHA} to ${LINEAR_ID}" >&2
done
