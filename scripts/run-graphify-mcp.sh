#!/usr/bin/env bash
set -euo pipefail

graphify_bin="${GRAPHIFY_BIN:-$HOME/.local/bin/graphify}"
graph_path="${1:-${GRAPHIFY_GRAPH_PATH:-graphify-out/graph.json}}"

if [[ ! -x "$graphify_bin" ]]; then
  echo "graphify executable not found at $graphify_bin" >&2
  exit 1
fi

resolved_bin="$(readlink "$graphify_bin")"
python_bin="$(cd "$(dirname "$resolved_bin")" && pwd)/python"

if [[ ! -x "$python_bin" ]]; then
  echo "graphify Python runtime not found at $python_bin" >&2
  exit 1
fi

exec "$python_bin" -m graphify.serve "$graph_path"
