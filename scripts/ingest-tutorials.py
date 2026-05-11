#!/usr/bin/env python3
# spec-verified: code.claude.com/docs 2026-05-11
"""STUB — full implementation tracked as Issue #20.

Final form will:
  1. Read playlist/channel/video URLs from a manifest (per-tool curated list)
  2. Call graphifyy ingest <url> to extract transcript metadata
  3. Download videos to local cache
  4. Insert rows into lattice/knowledge/tutorials (Pixeltable runs the
     computed columns: extract_audio → get_metadata → whisper.transcribe)
  5. The tutorial_sentences view + embedding index auto-populate
  6. Print a summary of (rows inserted, total runtime, embeddings generated)

For now this stub exits 0 so the substrate scaffold is complete.
"""
print("ingest-tutorials: STUB — see Issue #20")
print("Will populate lattice/knowledge/tutorials once tools allowlist + migration 0015 are live.")
