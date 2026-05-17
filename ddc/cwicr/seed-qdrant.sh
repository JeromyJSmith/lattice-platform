#!/usr/bin/env bash
# Idempotent loader for the CWICR cost database into local Qdrant.
#
# Prereqs: see INSTALL.md (OrbStack + Docker + Qdrant running on :6333)
#
# Tracked in meta/FEATURE_BACKLOG.md § DDC INTEGRATION → "CWICR cost search".

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT_DIR"

echo "Seeding local CWICR sample collection in Qdrant..."
uv run ddc/cwicr/seed_qdrant.py
echo "CWICR seed completed."
