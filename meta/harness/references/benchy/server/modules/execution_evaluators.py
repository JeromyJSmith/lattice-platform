import subprocess
from modules.data_types import ExeEvalType
import json
from deepdiff import DeepDiff


def eval_result_compare(evalType: ExeEvalType, expected: str, actual: str) -> bool:
    """
    Compare expected and actual results based on evaluation type.
    For numeric outputs, compare with a small epsilon tolerance.
    """
    try:
        if (
            evalType == ExeEvalType.execute_python_code_with_num_output
            or evalType == ExeEvalType.python_print_execution_with_num_output
        ):
            # Convert both values to float for numeric comparison
            expected_num = float(expected)
            actual_num = float(actual)
            epsilon = 1e-6
            return abs(expected_num - actual_num) < epsilon

        elif evalType == ExeEvalType.execute_python_code_with_string_output:
            return str(expected).strip() == str(actual).strip()

        elif evalType == ExeEvalType.raw_string_evaluator:
            return str(expected).strip() == str(actual).strip()

        elif evalType == ExeEvalType.json_validator_eval:

            if not isinstance(expected, dict):
                expected = json.loads(expected)
            actual_parsed = json.loads(actual) if isinstance(actual, str) else actual

            print(f"Expected: {expected}")
            print(f"Actual: {actual_parsed}")
            deepdiffed = DeepDiff(expected, actual_parsed, ignore_order=False)
            print(f"DeepDiff: {deepdiffed}")

            return not deepdiffed

        else:
            return str(expected).strip() == str(actual).strip()
    except (ValueError, TypeError):
        return str(expected).strip() == str(actual).strip()


def execute_python_code(code: str) -> str:
    """
    Execute Python code and return the numeric output as a string.
    """
    # Remove any surrounding quotes and whitespace
    code = code.strip().strip("'").strip('"')

    # Create a temporary file with the code
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=True) as tmp:
        tmp.write(code)
        tmp.flush()

        # Execute the temporary file using uv
        result = execute(f"uv run {tmp.name} --ignore-warnings")

        # Try to parse the result as a number
        try:
            # Remove any extra whitespace or newlines
            cleaned_result = result.strip()
            # Convert to float and back to string to normalize format
            return str(float(cleaned_result))
        except (ValueError, TypeError):
            # If conversion fails, return the raw result
            return result


def execute(code: str) -> str:
    """Execute the tests and return the output as a string."""
    try:
        result = subprocess.run(
            code.split(),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return f"Error: {result.stderr}"
        return result.stdout
    except Exception as e:
        return f"Execution error: {str(e)}"
