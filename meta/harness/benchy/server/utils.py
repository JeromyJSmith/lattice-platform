import time
from contextlib import contextmanager
from typing import Generator, Optional
from modules.data_types import ModelAlias


@contextmanager
def timeit() -> Generator[None, None, float]:
    """
    Context manager to measure execution time in milliseconds.

    Usage:
        with timeit() as t:
            # code to time
        elapsed_ms = t()

    Returns:
        Generator that yields None and returns elapsed time in milliseconds
    """
    start = time.perf_counter()
    yield lambda: int((time.perf_counter() - start) * 1000)


MAP_MODEL_ALIAS_TO_COST_PER_MILLION_TOKENS = {
    "gpt-4o-mini": {
        "input": 0.15,
        "output": 0.60,
    },
    "o1-mini-json": {
        "input": 3.00,
        "output": 15.00,
    },
    "claude-3-haiku-20240307": {
        "input": 0.25,
        "output": 1.25,
    },
    "gpt-4o": {
        "input": 2.50,
        "output": 10.00,
    },
    "gpt-4o-predictive": {
        "input": 2.50,
        "output": 10.00,
    },
    "gpt-4o-mini-predictive": {
        "input": 0.15,
        "output": 0.60,
    },
    "claude-3-5-haiku-latest": {
        "input": 1.00,
        "output": 5.00,
    },
    "claude-3-5-sonnet-20241022": {
        "input": 3.00,
        "output": 15.00,
    },
    "gemini-1.5-pro-002": {
        "input": 1.25,
        "output": 5.00,
    },
    "gemini-exp-1114-json": {
        "input": 1.25,
        "output": 5.00,
    },
    "gemini-1.5-flash-002": {
        "input": 0.075,
        "output": 0.300,
    },
    "gemini-1.5-flash-8b-latest": {
        "input": 0.0375,
        "output": 0.15,
    },
    # JSON variants with same pricing as base models
    "gpt-4o-json": {
        "input": 2.50,
        "output": 10.00,
    },
    "gpt-4o-mini-json": {
        "input": 0.15,
        "output": 0.60,
    },
    "gemini-1.5-pro-002-json": {
        "input": 1.25,
        "output": 5.00,
    },
    "gemini-1.5-flash-002-json": {
        "input": 0.075,
        "output": 0.300,
    },
    "claude-3-5-sonnet-20241022-json": {
        "input": 3.00,
        "output": 15.00,
    },
    "claude-3-5-haiku-latest-json": {
        "input": 1.00,
        "output": 5.00,
    },
    "deepseek-chat": {
        "input": 0.14,
        "output": 0.28,
    },
    "o1-mini": {
        "input": 1.10,
        "output": 4.40,
    },
    "o3-mini": {
        "input": 1.10,
        "output": 4.40,
    },
    "o1-preview": {
        "input": 15.00,
        "output": 60.00,
    },
    "o1": {
        "input": 15.00,
        "output": 60.00,
    },
    "gemini-2.0-flash-exp": {
        "input": 0.00,
        "output": 0.00,
    },
}


def parse_markdown_backticks(str) -> str:
    if "```" not in str:
        return str.strip()
    # Remove opening backticks and language identifier
    str = str.split("```", 1)[-1].split("\n", 1)[-1]
    # Remove closing backticks
    str = str.rsplit("```", 1)[0]
    # Remove any leading or trailing whitespace
    return str.strip()


def deepseek_r1_distil_separate_thoughts_and_response(
    response: str, xml_tag: str = "think"
) -> tuple[str, str]:
    """
    Parse DeepSeek R1 responses containing <think> blocks and separate thoughts from final response.

    Args:
        response: Raw model response string
        xml_tag: XML tag to look for (default: 'think')

    Returns:
        tuple: (thoughts, response) where:
            - thoughts: concatenated content from all <think> blocks
            - response: cleaned response with <think> blocks removed
    """
    import re
    from io import StringIO
    import logging

    thoughts = []
    cleaned_response = response

    try:
        # Find all think blocks using regex (more fault-tolerant than XML parsing)
        pattern = re.compile(rf"<{xml_tag}>(.*?)</{xml_tag}>", re.DOTALL)
        matches = pattern.findall(response)

        if matches:
            # Extract and clean thoughts
            thoughts = [m.strip() for m in matches]

            # Remove think blocks from response
            cleaned_response = pattern.sub("", response).strip()

            # Remove any remaining XML tags if they exist
            cleaned_response = re.sub(r"<\/?[a-zA-Z]+>", "", cleaned_response).strip()

        return "\n\n".join(thoughts), cleaned_response

    except Exception as e:
        logging.error(f"Error parsing DeepSeek R1 response: {str(e)}")
        # Fallback - return empty thoughts and full response
        return "", response.strip()


def parse_reasoning_effort(model: str) -> tuple[str, Optional[str]]:
    """
    Parse a model string to extract reasoning effort.
    If the model contains ":low", ":medium" or ":high" (case‐insensitive),
    returns (base_model, effort) where effort is the lowercase string.
    Otherwise returns (model, None).
    """
    if ":" in model:
        base_model, effort_candidate = model.rsplit(":", 1)
        effort_candidate = effort_candidate.lower().strip()
        if effort_candidate in {"low", "medium", "high"}:
            return base_model, effort_candidate
    return model, None
