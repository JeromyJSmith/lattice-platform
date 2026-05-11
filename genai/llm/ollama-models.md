# Ollama Models for LATTICE

Apple Silicon-native, runs entirely on Metal Performance Shaders backend. No GPU passthrough or Docker needed.

## Install

```bash
brew install ollama
ollama serve  # in one terminal
# in another:
ollama pull llama3.3:70b
ollama pull qwen2.5-coder:32b
ollama pull mistral-nemo:12b
ollama pull nomic-embed-text
```

## Recommended set

| Model | Size on disk | RAM/VRAM | Context | LATTICE role |
|---|---|---|---|---|
| `llama3.3:70b` | ~40 GB | 48+ GB unified | 128k | Heavyweight reasoning fallback; only when `claude -p` unavailable |
| `qwen2.5-coder:32b` | ~19 GB | 32 GB unified | 32k | Code generation, deterministic structured-output tasks |
| `mistral-nemo:12b` | ~7 GB | 16 GB unified | 128k | Cheap classification, status extraction, fast triage |
| `nomic-embed-text` | ~280 MB | 4 GB | 8k | Text embeddings for Pixeltable computed columns |

## Register them with LATTICE

After `ollama pull`, run the model-registry sync (when [`model-router.py`](model-router.py) is implemented):

```bash
python3 genai/llm/model-router.py --sync-registry
```

This populates `lattice/genai/model_registry` with one row per locally-available Ollama model, marking `provider='ollama'`, `endpoint='http://localhost:11434'`, `status='available'`.

## Why these picks

- **llama3.3:70b** — best non-Anthropic open model for AEC reasoning. Falls back behind `claude -p` because it doesn't have the same construction-domain training, but it's fully offline.
- **qwen2.5-coder:32b** — outperforms larger general models on structured code/JSON output tasks. Used for converting agent intents into Pixeltable rows.
- **mistral-nemo:12b** — fast enough to be the default for "classify this 3-line message" tasks. Burns no Claude tokens.
- **nomic-embed-text** — the embedding model the sidecar's `sentence-transformers/all-mpnet-base-v2` pin in `pixeltable/migrations/0011` was chosen for; nomic is a drop-in if you want a different speed/quality trade-off.
