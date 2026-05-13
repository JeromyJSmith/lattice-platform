def run_coder_agent(prompt: str) -> str:
    """
    Run the coder agent with the given prompt.

    Args:
        prompt (str): The input prompt for the coder agent

    Returns:
        str: The response from the coder agent
    """
    return "run_coder_agent"


def run_git_agent(prompt: str) -> str:
    """
    Run the git agent with the given prompt.

    Args:
        prompt (str): The input prompt for the git agent

    Returns:
        str: The response from the git agent
    """
    return "run_git_agent"


def run_docs_agent(prompt: str) -> str:
    """
    Run the docs agent with the given prompt.

    Args:
        prompt (str): The input prompt for the docs agent

    Returns:
        str: The response from the docs agent
    """
    return "run_docs_agent"


# Gemini tools list
gemini_tools_list = [
    {
        "function_declarations": [
            {
                "name": "run_coder_agent",
                "description": "Run the coding agent with the given prompt. Use this when the user needs help writing, reviewing, or modifying code.",
                "parameters": {
                    "type_": "OBJECT",
                    "properties": {
                        "prompt": {
                            "type_": "STRING",
                            "description": "The input prompt that describes what to code for the coder agent"
                        }
                    },
                    "required": ["prompt"]
                }
            },
            {
                "name": "run_git_agent",
                "description": "Run the git agent with the given prompt. Use this when the user needs help with git operations, commits, or repository management.",
                "parameters": {
                    "type_": "OBJECT", 
                    "properties": {
                        "prompt": {
                            "type_": "STRING",
                            "description": "The input prompt that describes what to commit for the git agent"
                        }
                    },
                    "required": ["prompt"]
                }
            },
            {
                "name": "run_docs_agent",
                "description": "Run the documentation agent with the given prompt. Use this when the user needs help creating, updating, or reviewing documentation.",
                "parameters": {
                    "type_": "OBJECT",
                    "properties": {
                        "prompt": {
                            "type_": "STRING",
                            "description": "The input prompt that describes what to document for the documentation agent"
                        }
                    },
                    "required": ["prompt"]
                }
            }
        ]
    }
]

# OpenAI tools list
openai_tools_list = [
    {
        "type": "function",
        "function": {
            "name": "run_coder_agent",
            "description": "Run the coding agent with the given prompt",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The input prompt that describes what to code for the coder agent",
                    }
                },
                "required": ["prompt"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_git_agent",
            "description": "Run the git agent with the given prompt",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The input prompt that describes what to commit for the git agent",
                    }
                },
                "required": ["prompt"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_docs_agent",
            "description": "Run the documentation agent with the given prompt",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The input prompt that describes what to document for the documentation agent",
                    }
                },
                "required": ["prompt"],
            },
        },
    },
]

anthropic_tools_list = [
    {
        "name": "run_coder_agent",
        "description": "Run the coding agent with the given prompt",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The input prompt that describes what to code for the coder agent",
                }
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "run_git_agent", 
        "description": "Run the git agent with the given prompt",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The input prompt that describes what to commit for the git agent",
                }
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "run_docs_agent",
        "description": "Run the documentation agent with the given prompt",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The input prompt that describes what to document for the documentation agent",
                }
            },
            "required": ["prompt"]
        }
    }
]

all_tools_list = [d["function"]["name"] for d in openai_tools_list]
