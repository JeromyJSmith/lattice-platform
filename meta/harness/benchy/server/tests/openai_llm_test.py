import pytest
from modules.openai_llm import tool_prompt
from modules.tools import all_tools_list
from modules.data_types import ToolCallResponse, SimpleToolCall
import json
import types


@pytest.mark.parametrize(
    "prompt,expected_tool_calls,model",
    [
        (
            "Write code in main.py. Git commit it. Then document changes in README.md",
            [
                SimpleToolCall(tool_name="run_coder_agent", params={}),
                SimpleToolCall(tool_name="run_git_agent", params={}),
                SimpleToolCall(tool_name="run_docs_agent", params={}),
            ],
            "gpt-4o",
        ),
        (
            "Write some code for me in main.py, and then commit it to git",
            [
                SimpleToolCall(tool_name="run_coder_agent", params={}),
                SimpleToolCall(tool_name="run_git_agent", params={}),
            ],
            "gpt-4o",
        ),
        (
            "Document our latest feature",
            [SimpleToolCall(tool_name="run_docs_agent", params={})],
            "gpt-4o-mini",
        ),
    ],
)
def test_tool_prompt(
    prompt: str, expected_tool_calls: list[SimpleToolCall], model: str
):
    result = tool_prompt(prompt=prompt, model=model, force_tools=all_tools_list)

    # Verify response type and fields
    assert isinstance(result.tool_calls, list)
    assert isinstance(result.runTimeMs, int)
    assert isinstance(result.inputAndOutputCost, float)

    # Verify tool calls match exactly in order
    assert len(result.tool_calls) == len(expected_tool_calls)
    for actual, expected in zip(result.tool_calls, expected_tool_calls):
        assert actual.tool_name == expected.tool_name
        assert isinstance(actual.params, dict)
        assert len(actual.params) > 0  # Just verify params exist and aren't empty

    # Verify timing and cost calculations
    assert result.runTimeMs > 0
    assert result.inputAndOutputCost >= 0


def test_openai_text_prompt():
    from modules.openai_llm import text_prompt

    response = text_prompt("ping", "gpt-4o")
    assert response.response != ""
    assert response.runTimeMs > 0
    assert response.inputAndOutputCost > 0.0


def test_openai_bench_prompt():
    from modules.openai_llm import bench_prompt

    response = bench_prompt("ping", "gpt-4o")
    assert response.response != ""
    assert response.total_duration_ms > 0
    # Check that cost is computed correctly (non-negative float)
    assert isinstance(response.inputAndOutputCost, float)
    assert response.inputAndOutputCost >= 0.0


@pytest.mark.parametrize(
    "model_input,expected_reasoning",
    [
        ("o3-mini:low", "low"),
        ("o3-mini:medium", "medium"),
        ("o3-mini:high", "high"),
        ("o3-mini", None),
    ],
)
def test_text_prompt_reasoning_effort(model_input, expected_reasoning):
    """
    Test that text_prompt works with real API calls and that our parsing works.
    """
    # Double-check the parsing outcome
    from utils import parse_reasoning_effort

    base_model, effective = parse_reasoning_effort(model_input)
    assert base_model == "o3-mini", "Base model should be 'o3-mini'"
    assert (
        effective == expected_reasoning
    ), f"Expected reasoning_effort to be {expected_reasoning}"

    # Do a real API call
    from modules.openai_llm import text_prompt

    response = text_prompt(
        "complete: method: def csvs_to_duckdb(csv_paths, duckdb_path)", model_input
    )

    # Validate the actual response received
    assert response.response != "", "Expected non-empty response"
    assert response.runTimeMs > 0, "Expected a positive runtime"
    assert response.inputAndOutputCost >= 0, "Expected non-negative cost"


def test_cost_ordering_group1():
    from modules.openai_llm import get_openai_cost

    input_tokens = 1000000
    output_tokens = 1000000
    cost_gpt4o_mini = get_openai_cost("gpt-4o-mini", input_tokens, output_tokens)
    cost_gpt4o = get_openai_cost("gpt-4o", input_tokens, output_tokens)
    cost_o1 = get_openai_cost("o1", input_tokens, output_tokens)
    cost_o1_preview = get_openai_cost("o1-preview", input_tokens, output_tokens)
    assert (
        cost_gpt4o_mini > 0.0
    ), f"cost_gpt4o_mini should be > 0.0, got {cost_gpt4o_mini}"
    assert cost_gpt4o > 0.0, f"cost_gpt4o should be > 0.0, got {cost_gpt4o}"
    assert cost_o1 > 0.0, f"cost_o1 should be > 0.0, got {cost_o1}"
    assert (
        cost_o1_preview > 0.0
    ), f"cost_o1_preview should be > 0.0, got {cost_o1_preview}"
    assert cost_gpt4o_mini < cost_gpt4o, f"{cost_gpt4o_mini} !< {cost_gpt4o}"
    assert cost_gpt4o < cost_o1, f"{cost_gpt4o} !< {cost_o1}"
    assert cost_o1 <= cost_o1_preview, f"{cost_o1} !<= {cost_o1_preview}"


def test_cost_ordering_group2():
    from modules.openai_llm import get_openai_cost

    input_tokens = 1000000
    output_tokens = 1000000
    cost_gpt4o_mini = get_openai_cost("gpt-4o-mini", input_tokens, output_tokens)
    cost_o1_mini = get_openai_cost("o1-mini", input_tokens, output_tokens)
    cost_o3_mini = get_openai_cost("o3-mini", input_tokens, output_tokens)
    cost_o1 = get_openai_cost("o1", input_tokens, output_tokens)
    assert (
        cost_gpt4o_mini > 0.0
    ), f"cost_gpt4o_mini should be > 0.0, got {cost_gpt4o_mini}"
    assert cost_o1_mini > 0.0, f"cost_o1_mini should be > 0.0, got {cost_o1_mini}"
    assert cost_o3_mini > 0.0, f"cost_o3_mini should be > 0.0, got {cost_o3_mini}"
    assert cost_o1 > 0.0, f"cost_o1 should be > 0.0, got {cost_o1}"
    assert cost_gpt4o_mini < cost_o1_mini, f"{cost_gpt4o_mini} !< {cost_o1_mini}"
    assert cost_o1_mini <= cost_o3_mini, f"{cost_o1_mini} !<= {cost_o3_mini}"
    assert cost_o3_mini < cost_o1, f"{cost_o3_mini} !< {cost_o1}"
