# Local LLMs in LATTICE

LATTICE talks to two LLM surfaces:

1. **`claude -p` CLI** (Claude Max subscription) — `pixeltable/service/worker.py` already wires this. Long-context, AEC-domain reasoning, code synthesis, design discussion.
2. **Ollama** (local) — cheap classification, fast embeddings, fallback when offline. Routed via [`model-router.py`](model-router.py).

Recommended Ollama models for an Apple Silicon Mac (see [`ollama-models.md`](ollama-models.md) for the install commands + size/VRAM details):

| Model | Use case |
|---|---|
| `llama3.3:70b` | Heavyweight general reasoning when `claude -p` is unavailable |
| `qwen2.5-coder:32b` | Code generation, deterministic transforms |
| `mistral-nemo:12b` | Cheap, fast classification (status, sentiment, category) |
| `nomic-embed-text` | Text embeddings for Pixeltable computed columns |

The model router (`model-router.py`) is the single source of truth for "which model handles which task." It reads `lattice/genai/model_registry` (live, in Pixeltable) and routes based on task type + model status.
