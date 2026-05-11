#!/usr/bin/env python3
# spec-verified: code.claude.com/docs 2026-05-11
"""STUB — full implementation tracked as Issue #24.

Final form will:
  1. Read scripts/doc-mirror-manifest.yaml
  2. Walk each local_path
  3. For every doc file matching category_map, insert pxt.Document into
     lattice/knowledge/docs with proper tool_name + doc_category + git_sha
  4. doc_chunks view + embedding index auto-populate via DocumentSplitter
"""
print("ingest-docs: STUB — see Issue #24")
