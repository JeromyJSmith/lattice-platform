import pytest
from modules.fireworks_llm import bench_prompt, text_prompt, thought_prompt


@pytest.fixture
def model():
    return "accounts/fireworks/models/llama-v3p2-3b-instruct"


def test_bench_prompt(model):
    prompt = "Hello, how are you?"
    response = bench_prompt(prompt, model)
    assert response is not None
    assert response.response
    print("bench_prompt response:", response.response)


def test_text_prompt(model):
    prompt = "Hello"
    response = text_prompt(prompt, model)
    assert response is not None
    assert response.response
    print("text_prompt response:", response.response)


def test_thought_prompt():
    model = "accounts/fireworks/models/deepseek-r1"
    prompt = "Hello. sum these numbers 1, 2, 3, 4, 5"
    response = thought_prompt(prompt, model)
    assert response is not None
    assert response.response
    assert response.thoughts
    print("thought_prompt response:", response.response)
    print("thought_prompt thoughts:", response.thoughts)
