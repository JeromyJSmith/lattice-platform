#!/usr/bin/env bash
# Deterministic CWICR seed restore + verification.
#
# The bounded default path restores the published HI_MUMBAI 3072-d snapshot into the
# local `cwicr` collection when needed, then verifies the resulting collection contract.
# Full multi-locale CWICR seeding remains a larger follow-on task.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

exec uv run python "$REPO_ROOT/scripts/verify-cwicr-seed.py" --restore-if-needed "$@"
