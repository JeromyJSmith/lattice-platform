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

| Backend | Install | Authentication |
|---|---|---|
| `claude` | [Claude Code](https://docs.anthropic.com/claude-code) | `claude login` (Anthropic account) |
| `codex` | `brew install codex` or `npm install -g @openai/codex` | `OPENAI_API_KEY` or `codex login` |
| `copilot` | `gh extension install github/gh-copilot` | GitHub Copilot subscription via `gh auth login` |
| `ollama` | `brew install ollama` | None — runs locally |

Run `meta/harness/bin/llm --list` to see what's actually present on this machine.

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
