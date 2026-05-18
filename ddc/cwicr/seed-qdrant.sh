#!/usr/bin/env bash
# Deterministic CWICR seed preflight.
#
# The upstream release currently ships large per-locale Qdrant snapshots rather than a
# single repo-managed tarball or a validated repo-local import workflow. Until a
# restore path is proven here, this helper stays honest: it verifies whether the target
# collection already satisfies the expected CWICR contract and exits non-zero with
# machine-readable blocker details when it does not.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

exec uv run python "$REPO_ROOT/scripts/verify-cwicr-seed.py" "$@"
