# Build a simple python based benchmarking tool on ollama models
> Ingest the information from this file, implement the Low-Level Tasks, and generate the code that will satisfy the High and Mid-Level Objectives.

## High-Level Objective

- We're building 'Execution Evaluator Benchmarking Tool' to test the performance of local models.
  - We're specifically looking at tokens per second, correctness (pass/fail) and total duration.

## Mid-Level Objective

- Update exbench.py to include a new command `ollama-bench <model1> <model2> <model3> <modelN> <prompt config yaml file path>`
  - This command will pull in a `ExecEvalBenchmarkFile` from the yaml file and run the benchmarks iteratively building up `ExecEvalBenchmarkCompleteResult`.
  - Output the results to a file in the `reports/*` directory with a unique name based on the prompt config benchmark_name and a human readable timestamp.

## Implementation Notes
- The flow is: pull in file, run prompts, execute code for each model based on their evaluator type (right now only `execute_python_code_with_uv` is supported), then compare the output to the expected output (stringify), then store results and write to output file.
- Pay close attention to the `data_types.py` as it contains the data structures for the input and output of the benchmark.

## Context
/drop
/add       server/data/simple_math.yaml
/add       server/exbench.py
/add       server/modules/data_types.py
/add       server/modules/execution_evaluators.py
/add       server/modules/ollama_llm.py
/add       server/utils.py


## Low-Level Tasks
> Ordered from start to finish

0. Create a new typer command `ollama-bench` that will take in a list of models and a yaml file path.
1. Pull in yaml file and use Pydantic to validate the data structure into `ExecEvalBenchmarkFile`.
2. Create a new `ExecEvalBenchmarkCompleteResult` object.
3. Iterate over each `ExecEvalBenchmarkFile.ExeEvalBenchmarkInputRow`, replace the `dynamic_variables` where the key of each should be replaced with {{key}} in the `ExecEvalBenchmarkFile.base_prompt` then call `bench_prompt` on each replaced prompt with for each model passed in.
4. Now that we have results, we need to clean it with `parse_markdown_backticks` then we need to execute the prompt response based on the `ExeEvalBenchmarkFile.evaluator` type (right now only `execute_python_code_with_uv` is supported)
5. After we execute we create a new `ExeEvalBenchmarkOutputResult` object and store the results in the `ExecEvalBenchmarkCompleteResult` object.
6. When every ExecEvalBenchmarkFile.prompts per model has been processed, we write the results to a file in the `reports/*` directory with a unique name based on the prompt config benchmark_name and a human readable timestamp. Be sure to give a total summary of the results for all models. and then a break down for each model. we're looking for tokens per second, correctness (pass/fail) and total duration for each model. Fill out a ExecEvalBenchmarkModelReport per model then combine it into a ExecEvalBenchmarkReport which we'll then write to a file in the `reports/*` directory with a unique name based on the prompt config benchmark_name and a human readable timestamp.