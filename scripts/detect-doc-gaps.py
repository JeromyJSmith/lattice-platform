#!/usr/bin/env python3
# spec-verified: code.claude.com/docs 2026-05-11
"""STUB — full implementation tracked as Issue #25.

Final form will:
  1. For each tool in analysis/capabilities/*-capability-registry.yaml:
     - For each ACTIVE row, query lattice/knowledge/doc_chunks for matches
       above 0.7 similarity, filtered by tool_name
     - If zero matches → gap_type='missing-api-ref', severity='critical'
     - If matches stale (git_sha older than capability tool_version) → 'stale-doc'
  2. Write ranked output to:
     - lattice/knowledge/doc_coverage_gaps table
     - analysis/gaps/docs-gap-report.md (markdown for human review)
  3. Optionally auto-open GitHub issues for critical-severity gaps
"""
print("detect-doc-gaps: STUB — see Issue #25")
