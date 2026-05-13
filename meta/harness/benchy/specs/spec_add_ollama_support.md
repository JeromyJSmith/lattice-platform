# Add ollama support
> Ingest the information from this file, implement the Low-Level Tasks, and generate the code that will satisfy the High and Mid-Level Objectives.

## High-Level Objective

- We're adding ollama support to our autocomplete live benchmarking tool

## Mid-Level Objective

- Add ollama support on the server
- Add ollama support on the client

## Implementation Notes
- Use the ollama library
- Add 'llama3.2:1b' as our first ollama model
- Mirror our other model providers

## Context

### Beginning context
- server/server.py
- server/modules/data_types.py
- server/modules/llm_models.py
- server/modules/ollama_llm.py
- server/tests/ollama_llm_test.py
- src/types.d.ts
- server/utils.py
- src/stores/autocompleteStore.ts

### Ending context  
- [List of files that will exist at end - what files will exist at end?]

## Low-Level Tasks
> Ordered from start to finish

1. Update types to add support for our new ollama model
```aider
UPDATE data_types.py:
    ADD 'llama3.2:1b' to ModelAlias

UPDATE types.d.ts:
    ADD 'llama3.2:1b' to ModelAlias

UPDATE server/utils.py:
    UPDATE MAP_MODEL_ALIAS_TO_COST_PER_MILLION_TOKENS 0, 0 cost entry for new 'llama3.2:1b'
```

2. Create the ollama_llm.py module
```aider
CREATE ollama_llm.py:
    
    CREATE def text_prompt(prompt: str, model: str) -> PromptResponse
        Use Code snippet as guide
            from ollama import chat
            from ollama import ChatResponse

            response: ChatResponse = chat(model='llama3.2', messages=[
            {
                'role': 'user',
                'content': 'Why is the sky blue?',
            },
            ])
            print(response['message']['content'])
            # or access fields directly from the response object
            print(response.message.content)

    CREATE def get_ollama_costs() -> instant return 0, 0 tuple ITS FREE!!!
```

3. Add tests for ollama_llm.py
```aider
UPDATE server/tests/ollama_llm_test.py
    create test for text_prompt(). 'ping' expect any response.
```

4. Add conditional logic to call ollama models in llm_models.py
```aider
UPDATE llm_models.py:
    UPDATE prompt() add support for calling ollama_llm.text_prompt if model in 'llama3.2:1b' ModelAlias
    UPDATE build_model_map() add an empty entry for 'llama...'
```

5. Add llama model support to the front end
```aider
UPDATE src/stores/autocompleteStore.ts:
    APPEND a rowData entry for the new 'llama3.2:1b' ModelAlias
```