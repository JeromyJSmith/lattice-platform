# Model Router

The Meta-Harness is model-agnostic. Any task that calls an LLM goes through the router at [`meta/harness/bin/llm`](bin/llm), which reads [`meta/harness/config/models.json`](config/models.json) and dispatches to the configured backend. If the primary fails or its backend isn't installed, the router falls through to the next entry in the chain.

No backend is "the" backend. Swap them by editing the JSON.

## Quick start

```bash
# See which backends are installed + the current task → model map
meta/harness/bin/llm --list

# Run a task using its configured chain
meta/harness/bin/llm --task=propose "Suggest one schema improvement."

# Pin a specific backend for one call
meta/harness/bin/llm --backend=ollama:qwen2.5-coder:7b "..."

# Use stdin for the prompt
cat prompt.txt | meta/harness/bin/llm --task=review
```

## Switching the model the autoresearch ratchet uses

Edit [`config/models.json`](config/models.json), change the `propose` task's `primary`:

```jsonc
"propose": { "primary": "ollama:qwen2.5-coder:7b", "fallback": ["claude", "codex"] }
```

For a one-shot override without editing config:

```bash
HARNESS_BACKEND=ollama:qwen2.5-coder:7b bash meta/harness/bootstrap/run-autoresearch.sh schema
```

## Supported backends

