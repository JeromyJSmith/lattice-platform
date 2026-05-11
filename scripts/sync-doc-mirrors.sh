#!/usr/bin/env bash
# spec-verified: code.claude.com/docs 2026-05-11
# STUB — full implementation tracked as Issue #24
#
# Final form will:
#   1. Read scripts/doc-mirror-manifest.yaml
#   2. For each entry in mirrors[]:
#      - Sparse-clone source_repo with sparse_path checkout
#      - Record git_sha_before / git_sha_after
#      - Write row to lattice/knowledge/doc_sync_log
#   3. For deferred_mirrors[]: skip with note
#
# Until then this stub exits 0.

set -euo pipefail
echo "sync-doc-mirrors: STUB — see Issue #24"
echo "manifest: scripts/doc-mirror-manifest.yaml"
ls scripts/doc-mirror-manifest.yaml >/dev/null && echo "manifest present"
exit 0
