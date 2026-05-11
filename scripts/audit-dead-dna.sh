#!/usr/bin/env bash
# spec-verified: code.claude.com/docs 2026-05-11
# STUB — full implementation tracked as Issue #17
#
# Final form will:
#   1. Parse every analysis/capabilities/*-capability-registry.yaml
#   2. For each ACTIVE row, verify wired_at file:line refs actually exist
#   3. For each DEFERRED row, verify target_phase is not in the past relative to current PR phase tag
#   4. For each BLOCKED row, verify blocker_resolution_path is non-empty
#   5. For each registry, verify Zero Dead DNA: no UNKNOWN, no missing required fields
#   6. Print summary + exit non-zero on violations
#
# Until then this stub exits 0 so CI passes; the rule files mandate the contract.

set -euo pipefail

echo "audit-dead-dna: STUB — see Issue #17"
echo "registries present:"
ls analysis/capabilities/*-capability-registry.yaml 2>/dev/null || echo "  (none yet)"
echo "stub exits 0; CI gate will activate when Issue #17 lands"
exit 0