| Backend | Install | Authentication | Notes |
|---|---|---|---|
| `claude` | [Claude Code](https://docs.anthropic.com/claude-code) | `claude login` | Anthropic Claude Code CLI |
| `codex` | `brew install codex` | `codex login` or `OPENAI_API_KEY` | OpenAI Codex CLI |
| `copilot` | `gh extension install github/gh-copilot` | GitHub Copilot subscription | Uses your paid Copilot |
| `ollama` | `brew install ollama` | None — local | GGUF models, broadest model zoo |
| `mlx-lm` | `uv tool install mlx-lm` | None — local | Apple Silicon native, ~2-4× faster than Ollama on M-series |
| `mlx-vlm` | `uv tool install mlx-vlm` | None — local | Vision-language (Qwen2-VL, LLaVA, etc.) |
| `omlx` | [oMLX.app](https://github.com/oMLX/oMLX) | None — local | Multi-model OpenAI-compatible server for Apple Silicon |

Run `meta/harness/bin/llm --list` to see what's actually present on this machine.

## PrismML Ternary Bonsai (recommended local primary)

PrismML released the Ternary Bonsai model family in April 2026 — Apache 2.0, native MLX support, weights constrained to `{-1, 0, +1}` with group-wise FP16 scaling. Approximately **9× smaller memory footprint** than equivalent FP16 models while maintaining benchmark parity. Three sizes:

| Model | Disk | Peak mem | Speed (M3 Max) | Use case |
|---|---|---|---|---|
| `prism-ml/Ternary-Bonsai-1.7B-mlx-2bit` | 495 MB | 0.54 GB | **418 tok/s** | Triage, classification, quick suggestions |
| `prism-ml/Ternary-Bonsai-4B-mlx-2bit` | 1.1 GB | 1.22 GB | **216 tok/s** | General reasoning, fallback for proposals |
| `prism-ml/Ternary-Bonsai-8B-mlx-2bit` | 2.3 GB | 2.41 GB | **136 tok/s** | Primary local — 75.5 avg benchmark score |

All three are already cached on this machine. The router uses them automatically:
- `quick` task → 1.7B primary
- `local` task → 8B primary
- `agent-loop`, `propose`, `docs`, `triage` → all have a Bonsai fallback in their chain

```bash
# Direct one-shot via router
meta/harness/bin/llm --backend=mlx-lm:prism-ml/Ternary-Bonsai-8B-mlx-2bit "..."

# Or pin Bonsai for an entire ratchet cycle
HARNESS_BACKEND=mlx-lm:prism-ml/Ternary-Bonsai-8B-mlx-2bit \
  bash meta/harness/bootstrap/run-autoresearch.sh schema
```

To pull additional sizes or a fresh copy:
```bash
hf download prism-ml/Ternary-Bonsai-1.7B-mlx-2bit
hf download prism-ml/Ternary-Bonsai-4B-mlx-2bit
hf download prism-ml/Ternary-Bonsai-8B-mlx-2bit
```

Refs: [PrismML announcement](https://prismml.com/news/ternary-bonsai) · [HF collection](https://huggingface.co/collections/prism-ml/bonsai) · [Bonsai-demo repo](https://github.com/PrismML-Eng/Bonsai-demo/)

## MLX-LM: other recommended models

Apple Silicon native — same `mlx_lm.generate` CLI, auto-downloads from HF on first call:

```bash
# Code reasoning
mlx_lm.generate --model mlx-community/Qwen2.5-Coder-7B-Instruct-4bit --prompt "..."

# General reasoning, 14B
mlx_lm.generate --model mlx-community/Qwen2.5-14B-Instruct-4bit --prompt "..."

# Reasoning chains (for plan-review)
mlx_lm.generate --model mlx-community/DeepSeek-R1-Distill-Qwen-14B-4bit --prompt "..."
```

Browse: https://huggingface.co/mlx-community

## MLX-VLM: vision-language models

For tasks involving drone frames, IFC screenshots, or plan-sheet OCR:

```bash
mlx_vlm.generate --model mlx-community/Qwen2-VL-7B-Instruct-4bit \
  --image /path/to/frame.jpg --prompt "Identify the plant species visible."
```

The router currently passes text-only via the `vision` task. To use images, call `mlx_vlm.generate` directly or extend the `cmd` array in `mlx-vlm` backend config to accept `--image` from the prompt structure.

## oMLX: multi-model server (advanced)

oMLX is a production-ready OpenAI-compatible server for Apple Silicon — useful when you want a single long-running process serving multiple models with hot-swap:

```bash
# Start a server bound to one model
omlx serve mlx-community/Llama-3.2-3B-Instruct-4bit --port 8000

# Or launch another CLI tool (Codex, etc.) against a local model
omlx launch codex --model prism-ml/Ternary-Bonsai-8B-mlx-2bit
```

The router calls oMLX in `launch` mode by default. For server-mode integration, point an OpenAI-SDK client at `http://localhost:8000/v1`.

## Ollama: recommended models for the harness

```bash
# Code reasoning (best for proposals, agent loops)
ollama pull qwen2.5-coder:7b      # 4.7 GB — fast, good code
ollama pull qwen2.5-coder:14b     # 9.0 GB — stronger code

# General reasoning (docs, research, plan review)
ollama pull qwen2.5:14b           # 8.7 GB
ollama pull deepseek-r1:14b       # 9.0 GB — reasoning chains

# Quick tasks (triage, classification)
ollama pull llama3.2:3b           # 2.0 GB — fast

# Long-context code
ollama pull codestral:22b         # 13 GB
```

After pulling, the router auto-detects them — no config change needed unless you want to make them primary for a task.

## Task table (current defaults)

| Task | Primary | Fallback chain |
|---|---|---|
| `propose` | `claude` | `ollama:qwen2.5-coder:7b` → `codex` → `copilot` |
| `agent-loop` | `claude` | `ollama:qwen2.5-coder:7b` |
| `triage` | `copilot` | `claude` → `ollama:llama3.2:3b` |
| `review` | `codex` | `claude` → `ollama:qwen2.5-coder:7b` |
| `docs` | `claude` | `ollama:qwen2.5:14b` |
| `local` | `ollama:qwen2.5-coder:7b` | `ollama:llama3.2:3b` |
| `quick` | `ollama:llama3.2:3b` | `claude` |

These are starting points. Tune them in [`config/models.json`](config/models.json).

## Adding a new backend

Edit `config/models.json` `backends`:

```jsonc
"mybackend": {
  "cmd": ["my-cli", "--prompt"],
  "stdin_prompt": false,
  "prompt_as_arg": true,
  "stream": false,
  "auth_check": "my-cli --version",
  "install": "npm install -g my-cli",
  "notes": "What it does."
}
```

Then reference it in a task's `primary` or `fallback`. The router handles the rest.

## What the harness uses today

- **`meta/harness/bootstrap/run-autoresearch.sh`** — calls `llm --task=propose`
- **`pixeltable/service/worker.py`** — *will be* migrated to `llm --task=agent-loop` in a follow-up (currently still uses `claude -p` directly via subprocess, but the API is identical)

## Failure semantics

- A backend is "unavailable" if its `auth_check` command returns non-zero (extension not installed, not logged in, etc.). The router skips it and tries the next.
- A backend "failed" if its CLI ran but exited non-zero. Same handling — try the next.
- Timeout (default 180s per attempt) — same handling.
- Final exit code `2` if every backend in the chain was unavailable or failed.

The harness ratchet treats `2` as "no proposal this cycle" — not an error. The loop stays healthy and tries again next time.

## Why this exists

The platform's quality flywheel cannot be tied to a single vendor. If Anthropic has an outage, the harness should keep running. If you want a private-data task to stay local, Ollama handles it. If you have a Copilot subscription paid for already, use it for what it's good at. The router makes those choices configuration, not code.

## Two HF caches on this machine

The router and mlx_lm respect `HF_HUB_CACHE`. There are two caches in play here:

| Path | Default? | Contents |
|---|---|---|
| `~/.cache/huggingface/hub/` | yes | Bonsai 1.7B/4B/8B · Hermes-3-8B · Qwen3.6-35B · Gemma-4-26B (4bit) |
| `/Volumes/PixelTable/models/huggingface-cache/` | no | Gemma-4-26B (NVFP4) · Gemma-2-2B · Gemma-4-E4B (FP16) · BitNet 1.58 2B · whisper-large-v3 · plus Pixeltable-side workloads |

To use the Pixeltable cache instead of the home cache (e.g. to run NVFP4 Gemma):

```bash
HF_HUB_CACHE=/Volumes/PixelTable/models/huggingface-cache \
  meta/harness/bin/llm --backend=mlx-lm:mlx-community/gemma-4-26b-a4b-nvfp4 "..."
```

For Benchy, add to `meta/harness/benchy/server/.env`:
```
HF_HUB_CACHE=/Volumes/PixelTable/models/huggingface-cache
```

There is no native "search both caches" mode in huggingface_hub. The model you want must be in whichever cache `HF_HUB_CACHE` points to.

## Heretic / abliterated models (GGUF — via Ollama, not direct MLX)

PrismML's Ternary Bonsai ships with built-in safety alignment. For uncensored / abliterated work the project has GGUF weights cached at:

| Path | What | Size | Wire-up |
|---|---|---|---|
| `/Volumes/PixelTable/gemma4-heretical/` | Script that pulls `trohrbaugh/gemma-4-31b-it-heretic-ara` and registers it in Ollama with the correct Gemma-4 chat template (community GGUFs ship the wrong one). ARA-abliterated, 5/100 refusal rate vs 98/100 stock, KL divergence 0.012. | 17-33 GB | `./get-gemma4-heretical Q4_K_M && ollama run gemma4-heretical` |
| `/Volumes/PixelTable/models/huggingface-cache/models--DavidAU--Qwen3-48B-A4B-Savant-Commander-Distill-12X-Closed-Open-Heretic-Uncensored-GGUF/` | DavidAU's 48B MoE mega-merge with "Heretic" branding. GGUF Q4_K_M. | 19 GB | Convert to Modelfile + `ollama create` |
| `/Volumes/Docker/_ai_/z-turbo/qwen3-4b-Z-Image-Engineer/qwen3-4b-heretic-merged-f16.gguf` | Smaller Qwen3-4B heretic merge, FP16. | ~8 GB | Same path |

These are **GGUF format** — they run via Ollama (or llama.cpp), not directly via `mlx_lm.generate`. To use one through the router:
1. Register it in Ollama: see `/Volumes/PixelTable/gemma4-heretical/get-gemma4-heretical` for the canonical script
2. Reference it via the Ollama backend: `meta/harness/bin/llm --backend=ollama:gemma4-heretical "..."`

To convert GGUF → MLX (so the model can run via `mlx-lm` directly): `mlx_lm.convert --hf-path <gguf-path> -q --q-bits 4`. Not currently wired in.
