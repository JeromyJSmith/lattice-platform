# SFA Evaluation Folder

Pre-capability staging area for Single-File Agents (SFAs) that are being evaluated before promotion to a specific section harness.

## Why a separate folder

The Grove harness (`/Volumes/PixelTable/GROVE_HARNESS/juniper2026`) ships **30 SFAs** plus the Disler upstream contributes **provider-variant agents**. Most are LATTICE-relevant but their final home depends on what they actually do once we run them. Rather than guess up-front, we land them here, run them, observe their behavior, then promote each row in `analysis/capabilities/grove-harness-capability-registry.yaml` from `DEFERRED` → `ACTIVE` in the same commit that moves the SFA to its proper harness directory (`meta/harness/tools/sfa-schema/`, `sfa-georef/`, etc.) — yet to be created.

This folder is **temporary**. Every SFA here is one of:

1. **Under evaluation** — we ran it, captured a session, haven't committed to a home yet.
2. **Proof-of-pattern** — demonstrates a substrate piece works (e.g. local-model swap).

## What's here

| File | Source pattern | LLM? | Status |
|---|---|---|---|
| `sfa_init_caches.py` | LATTICE-adapted port of `juniper2026/harness/init_caches.py` | no | proof: marker contract works |
| `sfa_duckdb_local_v1.py` | LATTICE port of `disler/sfa_duckdb_openai_v2.py`, OpenAI→llama-swap+bonsai | yes | proof: local-model swap works on bonsai-8b |

## How to add a new evaluation SFA

1. Copy the source SFA into this folder. Adapt paths to LATTICE only (don't re-architect).
2. Keep the PEP 723 header and marker JSON contract per `SPEC_SFA_PATTERN.md` (lifted from Grove).
3. Marker writes to `meta/harness/state/_<tool>.done.json`.
4. Session transcript writes to `meta/harness/docs/sessions/<date>-<tool>-<tag>.json`.
5. Run it; capture the session JSON; commit the SFA + session evidence.
6. Add a row to `analysis/capabilities/grove-harness-capability-registry.yaml` only after the proof passes — same commit as the move out of `sfa-eval/` and into its final harness directory.

## Substrate dependencies

- **llama-swap** running on `http://localhost:9090` for any LLM-using SFA. Start it via `bash meta/harness/bin/llama-swap/llama-swap -config meta/harness/bin/llama-swap/config.yaml -listen :9090 &`
- **DuckDB cache** populated via `uv run meta/harness/tools/sfa-eval/sfa_init_caches.py`
- **Pixeltable** running for any SFA that hits `lattice/*` tables (Wave 1 PR #383 brings this up to date)

## Findings so far — local-model swap

`sfa_duckdb_local_v1.py` proves the architecture:

| Model | Result | Iterations | Wall time | Why |
|---|---|---|---|---|
| `bonsai-1.7b` | (not tested — too small for multi-turn tool calling) | — | — | — |
| `bonsai-4b` | ❌ FAIL | 8 (max) | 6.0 s | Emits Qwen-style `<tool_call>` JSON with only `reasoning` field; drops other required args |
| **`bonsai-8b`** | ✅ PASS | 6 | 17.9 s (cold), 11.4 s (warm) | Handles multi-step tool calling; generates correct SQL |
| `qwen3.6-35b` | (not tested yet — candidate for future eval) | — | — | — |

**Wire-format note.** mlx_lm.server does not currently translate Qwen-style `<tool_call>...</tool_call>` content blocks into the OpenAI `tool_calls` API field. `sfa_duckdb_local_v1.py` ships a fallback parser (`extract_pseudo_tool_calls`) that scans the response content for both `<tool_call>{...}</tool_call>` XML blocks and bare `{"name": ..., "arguments": ...}` JSON objects. This is the bridge that makes any Qwen-family model work through the llama-swap endpoint.

Without that parser, **none of the local Qwen-derived models would work for tool-calling SFAs**. With it, `bonsai-8b` solved real DuckDB query tasks end-to-end on the first attempt.

## Two evidence files per proof run

```
meta/harness/state/_<tool>.done.json                          ← L1 → L2 marker
meta/harness/docs/sessions/<date>-<tool>-<tag>.json          ← Full transcript
```

The marker has the canonical SPEC_SFA_PATTERN shape (`ok`, `timestamp`, plus domain fields). The session log has the marker payload PLUS the full conversation transcript for debugging and future fine-tuning data.

## When to promote out of `sfa-eval/`

A row in `analysis/capabilities/grove-harness-capability-registry.yaml` moves from `DEFERRED` → `ACTIVE` when:

1. The SFA has been run at least once with a passing marker.
2. The session evidence file is committed alongside the SFA.
3. The SFA has been moved to its final harness directory (or LATTICE-owned name).
4. The registry row is updated in the **same commit** as the move and includes `wired_at: [...]` and `invoked_by: [...]` per `.claude/rules/capability-harvest-protocol.md`.
