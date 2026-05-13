"""MLX adapter for Benchy.

Routes prompts to local MLX models via the `mlx_lm.generate` CLI (already
installed system-wide as a uv tool). Free, runs on Apple Silicon, supports
PrismML Ternary Bonsai (1.58-bit), Hermes, Qwen, Gemma, Llama — any model
on https://huggingface.co/mlx-community or https://huggingface.co/prism-ml.

Model strings use HF repo IDs verbatim, e.g.:
    mlx:prism-ml/Ternary-Bonsai-8B-mlx-2bit
    mlx:mlx-community/Hermes-3-Llama-3.1-8B-4bit
"""
from __future__ import annotations

import re
import shutil
import subprocess
from modules.data_types import PromptResponse, ThoughtResponse
from utils import timeit

_MLX_BIN = shutil.which("mlx_lm.generate") or "mlx_lm.generate"

# Regex to strip the boxed banner mlx_lm prints around generated text:
#   ==========
#   <text>
#   ==========
#   Prompt: ... tokens-per-sec
#   Generation: ... tokens-per-sec
#   Peak memory: ...
_BANNER = re.compile(r"^=+\s*$", re.MULTILINE)
_STATS_TAIL = re.compile(
    r"\n(Prompt|Generation|Peak memory):.*$", re.DOTALL
)


def _strip_mlx_output(raw: str) -> str:
    """Return only the model's generated text — drop banners and stats."""
    text = _STATS_TAIL.sub("", raw)
    # Slice between the first two `==========` banners if both exist.
    banners = list(_BANNER.finditer(text))
    if len(banners) >= 2:
        text = text[banners[0].end(): banners[1].start()]
    return text.strip()


def text_prompt(prompt: str, model: str, max_tokens: int = 2048) -> PromptResponse:
    """Send a prompt to an MLX model via the `mlx_lm.generate` CLI."""
    try:
        with timeit() as t:
            result = subprocess.run(
                [_MLX_BIN, "--model", model, "--prompt", prompt, "--max-tokens", str(max_tokens)],
                capture_output=True,
                text=True,
                timeout=600,
                check=False,
            )
            elapsed_ms = t()
        if result.returncode != 0:
            return PromptResponse(
                response=f"Error: mlx_lm exited {result.returncode}\n{result.stderr[-500:]}",
                runTimeMs=elapsed_ms,
                inputAndOutputCost=0.0,
            )
        return PromptResponse(
            response=_strip_mlx_output(result.stdout),
            runTimeMs=elapsed_ms,
            inputAndOutputCost=0.0,  # local, no cost
        )
    except subprocess.TimeoutExpired:
        return PromptResponse(
            response="Error: mlx_lm timed out (600s)",
            runTimeMs=0,
            inputAndOutputCost=0.0,
        )
    except Exception as e:
        return PromptResponse(
            response=f"Error: {e}",
            runTimeMs=0,
            inputAndOutputCost=0.0,
        )


def thought_prompt(prompt: str, model: str) -> ThoughtResponse:
    """Stub for reasoning models — falls back to plain text."""
    text = text_prompt(prompt, model)
    return ThoughtResponse(thoughts="", response=text.response, error=None)


def get_mlx_costs() -> tuple[int, int]:
    """MLX is local — zero cost."""
    return 0, 0


# Regex to pull mlx_lm's stats lines:
#   "Prompt: 25 tokens, 207.379 tokens-per-sec"
#   "Generation: 11 tokens, 135.742 tokens-per-sec"
#   "Peak memory: 2.407 GB"
_STAT_LINE = re.compile(
    r"^(Prompt|Generation):\s+(\d+)\s+tokens?,\s+([\d.]+)\s+tokens-per-sec",
    re.MULTILINE,
)


def bench_prompt(prompt: str, model: str, max_tokens: int = 1024):
    """Send a prompt and return BenchPromptResponse with measured tok/s.

    Parses mlx_lm.generate's stdout stats footer for token counts + speed.
    """
    from modules.data_types import BenchPromptResponse

    try:
        with timeit() as t:
            result = subprocess.run(
                [_MLX_BIN, "--model", model, "--prompt", prompt, "--max-tokens", str(max_tokens)],
                capture_output=True,
                text=True,
                timeout=600,
                check=False,
            )
            elapsed_ms = t()
        if result.returncode != 0:
            return BenchPromptResponse(
                response=f"Error: mlx_lm exited {result.returncode}\n{result.stderr[-500:]}",
                tokens_per_second=0.0,
                provider="mlx",
                total_duration_ms=elapsed_ms,
                load_duration_ms=0.0,
                errored=True,
            )

        stats = {m.group(1): (int(m.group(2)), float(m.group(3))) for m in _STAT_LINE.finditer(result.stdout)}
        gen_tps = stats.get("Generation", (0, 0.0))[1]
        prompt_tps = stats.get("Prompt", (0, 0.0))[1]

        # Estimate load time: total wall time minus the model-token time
        prompt_tokens = stats.get("Prompt", (0, 0.0))[0]
        gen_tokens = stats.get("Generation", (0, 0.0))[0]
        model_seconds = 0.0
        if prompt_tps > 0:
            model_seconds += prompt_tokens / prompt_tps
        if gen_tps > 0:
            model_seconds += gen_tokens / gen_tps
        load_ms = max(0.0, elapsed_ms - model_seconds * 1000.0)

        return BenchPromptResponse(
            response=_strip_mlx_output(result.stdout),
            tokens_per_second=gen_tps,
            provider="mlx",
            total_duration_ms=elapsed_ms,
            load_duration_ms=load_ms,
            inputAndOutputCost=0.0,
        )
    except subprocess.TimeoutExpired:
        return BenchPromptResponse(
            response="Error: mlx_lm timed out (600s)",
            tokens_per_second=0.0,
            provider="mlx",
            total_duration_ms=600_000.0,
            load_duration_ms=0.0,
            errored=True,
        )
    except Exception as e:
        return BenchPromptResponse(
            response=f"Error: {e}",
            tokens_per_second=0.0,
            provider="mlx",
            total_duration_ms=0.0,
            load_duration_ms=0.0,
            errored=True,
        )
