#!/usr/bin/env bash
set -euo pipefail

start_dir="${1:-$PWD}"
repo_root=""

if repo_root="$(git -C "$start_dir" rev-parse --show-toplevel 2>/dev/null)"; then
  :
elif [ -d "$start_dir/VW_iTwin_Bridge/.git" ]; then
  repo_root="$(cd "$start_dir/VW_iTwin_Bridge" && pwd)"
else
  echo "error: could not locate the LATTICE repo root from: $start_dir" >&2
  exit 1
fi

printf 'Repo root: %s\n\n' "$repo_root"

git -C "$repo_root" worktree list --porcelain | awk '
  /^worktree / { wt=substr($0,10) }
  /^HEAD / { head=substr($0,6) }
  /^branch / {
    branch=substr($0,8)
    sub("refs/heads/", "", branch)
    print wt "\t" branch "\t" head
  }
' | while IFS=$'\t' read -r wt branch head; do
  upstream="$(git -C "$wt" rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || true)"
  track="$(git -C "$wt" for-each-ref --format='%(upstream:trackshort)' "refs/heads/$branch" 2>/dev/null || true)"
  status="$(git -C "$wt" status --short | wc -l | tr -d ' ')"
  printf '%s\n' "Worktree: $wt"
  printf '  Branch: %s\n' "$branch"
  printf '  HEAD: %s\n' "$head"
  printf '  Upstream: %s\n' "${upstream:-none}"
  printf '  Divergence: %s\n' "${track:-none}"
  printf '  Dirty entries: %s\n' "$status"
  if [ "$status" != "0" ]; then
    git -C "$wt" status --short
  fi
  printf '\n'
done
