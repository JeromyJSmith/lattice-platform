from modules.tools import run_coder_agent, run_git_agent, run_docs_agent


def test_run_coder_agent():
    result = run_coder_agent("test prompt")
    assert isinstance(result, str)
    assert result == "run_coder_agent"


def test_run_git_agent():
    result = run_git_agent("test prompt")
    assert isinstance(result, str)
    assert result == "run_git_agent"


def test_run_docs_agent():
    result = run_docs_agent("test prompt")
    assert isinstance(result, str)
    assert result == "run_docs_agent"


