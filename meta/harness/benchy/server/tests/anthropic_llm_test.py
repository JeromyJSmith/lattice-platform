import pytest
from modules.anthropic_llm import text_prompt

def test_anthropic_text_prompt():
    response = text_prompt("ping", "claude-3-5-haiku-latest")
    assert response.response != ""
    assert response.runTimeMs > 0
    assert response.inputAndOutputCost > 0.0


def test_anthropic_bench_prompt():
    from modules.anthropic_llm import bench_prompt
    response = bench_prompt("ping", "claude-3-5-haiku-latest")
    assert response.response != ""
    assert response.total_duration_ms > 0
    # Verify cost computed is a non-negative float
    assert isinstance(response.inputAndOutputCost, float)
    assert response.inputAndOutputCost >= 0.0
