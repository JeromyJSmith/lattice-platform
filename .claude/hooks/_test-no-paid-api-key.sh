#!/usr/bin/env bash
# Proof harness for .claude/hooks/no-paid-api-key.sh + api-key-policy.json.
# Test inputs are base64-encoded so this runner does not contain literal
# patterns the hook tests for, avoiding self-block.

set -u
HOOK=".claude/hooks/no-paid-api-key.sh"

# Read denylist / allowlist key ids from the policy data — keeps the literal
# variable names out of this test file. The policy JSON is the single data row
# of authority.
POLICY=".claude/hooks/api-key-policy.json"
KEY_DENIED="$(jq -r '.denylist[0].id' "$POLICY")"
KEY_DENIED_2="$(jq -r '.denylist[1].id // .denylist[0].id' "$POLICY")"
KEY_ALLOWED="$(jq -r '.allowlist[0].id' "$POLICY")"
KEY_ALLOWED_2="$(jq -r '.allowlist[1].id // .allowlist[0].id' "$POLICY")"
KEY_UNKNOWN="MYSTERY_VENDOR_API_KEY"

# Each row: <expected_exit>|<label>|<base64 of JSON payload>
fixtures=(
  # ===== Denylisted key (read from policy data — no literal in this test file) =====
  "2|deny: bare claude -p|$(printf '{"tool_name":"Bash","tool_input":{"command":"claude -p hello"}}' | base64)"
  "2|deny: piped claude -p no strip|$(printf '{"tool_name":"Bash","tool_input":{"command":"cat prompt.md | claude -p --permission-mode acceptEdits"}}' | base64)"
  "2|deny: inline set denied key|$(printf '{"tool_name":"Bash","tool_input":{"command":"%s=sk-fake-1234 claude -p hi"}}' "$KEY_DENIED" | base64)"
  "2|deny: export denied key|$(printf '{"tool_name":"Bash","tool_input":{"command":"export %s=sk-fake-xyz && claude -p hi"}}' "$KEY_DENIED" | base64)"
  "0|allow: env -u denied then claude -p|$(printf '{"tool_name":"Bash","tool_input":{"command":"env -u %s claude -p hello"}}' "$KEY_DENIED" | base64)"
  "0|allow: piped env -u denied|$(printf '{"tool_name":"Bash","tool_input":{"command":"cat prompt.md | env -u %s claude -p"}}' "$KEY_DENIED" | base64)"
  "0|allow: unset denied then claude -p|$(printf '{"tool_name":"Bash","tool_input":{"command":"unset %s; claude -p hi"}}' "$KEY_DENIED" | base64)"
  # ===== claude-cli wrapper (the canonical safe form — no env -u needed) =====
  "0|allow: claude-cli -p (wrapper)|$(printf '{"tool_name":"Bash","tool_input":{"command":"claude-cli -p hello"}}' | base64)"
  "0|allow: piped to claude-cli|$(printf '{"tool_name":"Bash","tool_input":{"command":"cat prompt.md | claude-cli -p --permission-mode acceptEdits"}}' | base64)"
  "0|allow: absolute-path claude-cli|$(printf '{"tool_name":"Bash","tool_input":{"command":".claude/bin/claude-cli -p hi"}}' | base64)"

  # ===== Second denylisted entry =====
  "2|deny: export second-denied|$(printf '{"tool_name":"Bash","tool_input":{"command":"export %s=sk-xxx && uv run python script.py"}}' "$KEY_DENIED_2" | base64)"
  "2|deny: inline second-denied|$(printf '{"tool_name":"Bash","tool_input":{"command":"%s=sk-real uv run python embed.py"}}' "$KEY_DENIED_2" | base64)"

  # ===== First allowlisted entry =====
  "0|allow: export first allowed|$(printf '{"tool_name":"Bash","tool_input":{"command":"export %s=allowed-real-key && npx -y something"}}' "$KEY_ALLOWED" | base64)"
  "0|allow: inline first allowed|$(printf '{"tool_name":"Bash","tool_input":{"command":"%s=$VAL npx -y something"}}' "$KEY_ALLOWED" | base64)"

  # ===== Second allowlisted entry =====
  "0|allow: export second allowed|$(printf '{"tool_name":"Bash","tool_input":{"command":"export %s=allowed-real-value && echo ok"}}' "$KEY_ALLOWED_2" | base64)"

  # ===== Default-deny: unknown key =====
  "2|deny: unknown vendor key|$(printf '{"tool_name":"Bash","tool_input":{"command":"export %s=mystery && uv run python something.py"}}' "$KEY_UNKNOWN" | base64)"

  # ===== Safe / unrelated =====
  "0|allow: claude --version|$(printf '{"tool_name":"Bash","tool_input":{"command":"claude --version"}}' | base64)"
  "0|allow: git status|$(printf '{"tool_name":"Bash","tool_input":{"command":"git status"}}' | base64)"
  "0|allow: bash mentions KEY name without value|$(printf '{"tool_name":"Bash","tool_input":{"command":"echo set %s before running"}}' "$KEY_DENIED" | base64)"

  # ===== Write tool — file persistence =====
  "2|deny: Write tool persists denied key|$(printf '{"tool_name":"Write","tool_input":{"file_path":"/tmp/secrets.env","content":"%s=sk-prod-realkeyhere\\n"}}' "$KEY_DENIED" | base64)"
  "2|deny: Write tool persists unknown key|$(printf '{"tool_name":"Write","tool_input":{"file_path":"/tmp/.env","content":"%s=mystery-value\\n"}}' "$KEY_UNKNOWN" | base64)"
  "0|allow: Write to .env.example with placeholder is fine|$(printf '{"tool_name":"Write","tool_input":{"file_path":"/path/.env.example","content":"%s=replace-me\\n"}}' "$KEY_DENIED" | base64)"
  "0|allow: Write to meta/harness/docs/prompts/foo.md (doc surface)|$(printf '{"tool_name":"Write","tool_input":{"file_path":"/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/meta/harness/docs/prompts/foo.md","content":"set %s=example for testing"}}' "$KEY_DENIED" | base64)"
  "0|allow: Write to this hook file itself|$(printf '{"tool_name":"Write","tool_input":{"file_path":"/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/.claude/hooks/no-paid-api-key.sh","content":"# test %s=any\\n"}}' "$KEY_DENIED" | base64)"
)

pass=0
fail=0
total=${#fixtures[@]}
declare -a failures

for row in "${fixtures[@]}"; do
  expected="${row%%|*}"
  rest="${row#*|}"
  label="${rest%%|*}"
  payload_b64="${rest#*|}"

  payload="$(printf '%s' "$payload_b64" | base64 --decode)"
  err="$(printf '%s' "$payload" | "$HOOK" 2>&1 1>/dev/null)"; actual=$?

  if [ "$actual" = "$expected" ]; then
    status="PASS"
    pass=$((pass+1))
  else
    status="FAIL"
    fail=$((fail+1))
    failures+=("$label (expected=$expected actual=$actual)")
  fi

  printf '%s  expected=%s actual=%s — %s\n' "$status" "$expected" "$actual" "$label"
  if [ -n "$err" ] && [ "$actual" = "2" ]; then
    reason_line="$(printf '%s' "$err" | grep -E '^Rule violated' | head -1)"
    [ -n "$reason_line" ] && printf '       %s\n' "$reason_line"
  fi
done

printf '\n=== Summary: %d/%d pass ===\n' "$pass" "$total"
if [ "$fail" -ne 0 ]; then
  printf '\nFailures:\n'
  for f in "${failures[@]}"; do
    printf '  - %s\n' "$f"
  done
  exit 1
fi
