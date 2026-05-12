# ------------------------- Imports -------------------------
from typing import List, Optional
from datetime import datetime
from pathlib import Path
import time
from concurrent.futures import ThreadPoolExecutor
from modules.data_types import (
    ExecEvalBenchmarkFile,
    ExecEvalBenchmarkCompleteResult,
    ExeEvalBenchmarkOutputResult,
    ExecEvalBenchmarkModelReport,
    ExecEvalBenchmarkReport,
    ExecEvalPromptIteration,
    ModelAlias,
    ExeEvalType,
    ModelProvider,
    BenchPromptResponse,
)
from modules.ollama_llm import bench_prompt
from modules.execution_evaluators import (
    execute_python_code,
    eval_result_compare,
)
from utils import parse_markdown_backticks
from modules import (
    ollama_llm,
    anthropic_llm,
    deepseek_llm,
    gemini_llm,
    openai_llm,
    fireworks_llm,
)

provider_delimiter = "~"


def parse_model_string(model: str) -> tuple[str, str]:
    """
    Parse model string into provider and model name.
    Format: "provider:model_name" or "model_name" (defaults to ollama)

    Raises:
        ValueError: If provider is not supported
    """
    if provider_delimiter not in model:
        # Default to ollama if no provider specified
        return "ollama", model

    provider, *model_parts = model.split(provider_delimiter)
    model_name = provider_delimiter.join(model_parts)

    # Validate provider
    supported_providers = [
        "ollama",
        "anthropic",
        "deepseek",
        "openai",
        "gemini",
        "fireworks",
        # "mlx",
        # "groq",
    ]
    if provider not in supported_providers:
        raise ValueError(
            f"Unsupported provider: {provider}. "
            f"Supported providers are: {', '.join(supported_providers)}"
        )

    return provider, model_name


