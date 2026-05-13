#!/usr/bin/env bash
# Run llama-swap behind https://llm.localhost
set -euo pipefail
REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT/meta/harness/bin/llama-swap"
# Portless sets $PORT; llama-swap honors -listen :PORT
exec portless ./llama-swap -config config.yaml -listen ":${PORT:-9090}" -watch-config
