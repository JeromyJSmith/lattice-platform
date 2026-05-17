#!/usr/bin/env bash
set -euo pipefail

ROOT="/Volumes/PixelTable/VW_iTWIN_Bridge/lattice-worktrees/feat-fre-meta-harness-eval"
FRE_ROOT="$ROOT/meta/harness/fre"

required_docs=(
  "$FRE_ROOT/docs/research-grounding.md"
  "$FRE_ROOT/docs/research-findings.md"
  "$FRE_ROOT/docs/source-normalization.md"
  "$FRE_ROOT/docs/sources.md"
)

for doc in "${required_docs[@]}"; do
  if [[ ! -f "$doc" ]]; then
    echo "missing required research doc: $doc" >&2
    exit 1
  fi
done

uv run pytest "$FRE_ROOT/tests"
uv run python "$FRE_ROOT/harness/iterate.py"
