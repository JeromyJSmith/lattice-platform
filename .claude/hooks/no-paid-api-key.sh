#!/usr/bin/env bash
# .claude/hooks/no-paid-api-key.sh
#
# PreToolUse hook. Policy-driven allowlist/denylist for API-key wiring.
# Reads .claude/hooks/api-key-policy.json. Default behavior for any
# unrecognized *_API_KEY pattern is DENY.
#
# Spec authority:
#   meta/harness/docs/specs/agent-heavy-run-prompt-schema.md (hard_rules.environment)
#   meta/harness/docs/specs/agent-heavy-run-prompt-index.md  (Policy Summary)
#
# Exit 0 = allow. Exit 2 = block (stderr shown back to the agent).

set -euo pipefail

POLICY_FILE="${POLICY_FILE:-.claude/hooks/api-key-policy.json}"

input="$(cat || true)"
tool_name="$(printf '%s' "$input" | jq -r '.tool_name // ""')"

if [ -z "$tool_name" ]; then
  exit 0
fi

if [ ! -f "$POLICY_FILE" ]; then
  {
    printf 'BLOCKED by .claude/hooks/no-paid-api-key.sh\n\n'
    printf 'Rule violated: api-key policy file missing\n\n'
    printf 'Expected:  %s\n' "$POLICY_FILE"
    printf 'The hook requires an explicit allow/deny policy. Restore the policy file or remove this hook.\n'
  } >&2
  exit 2
fi

policy="$(cat "$POLICY_FILE")"
default_policy="$(printf '%s' "$policy" | jq -r '.default // "deny"')"

block() {
  local rule="$1"; shift
  {
    printf 'BLOCKED by .claude/hooks/no-paid-api-key.sh\n\n'
    printf 'Rule violated: %s\n\n' "$rule"
    printf '%s\n' "$@"
    printf '\nPolicy: %s (default = %s)\n' "$POLICY_FILE" "$default_policy"
    printf 'Spec authority:\n'
    printf '  meta/harness/docs/specs/agent-heavy-run-prompt-schema.md (hard_rules.environment)\n'
    printf '  meta/harness/docs/specs/agent-heavy-run-prompt-index.md  (Policy Summary)\n'
  } >&2
  exit 2
}

