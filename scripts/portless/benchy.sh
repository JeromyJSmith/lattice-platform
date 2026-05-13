#!/usr/bin/env bash
# Run the Benchy Vue client behind https://benchy.localhost
set -euo pipefail
REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT/meta/harness/benchy/client"
exec portless bun run dev