# ------------------------- File Operations -------------------------
def save_report_to_file(
    report: ExecEvalBenchmarkReport, output_dir: str = "reports"
) -> str:
    """Save benchmark report to file with standardized naming.

    Args:
        report: The benchmark report to save
        output_dir: Directory to save the report in

    Returns:
        Path to the saved report file
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(exist_ok=True)

    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_benchmark_name = report.benchmark_name.replace(" ", "_")
    report_filename = f"{output_dir}/{safe_benchmark_name}_{timestamp}.json"
    # Save report
    with open(report_filename, "w") as f:
        f.write(report.model_dump_json(indent=4))
    return report_filename


# ------------------------- Benchmark Execution -------------------------
provider_bench_functions = {
    "ollama": ollama_llm.bench_prompt,
    "anthropic": anthropic_llm.bench_prompt,
    "deepseek": deepseek_llm.bench_prompt,
    "openai": openai_llm.bench_prompt,
    "gemini": gemini_llm.bench_prompt,
    "fireworks": fireworks_llm.bench_prompt,
}


def process_single_prompt(
    prompt_row, benchmark_file, provider, model_name, index, total_tests
):
    print(f"  Running test {index}/{total_tests}...")

    prompt = benchmark_file.base_prompt
    if prompt_row.dynamic_variables:
        for key, value in prompt_row.dynamic_variables.items():
            prompt = prompt.replace(f"{{{{{key}}}}}", str(value))

    bench_response = None
    max_retries = 3
    delay = 1
    for attempt in range(max_retries + 1):
        try:
            bench_response = provider_bench_functions[provider](prompt, model_name)
            break
        except Exception as e:
            if attempt < max_retries:
                print(f"Retry {attempt+1} for test {index} due to error: {str(e)}")
                time.sleep(delay * (attempt + 1))
            else:
                print(f"All retries failed for test {index}")
                bench_response = BenchPromptResponse(
                    response=f"Error: {str(e)}",
                    tokens_per_second=0.0,
                    provider=provider,
                    total_duration_ms=0.0,
                    load_duration_ms=0.0,
                    errored=True,
                )

    backtick_parsed_response = parse_markdown_backticks(bench_response.response)
    execution_result = ""
    expected_result = str(prompt_row.expectation).strip()
    correct = False

    try:
        if benchmark_file.evaluator == ExeEvalType.execute_python_code_with_num_output:
            execution_result = execute_python_code(backtick_parsed_response)
            parsed_execution_result = str(execution_result).strip()
            correct = eval_result_compare(
                benchmark_file.evaluator, expected_result, parsed_execution_result
            )
        elif (
            benchmark_file.evaluator
            == ExeEvalType.execute_python_code_with_string_output
        ):
            execution_result = execute_python_code(backtick_parsed_response)

            correct = eval_result_compare(
                benchmark_file.evaluator, expected_result, execution_result
            )
        elif benchmark_file.evaluator == ExeEvalType.raw_string_evaluator:
            execution_result = backtick_parsed_response
            correct = eval_result_compare(
                benchmark_file.evaluator, expected_result, execution_result
            )
        elif benchmark_file.evaluator == "json_validator_eval":
            # For JSON validator, no code execution is needed;
            # use the response directly and compare the JSON objects.
            execution_result = backtick_parsed_response
            # expectation is assumed to be a dict (or JSON string convertible to dict)
            expected_result = prompt_row.expectation
            correct = eval_result_compare(
                "json_validator_eval", expected_result, execution_result
            )
        elif (
            benchmark_file.evaluator
            == ExeEvalType.python_print_execution_with_num_output
        ):
            wrapped_code = f"print({backtick_parsed_response})"
            execution_result = execute_python_code(wrapped_code)
            correct = eval_result_compare(
                ExeEvalType.execute_python_code_with_num_output,
                expected_result,
                execution_result.strip(),
            )
        else:
            raise ValueError(f"Unsupported evaluator: {benchmark_file.evaluator}")
    except Exception as e:
        print(f"Error executing code in test {index}: {e}")
        execution_result = str(e)
        correct = False

    return ExeEvalBenchmarkOutputResult(
        input_prompt=prompt,
        prompt_response=bench_response,
        execution_result=str(execution_result),
        expected_result=str(expected_result),
        model=f"{provider}{provider_delimiter}{model_name}",
        correct=correct,
        index=index,
    )


def run_benchmark_for_model(
    model: str, benchmark_file: ExecEvalBenchmarkFile
) -> List[ExeEvalBenchmarkOutputResult]:
    results = []
    total_tests = len(benchmark_file.prompts)

    try:
        provider, model_name = parse_model_string(model)
    except ValueError as e:
        print(f"Invalid model string {model}: {str(e)}")
        return []

    print(f"Running benchmark with provider: {provider}, model: {model_name}")

    if provider == "ollama":
        # Sequential processing for Ollama
        for i, prompt_row in enumerate(benchmark_file.prompts, 1):
            result = process_single_prompt(
                prompt_row, benchmark_file, provider, model_name, i, total_tests
            )
            results.append(result)
    else:
        # Parallel processing for other providers
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = []
            for i, prompt_row in enumerate(benchmark_file.prompts, 1):
                futures.append(
                    executor.submit(
                        process_single_prompt,
                        prompt_row,
                        benchmark_file,
                        provider,
                        model_name,
                        i,
                        total_tests,
                    )
                )

            for future in futures:
                results.append(future.result())

    return results


# ------------------------- Report Generation -------------------------
def generate_report(
    complete_result: ExecEvalBenchmarkCompleteResult,
) -> ExecEvalBenchmarkReport:
    model_reports = []

    # Group results by model
    model_results = {}
    for result in complete_result.results:
        if result.model not in model_results:
            model_results[result.model] = []
        model_results[result.model].append(result)

    # Create model reports
    for model, results in model_results.items():
        correct_count = sum(1 for r in results if r.correct)
        incorrect_count = len(results) - correct_count
        accuracy = correct_count / len(results)

        avg_tokens_per_second = sum(
            r.prompt_response.tokens_per_second for r in results
        ) / len(results)
        avg_total_duration = sum(
            r.prompt_response.total_duration_ms for r in results
        ) / len(results)
        avg_load_duration = sum(
            r.prompt_response.load_duration_ms for r in results
        ) / len(results)

        model_total_cost = 0

        try:
            model_total_cost = sum(
                (
                    r.prompt_response.inputAndOutputCost
                    if hasattr(r.prompt_response, "inputAndOutputCost")
                    else 0.0
                )
                for r in results
            )
        except:
            print(f"Error calculating model_total_cost for model: {model}")
            model_total_cost = 0

        model_reports.append(
            ExecEvalBenchmarkModelReport(
                model=model,
                results=results,
                correct_count=correct_count,
                incorrect_count=incorrect_count,
                accuracy=accuracy,
                average_tokens_per_second=avg_tokens_per_second,
                average_total_duration_ms=avg_total_duration,
                average_load_duration_ms=avg_load_duration,
                total_cost=model_total_cost,
            )
        )

    # Calculate overall statistics
    overall_correct = sum(r.correct_count for r in model_reports)
    overall_incorrect = sum(r.incorrect_count for r in model_reports)
    overall_accuracy = overall_correct / (overall_correct + overall_incorrect)

    avg_tokens_per_second = sum(
        r.average_tokens_per_second for r in model_reports
    ) / len(model_reports)
    avg_total_duration = sum(r.average_total_duration_ms for r in model_reports) / len(
        model_reports
    )
    avg_load_duration = sum(r.average_load_duration_ms for r in model_reports) / len(
        model_reports
    )

    return ExecEvalBenchmarkReport(
        benchmark_name=complete_result.benchmark_file.benchmark_name,
        purpose=complete_result.benchmark_file.purpose,
        base_prompt=complete_result.benchmark_file.base_prompt,
        prompt_iterations=[
            ExecEvalPromptIteration(
                dynamic_variables=(
                    prompt.dynamic_variables
                    if prompt.dynamic_variables is not None
                    else {}
                ),
                expectation=prompt.expectation,
            )
            for prompt in complete_result.benchmark_file.prompts
        ],
        models=model_reports,
        overall_correct_count=overall_correct,
        overall_incorrect_count=overall_incorrect,
        overall_accuracy=overall_accuracy,
        average_tokens_per_second=avg_tokens_per_second,
        average_total_duration_ms=avg_total_duration,
        average_load_duration_ms=avg_load_duration,
    )