# Returns "allow", "deny", or "unknown" for a given key id and surface.
classify_key() {
  local key_id="$1"
  local surface="$2"   # bash_set | bash_propagate | file_persist
  printf '%s' "$policy" | jq -r --arg id "$key_id" --arg surface "$surface" '
    def member(list; id; s): list | map(select(.id == id and ((.enforce_on // []) | any(. == s)))) | length > 0;
    if   member(.denylist;  $id; $surface) then "deny"
    elif member(.allowlist; $id; $surface) then "allow"
    else "unknown"
    end
  '
}

# Returns the reason text for a key id from whichever list it lives in.
key_reason() {
  local key_id="$1"
  printf '%s' "$policy" | jq -r --arg id "$key_id" '
    ([(.denylist // []), (.allowlist // [])] | flatten | map(select(.id == $id)) | first | .reason) // "unspecified"
  '
}

# Returns space-separated list of executables that must strip the key.
key_must_strip_for() {
  local key_id="$1"
  printf '%s' "$policy" | jq -r --arg id "$key_id" '
    ([(.denylist // []), (.allowlist // [])] | flatten | map(select(.id == $id)) | first | .must_strip_when_invoking // []) | join(" ")
  '
}

# Extracts all *_API_KEY variable names being SET in a bash command.
# Matches: KEY=value, export KEY=value, env KEY=value (but NOT env -u KEY).
# Uses POSIX regex (no \b, works on BSD/macOS sed).
extract_set_keys() {
  local cmd="$1"
  printf '%s' "$cmd" \
    | grep -oE '[A-Z][A-Z0-9_]*_API_KEY=' \
    | tr -d '=' \
    | sort -u
}

# Extracts all *_API_KEY variable names being SET in a written file's content.
# A bare 'KEY=' alone (no value) does NOT match — value must start with [A-Za-z0-9].
extract_persist_keys() {
  local content="$1"
  printf '%s' "$content" \
    | grep -oE '[A-Z][A-Z0-9_]*_API_KEY=[A-Za-z0-9]' \
    | sed -E 's/=.*//' \
    | sort -u
}

# Returns 0 if the command contains `env -u KEY` or `unset KEY`,
# OR if it uses the canonical safe wrapper (claude-cli) which handles the
# stripping internally.
command_strips_key() {
  local cmd="$1"; local key_id="$2"
  # Safe wrapper short-circuit: claude-cli does `exec env -u <key>` internally.
  if printf '%s' "$cmd" | grep -qE '(^|[[:space:]|;&(`/])claude-cli([[:space:]]|$)'; then
    return 0
  fi
  printf '%s' "$cmd" \
    | grep -qE "(env[[:space:]]+(-u[[:space:]]+|--unset=)${key_id}|unset[[:space:]]+${key_id})"
}

# Returns 0 if the command invokes the given executable with -p/--print.
# Excludes hyphenated derivatives (e.g., `claude-cli` does NOT count as `claude`).
command_invokes_with_print() {
  local cmd="$1"; local exe="$2"
  printf '%s' "$cmd" \
    | grep -qE "(^|[[:space:]|;&(\`])(/[^[:space:]]*/)?${exe}([[:space:]]|$)" \
    && printf '%s' "$cmd" \
    | grep -qE '([[:space:]]|^)(-p|--print)([[:space:]]|$)'
}

# Returns 0 if the file path matches any safe-write glob in the policy.
path_is_safe_for_write() {
  local file_path="$1"
  local patterns
  patterns="$(printf '%s' "$policy" | jq -r '.file_write_safe_paths[]? // empty')"
  while IFS= read -r pat; do
    [ -z "$pat" ] && continue
    case "$file_path" in
      $pat|*/$pat) return 0 ;;
    esac
  done <<< "$patterns"
  return 1
}

case "$tool_name" in
  Bash)
    command="$(printf '%s' "$input" | jq -r '.tool_input.command // ""')"

    # 1) Check every *_API_KEY being SET in the command.
    keys_set="$(extract_set_keys "$command" || true)"
    if [ -n "$keys_set" ]; then
      while IFS= read -r key_id; do
        [ -z "$key_id" ] && continue
        verdict="$(classify_key "$key_id" "bash_set")"
        case "$verdict" in
          deny|unknown)
            reason="$(key_reason "$key_id")"
            label="explicitly denylisted"
            [ "$verdict" = "unknown" ] && label="not allowlisted (default = $default_policy)"
            block \
              "API key $key_id $label" \
              "Reason: $reason" \
              "" \
              "If this key truly should be allowed, add it to .allowlist in $POLICY_FILE with explicit enforce_on values and a reason, then re-run."
            ;;
          allow)
            : # pass
            ;;
        esac
      done <<< "$keys_set"
    fi

    # 2) For every denylisted key with must_strip_when_invoking, check that
    #    when those executables are invoked with -p/--print, the key is stripped.
    denylist_ids="$(printf '%s' "$policy" | jq -r '.denylist[]?.id // empty')"
    while IFS= read -r key_id; do
      [ -z "$key_id" ] && continue
      strip_targets="$(key_must_strip_for "$key_id")"
      [ -z "$strip_targets" ] && continue
      for exe in $strip_targets; do
        if command_invokes_with_print "$command" "$exe"; then
          if ! command_strips_key "$command" "$key_id"; then
            reason="$(key_reason "$key_id")"
            block \
              "invoking '$exe -p' through the unsafe API-key path" \
              "Reason: $reason" \
              "" \
              "Canonical safe form (preferred — uses .claude/bin/claude-cli wrapper):" \
              "  .claude/bin/claude-cli -p ..." \
              "  cat prompt.md | .claude/bin/claude-cli -p --permission-mode acceptEdits" \
              "" \
              "Or the explicit raw form:" \
              "  env -u $key_id $exe -p ..." \
              "  unset $key_id; $exe -p ..." \
              "" \
              "Authority: ~/.claude-code-docs/docs/authentication.md (Authentication precedence)."
          fi
        fi
      done
    done <<< "$denylist_ids"
    ;;

  Write|Edit|MultiEdit)
    file_path="$(printf '%s' "$input" | jq -r '.tool_input.file_path // ""')"
    new_text="$(printf '%s' "$input" | jq -r '.tool_input.new_string // .tool_input.content // ""')"

    if path_is_safe_for_write "$file_path"; then
      exit 0
    fi

    keys_persisted="$(extract_persist_keys "$new_text" || true)"
    if [ -n "$keys_persisted" ]; then
      while IFS= read -r key_id; do
        [ -z "$key_id" ] && continue
        verdict="$(classify_key "$key_id" "file_persist")"
        case "$verdict" in
          deny|unknown)
            reason="$(key_reason "$key_id")"
            label="denylisted for file persistence"
            [ "$verdict" = "unknown" ] && label="not allowlisted for file persistence (default = $default_policy)"
            block \
              "writing $key_id=<value> into $file_path" \
              "$key_id is $label." \
              "Reason: $reason" \
              "" \
              "Tracked files must never carry secret values. If this file is a documentation surface that should be allowed, add its path or a glob to .file_write_safe_paths in $POLICY_FILE."
            ;;
          allow)
            : # explicit allow — pass
            ;;
        esac
      done <<< "$keys_persisted"
    fi
    ;;
esac

exit 0
