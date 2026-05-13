import typer
from typing import List
import yaml
from pathlib import Path
from datetime import datetime
import json
from modules.data_types import (
    ExecEvalBenchmarkFile,
    ExecEvalBenchmarkCompleteResult,
)
from modules.exbench_module import (
    run_benchmark_for_model, 
    generate_report, 
    save_report_to_file
)

app = typer.Typer()


@app.command()
def ping():
    typer.echo("pong")


@app.command()
def ollama_bench(
    yaml_file: str = typer.Argument(
        ..., help="Path to YAML benchmark configuration file"
    ),
    output_dir: str = typer.Option(
        "reports",
        "--output-dir",
        "-o",
        help="Directory to save benchmark reports",
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        resolve_path=True,
    ),
    count: int = typer.Option(
        None,
        "--count",
        "-c",
        help="Limit the number of tests to run from the YAML file",
        min=1,
    ),
):
    """
    Run benchmarks on Ollama models using a YAML configuration file.

    Example usage:

    uv run python exbench.py ollama-bench benchmark_data/simple_math.yaml -c 5
    """
    # Load and validate YAML file
    try:
        with open(yaml_file) as f:
            yaml_data = yaml.safe_load(f)

        # If YAML is a list, convert to dict with default structure
        if isinstance(yaml_data, list):
            yaml_data = {
                "base_prompt": "",
                "evaluator": "execute_python_code_with_uv",
                "prompts": yaml_data,
                "benchmark_name": "unnamed_benchmark",
                "purpose": "No purpose specified",
                "models": [],  # Default empty models list
                "model_provider": "ollama",  # Default to ollama
            }

        # Ensure prompts have the correct structure
        if "prompts" in yaml_data:
            for prompt in yaml_data["prompts"]:
                if not isinstance(prompt, dict):
                    prompt = {"dynamic_variables": {}, "expectation": str(prompt)}
                if "dynamic_variables" not in prompt:
                    prompt["dynamic_variables"] = {}
                if "expectation" not in prompt:
                    prompt["expectation"] = ""

        benchmark_file = ExecEvalBenchmarkFile(**yaml_data)
    except Exception as e:
        typer.echo(f"Error loading YAML file: {e}")
        raise typer.Exit(code=1)

    # Limit number of prompts if count is specified
    if count is not None:
        benchmark_file.prompts = benchmark_file.prompts[:count]
        typer.echo(f"Limiting to first {count} tests")

    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(exist_ok=True)

    # Run benchmarks
    complete_result = ExecEvalBenchmarkCompleteResult(
        benchmark_file=benchmark_file, results=[]
    )

    for model in benchmark_file.models:
        typer.echo(f"\nRunning benchmarks for model: {model}")
        total_tests = len(benchmark_file.prompts)

        # Run all prompts for this model at once
        results = run_benchmark_for_model(model, benchmark_file)
        complete_result.results.extend(results)

        typer.echo(f"Completed benchmarks for model: {model}\n")

    # Generate and save report using the new function
    report = generate_report(complete_result)
    report_path = save_report_to_file(report, output_dir)
    
    typer.echo(f"Benchmark report saved to: {report_path}")


if __name__ == "__main__":
    app()
