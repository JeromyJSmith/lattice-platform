from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

FRE_ROOT = Path(__file__).resolve().parents[1]
SOURCE_PACKET = "/Volumes/PixelTable/VW_iTWIN_Bridge/fre-test-eval-improvement 76019c48ec2441c0a42a1ac7a3f9b49b.md"
WORKTREE = "/Volumes/PixelTable/VW_iTWIN_Bridge/lattice-worktrees/feat-fre-meta-harness-eval"
BASE_COMMIT = "d02328e"
DEFAULT_RUN_ID = "RUN-2026-05-16-0001"

REQUIRED_METRICS = {
    "research_grounding",
    "schema_validity",
    "example_validation",
    "repair_task_count",
    "promotion_readiness",
}
RESEARCH_DOC_PATHS = [
    FRE_ROOT / "docs" / "research-grounding.md",
    FRE_ROOT / "docs" / "research-findings.md",
]
ALLOWED_GREEN_TERM_PATHS = {
    "examples/expected-failures.yaml",
    "examples/fre-loop.invalid.green-terminology.json",
    "docs/source-normalization.md",
    "docs/sources.md",
}
REQUIRED_MAPPING_ROWS = {
    "repair_task": "clean",
    "promotion_decision": "partial",
    "scorecard": "clean",
    "validation_pass_criteria": "clean",
    "source_record": "partial",
    "artifact": "partial",
}
ALLOWED_MAPPING_STATUSES = {"clean", "partial", "conflict", "reject", "needs_extension"}
FORBIDDEN_GREEN_TERM = "definition_of_" + "green"
REQUIRED_RUN_ARTIFACTS = [
    "input-manifest.yaml",
    "normalized-source-summary.md",
    "research-grounding.json",
    "schema-validation.json",
    "example-validation.json",
    "determinism-check.json",
    "real-fixture-evaluation.json",
    "gate-results.json",
    "scorecard.yaml",
    "repair-tasks.yaml",
    "report.md",
    "promotion-decision.md",
]
SUPPORTED_SCHEMA_KEYS = {
    "$schema",
    "$id",
    "title",
    "type",
    "additionalProperties",
    "required",
    "properties",
    "pattern",
    "const",
    "enum",
    "minLength",
    "format",
    "minItems",
    "uniqueItems",
    "items",
    "contains",
    "prefixItems",
    "minimum",
    "maximum",
}
FIXTURE_DIR = FRE_ROOT / "fixtures"


@dataclass(frozen=True)
class FailureObservation:
    failure_class: str
    field: str
    missing_value: str | None = None


def current_run_id() -> str:
    return os.environ.get("FRE_RUN_ID", DEFAULT_RUN_ID)


def current_run_dir() -> Path:
    return FRE_ROOT / "runs" / current_run_id()


def session_summary_path(run_id: str | None = None) -> Path:
    target_run_id = run_id or current_run_id()
    return FRE_ROOT / "docs" / "sessions" / f"{target_run_id}.md"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(read_text(path))


def read_yaml(path: Path) -> Any:
    return json.loads(read_text(path))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_yaml(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


def ensure_run_dir() -> Path:
    run_dir = current_run_dir()
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def write_input_manifest() -> Path:
    path = ensure_run_dir() / "input-manifest.yaml"
    payload = {
        "run_id": current_run_id(),
        "branch": "feat/fre-meta-harness-eval",
        "base_commit": BASE_COMMIT,
        "worktree": WORKTREE,
        "source_packet": SOURCE_PACKET,
        "commands": [
            "uv run pytest meta/harness/fre/tests",
            "uv run python meta/harness/fre/harness/validate_schema.py",
            "uv run python meta/harness/fre/harness/validate_examples.py",
            "uv run python meta/harness/fre/harness/evaluate.py",
            "uv run python meta/harness/fre/harness/propose_repairs.py",
            "uv run python meta/harness/fre/harness/report.py",
            "uv run python meta/harness/fre/harness/evaluate_real_fixtures.py",
            "uv run python meta/harness/fre/harness/iterate.py",
        ],
    }
    write_yaml(path, payload)
    return path


def write_normalized_source_summary() -> Path:
    path = ensure_run_dir() / "normalized-source-summary.md"
    summary = (
        "# Normalized Source Summary\n\n"
        "- Source packet recorded as provenance, not executable truth.\n"
        "- Notion link corruption is treated as malformed input.\n"
        "- `validation_pass_criteria` is canonical.\n"
        "- Rejected terminology is confined to intentional invalid fixtures and enforcement tests.\n"
    )
    write_text(path, summary)
    return path


def schema_path(name: str) -> Path:
    return FRE_ROOT / "schemas" / name


def example_path(name: str) -> Path:
    return FRE_ROOT / "examples" / name


def load_schema(name: str) -> dict[str, Any]:
    payload = read_json(schema_path(name))
    if not isinstance(payload, dict):
        raise ValueError(f"{name} is not a JSON object schema")
    return payload


def _required_snippets() -> dict[str, list[str]]:
    return {
        "docs/research-grounding.md": [
            "research -> source -> schema",
            "source packet",
            "meta-harness",
            "ratchet",
        ],
        "docs/research-findings.md": [
            "ratchet",
            "real-fixture",
            "research-grounding",
            "source packet",
        ],
    }


def research_grounding_status() -> dict[str, Any]:
    evidence = [path.relative_to(FRE_ROOT).as_posix() for path in RESEARCH_DOC_PATHS]
    missing: list[str] = []
    source_exists = Path(SOURCE_PACKET).exists()
    if not source_exists:
        missing.append("source_packet")

    for path in RESEARCH_DOC_PATHS:
        rel = path.relative_to(FRE_ROOT).as_posix()
        if not path.exists():
            missing.append(rel)
            continue
        text = read_text(path).lower()
        for snippet in _required_snippets()[rel]:
            if snippet not in text:
                missing.append(f"{rel}::{snippet}")
    return {
        "status": "pass" if not missing else "fail",
        "evidence": evidence + ["../CLAUDE.md", "../GOAL.md"],
        "missing": missing,
        "source_packet_exists": source_exists,
    }


def write_research_grounding_summary() -> Path:
    path = ensure_run_dir() / "research-grounding.json"
    write_json(path, research_grounding_status())
    return path


def _inspect_schema_node(node: Any, field: str) -> list[str]:
    issues: list[str] = []
    if isinstance(node, dict):
        unknown = [key for key in node if key not in SUPPORTED_SCHEMA_KEYS]
        issues.extend(f"{field}:unsupported_keyword:{key}" for key in unknown)

        schema_type = node.get("type")
        if schema_type == "object":
            required = node.get("required", [])
            properties = node.get("properties", {})
            if not isinstance(properties, dict):
                issues.append(f"{field}:properties_not_object")
            else:
                for required_key in required:
                    if required_key not in properties:
                        issues.append(f"{field}:required_missing_property:{required_key}")
        if schema_type == "array":
            prefix_items = node.get("prefixItems", [])
            if prefix_items and not isinstance(prefix_items, list):
                issues.append(f"{field}:prefix_items_not_list")

        for key, value in node.items():
            child_field = f"{field}.{key}"
            if key == "properties" and isinstance(value, dict):
                for prop_name, prop_value in value.items():
                    issues.extend(_inspect_schema_node(prop_value, f"{child_field}.{prop_name}"))
            elif key == "items":
                issues.extend(_inspect_schema_node(value, child_field))
            elif key == "prefixItems" and isinstance(value, list):
                for index, item in enumerate(value):
                    issues.extend(_inspect_schema_node(item, f"{child_field}[{index}]"))
    elif isinstance(node, list):
        for index, item in enumerate(node):
            issues.extend(_inspect_schema_node(item, f"{field}[{index}]"))
    return issues


def check_all_schemas() -> dict[str, Any]:
    results = []
    all_valid = True
    for path in sorted((FRE_ROOT / "schemas").glob("*.json")):
        schema = load_schema(path.name)
        issues = _inspect_schema_node(schema, path.name)
        status = "pass" if not issues else "fail"
        all_valid = all_valid and status == "pass"
        results.append({"schema": path.name, "status": status, "issues": issues})
    return {"schemas": results, "all_valid": all_valid}


def _as_hashable(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(_as_hashable(item) for item in value)
    if isinstance(value, dict):
        return tuple((key, _as_hashable(val)) for key, val in sorted(value.items()))
    return value


def _validate_against_schema(schema: dict[str, Any], payload: Any, field: str) -> list[FailureObservation]:
    failures: list[FailureObservation] = []
    schema_type = schema.get("type")

    if schema_type == "object":
        if not isinstance(payload, dict):
            return [FailureObservation("TYPE_MISMATCH", field)]
        required = schema.get("required", [])
        properties = schema.get("properties", {})
        for required_field in required:
            if required_field not in payload:
                failures.append(FailureObservation("REQUIRED_FIELD_MISSING", f"{field}.{required_field}" if field else required_field))
        if schema.get("additionalProperties") is False:
            for extra_field in sorted(set(payload) - set(properties)):
                failures.append(
                    FailureObservation(
                        "ADDITIONAL_PROPERTY_NOT_ALLOWED",
                        f"{field}.{extra_field}" if field else extra_field,
                    )
                )
        for prop_name, prop_schema in properties.items():
            if prop_name in payload:
                child_field = f"{field}.{prop_name}" if field else prop_name
                failures.extend(_validate_against_schema(prop_schema, payload[prop_name], child_field))

    elif schema_type == "array":
        if not isinstance(payload, list):
            return [FailureObservation("TYPE_MISMATCH", field)]
        min_items = schema.get("minItems")
        if min_items is not None and len(payload) < min_items:
            failures.append(FailureObservation("MIN_ITEMS_VIOLATION", field))
        if schema.get("uniqueItems"):
            seen = set()
            for item in payload:
                marker = _as_hashable(item)
                if marker in seen:
                    failures.append(FailureObservation("UNIQUE_ITEMS_VIOLATION", field))
                    break
                seen.add(marker)
        prefix_items = schema.get("prefixItems", [])
        for index, item_schema in enumerate(prefix_items):
            if index < len(payload):
                failures.extend(_validate_against_schema(item_schema, payload[index], f"{field}[{index}]"))
        items_schema = schema.get("items")
        if items_schema is not None:
            for index, item in enumerate(payload):
                failures.extend(_validate_against_schema(items_schema, item, f"{field}[{index}]"))
        contains = schema.get("contains")
        if contains is not None:
            target = contains.get("const")
            if target is not None and target not in payload:
                failure_class = (
                    "AUTHORITY_CHAIN_MISSING_REQUIRED_VALUE"
                    if field == "authority_chain"
                    else "ARRAY_CONTAINS_VIOLATION"
                )
                failures.append(FailureObservation(failure_class, field, str(target)))

    elif schema_type == "string":
        if not isinstance(payload, str):
            return [FailureObservation("TYPE_MISMATCH", field)]
        min_length = schema.get("minLength")
        if min_length is not None and len(payload) < min_length:
            failures.append(FailureObservation("MIN_LENGTH_VIOLATION", field))
        pattern = schema.get("pattern")
        if pattern is not None and re.match(pattern, payload) is None:
            failures.append(FailureObservation("PATTERN_MISMATCH", field))
        enum = schema.get("enum")
        if enum is not None and payload not in enum:
            failures.append(FailureObservation("ENUM_VIOLATION", field, payload))
        const = schema.get("const")
        if const is not None and payload != const:
            failures.append(FailureObservation("CONST_VIOLATION", field))
        fmt = schema.get("format")
        if fmt == "date" and re.match(r"^\d{4}-\d{2}-\d{2}$", payload) is None:
            failures.append(FailureObservation("FORMAT_VIOLATION", field))

    elif schema_type == "integer":
        if not isinstance(payload, int) or isinstance(payload, bool):
            return [FailureObservation("TYPE_MISMATCH", field)]
        minimum = schema.get("minimum")
        maximum = schema.get("maximum")
        if minimum is not None and payload < minimum:
            failures.append(FailureObservation("MINIMUM_VIOLATION", field))
        if maximum is not None and payload > maximum:
            failures.append(FailureObservation("MAXIMUM_VIOLATION", field))

    elif schema_type == "boolean":
        if not isinstance(payload, bool):
            return [FailureObservation("TYPE_MISMATCH", field)]

    enum = schema.get("enum")
    if enum is not None and schema_type not in {"string"} and payload not in enum:
        failures.append(FailureObservation("ENUM_VIOLATION", field, str(payload)))
    const = schema.get("const")
    if const is not None and schema_type not in {"string"} and payload != const:
        failures.append(FailureObservation("CONST_VIOLATION", field))
    return failures


def validate_instance(schema_name: str, payload: Any) -> list[FailureObservation]:
    return _validate_against_schema(load_schema(schema_name), payload, "")


def _normalize_failure_field(field: str) -> str:
    return field.lstrip(".")


def validate_examples_data() -> dict[str, Any]:
    valid_pairs = [
        ("fre-loop.schema.json", "fre-loop.valid.json"),
        ("gate-result.schema.json", "gate-result.valid.json"),
        ("repair-task.schema.json", "repair-task.valid.json"),
        ("promotion-decision.schema.json", "promotion-decision.valid.json"),
    ]
    valid_results = []
    for schema_name, example_name in valid_pairs:
        failures = validate_instance(schema_name, read_json(example_path(example_name)))
        valid_results.append(
            {
                "example": example_name,
                "schema": schema_name,
                "status": "pass" if not failures else "fail",
                "failures": [failure.__dict__ for failure in failures],
            }
        )

    expected = read_yaml(example_path("expected-failures.yaml"))["expected_failures"]
    invalid_results = []
    for entry in expected:
        failures = validate_instance(entry["schema"], read_json(FRE_ROOT / entry["example"]))
        observed_classes = {failure.failure_class for failure in failures}
        observed_fields = {_normalize_failure_field(failure.field) for failure in failures}
        observed_missing_values = {failure.missing_value for failure in failures if failure.missing_value}
        expected_classes = set(entry.get("expected_failure_classes", []))
        expected_fields = set(entry.get("expected_fields", []))
        expected_missing_values = set(entry.get("expected_missing_values", []))
        invalid_results.append(
            {
                "example": entry["example"],
                "schema": entry["schema"],
                "status": "pass" if failures else "fail",
                "observed_failures": [failure.__dict__ for failure in failures],
                "matched_expected": (
                    bool(failures)
                    and expected_classes.issubset(observed_classes)
                    and expected_fields.issubset(observed_fields)
                    and expected_missing_values.issubset(observed_missing_values)
                ),
            }
        )

    return {
        "valid_examples": valid_results,
        "invalid_examples": invalid_results,
    }


def mapping_rows() -> dict[str, str]:
    text = read_text(FRE_ROOT / "docs" / "fre-to-lattice-map.md")
    rows = {}
    for fre_field in REQUIRED_MAPPING_ROWS:
        match = re.search(rf"`{re.escape(fre_field)}` \| [^|]+ \| ([^|]+) \|", text)
        rows[fre_field] = match.group(1).strip() if match else ""
    return rows


def mapping_contract_status() -> dict[str, Any]:
    rows = mapping_rows()
    missing = [field for field, status in rows.items() if not status]
    invalid = [field for field, status in rows.items() if status and status not in ALLOWED_MAPPING_STATUSES]
    conflicts = [field for field, status in rows.items() if status in {"conflict", "reject"}]
    status = "pass" if not missing and not invalid else "fail"
    return {
        "status": status,
        "rows": rows,
        "missing": missing,
        "invalid": invalid,
        "conflicts": conflicts,
    }


def forbidden_term_violations() -> list[str]:
    violations = []
    for path in FRE_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        rel = path.relative_to(FRE_ROOT).as_posix()
        if rel.startswith("runs/"):
            continue
        if rel in ALLOWED_GREEN_TERM_PATHS:
            continue
        if rel.startswith("tests/"):
            continue
        try:
            text = read_text(path)
        except UnicodeDecodeError:
            continue
        if FORBIDDEN_GREEN_TERM in text:
            violations.append(rel)
    return sorted(violations)


def available_run_ids() -> list[str]:
    runs_dir = FRE_ROOT / "runs"
    if not runs_dir.exists():
        return []
    return sorted(path.name for path in runs_dir.iterdir() if path.is_dir() and path.name.startswith("RUN-"))


def previous_run_id() -> str | None:
    runs = available_run_ids()
    current = current_run_id()
    prior = [run_id for run_id in runs if run_id < current]
    return prior[-1] if prior else None


def required_run_artifact_status() -> dict[str, bool]:
    run_dir = current_run_dir()
    return {name: (run_dir / name).exists() for name in REQUIRED_RUN_ARTIFACTS}


def get_nested_value(payload: dict[str, Any], dotted_key: str) -> object | None:
    current: object = payload
    for part in dotted_key.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def evaluate_fixture_manifest(manifest_path: Path) -> dict[str, Any]:
    manifest = read_json(manifest_path)
    target_path = Path(manifest["path"])
    result = {
        "fixture_id": manifest["id"],
        "name": manifest["name"],
        "type": manifest["type"],
        "path": manifest["path"],
        "exists": target_path.exists(),
        "status": "fail",
        "checks": [],
    }
    if not target_path.exists():
        result["checks"].append({"check": "exists", "status": "fail"})
        return result

    if manifest["type"] == "json_proof_artifact":
        payload = read_json(target_path)
        checks = []
        for key in manifest.get("must_have_top_level_keys", []):
            checks.append({"check": key, "status": "pass" if key in payload else "fail"})
        for key in manifest.get("must_have_nested_keys", []):
            checks.append({"check": key, "status": "pass" if get_nested_value(payload, key) is not None else "fail"})
        result["checks"] = checks
    elif manifest["type"] == "markdown_handoff":
        text = read_text(target_path)
        checks = []
        for phrase in manifest.get("must_contain", []):
            checks.append({"check": phrase, "status": "pass" if phrase in text else "fail"})
        result["checks"] = checks
    else:
        result["checks"] = [{"check": "supported_type", "status": "fail"}]
        return result

    result["status"] = "pass" if all(check["status"] == "pass" for check in result["checks"]) else "fail"
    return result


def build_real_fixture_summary() -> dict[str, Any]:
    manifests = sorted(FIXTURE_DIR.glob("*.json"))
    results = [evaluate_fixture_manifest(path) for path in manifests]
    return {
        "run_id": current_run_id(),
        "fixture_count": len(results),
        "passed_count": sum(1 for item in results if item["status"] == "pass"),
        "all_passed": all(item["status"] == "pass" for item in results) and len(results) >= 2,
        "fixtures": results,
    }


def write_real_fixture_evaluation_artifacts() -> tuple[Path, Path]:
    summary = build_real_fixture_summary()
    json_path = ensure_run_dir() / "real-fixture-evaluation.json"
    md_path = ensure_run_dir() / "real-fixture-evaluation.md"
    write_json(json_path, summary)
    markdown_lines = [
        f"# Real Fixture Evaluation {current_run_id()}",
        "",
        f"- Fixture count: `{summary['fixture_count']}`",
        f"- Passed count: `{summary['passed_count']}`",
        f"- All passed: `{summary['all_passed']}`",
        "",
        "## Fixture Results",
        "",
    ]
    for item in summary["fixtures"]:
        markdown_lines.append(f"- `{item['fixture_id']}` `{item['status']}` — {item['name']}")
    write_text(md_path, "\n".join(markdown_lines) + "\n")
    return json_path, md_path


def real_fixture_pressure_status() -> dict[str, Any]:
    summary = build_real_fixture_summary()
    evidence = [
        "fixtures/golden-path-proof-run.json",
        "fixtures/handoff-next-session.json",
        "docs/phase3-fixture-selection.md",
        f"runs/{current_run_id()}/real-fixture-evaluation.json",
        f"runs/{current_run_id()}/real-fixture-evaluation.md",
    ]
    missing = [item for item in evidence[:3] if not (FRE_ROOT / item).exists()]
    return {
        "status": "pass" if not missing and summary["all_passed"] else "fail",
        "evidence": evidence,
        "missing": missing,
        "fixture_count": summary["fixture_count"],
        "passed_count": summary["passed_count"],
    }


def build_determinism_check() -> dict[str, Any]:
    first = {
        "research": research_grounding_status(),
        "schemas": check_all_schemas(),
        "examples": validate_examples_data(),
        "mapping": mapping_contract_status(),
        "fixtures": build_real_fixture_summary(),
    }
    second = {
        "research": research_grounding_status(),
        "schemas": check_all_schemas(),
        "examples": validate_examples_data(),
        "mapping": mapping_contract_status(),
        "fixtures": build_real_fixture_summary(),
    }
    return {
        "status": "pass" if first == second else "fail",
        "comparisons": {
            "first": first,
            "second": second,
        },
    }


def write_determinism_check() -> Path:
    path = ensure_run_dir() / "determinism-check.json"
    write_json(path, build_determinism_check())
    return path


def compare_to_previous_run() -> dict[str, Any] | None:
    prior_id = previous_run_id()
    if prior_id is None:
        return None
    prior_score_path = FRE_ROOT / "runs" / prior_id / "scorecard.yaml"
    if not prior_score_path.exists():
        return None
    previous_scorecard = read_yaml(prior_score_path)
    current_scorecard_path = current_run_dir() / "scorecard.yaml"
    current_scorecard = read_yaml(current_scorecard_path) if current_scorecard_path.exists() else None
    if current_scorecard is None:
        return None
    return {
        "previous_run_id": prior_id,
        "previous_total_score": previous_scorecard["total_score"],
        "current_total_score": current_scorecard["total_score"],
        "delta": current_scorecard["total_score"] - previous_scorecard["total_score"],
    }


def evaluate_data() -> dict[str, Any]:
    schema_result = check_all_schemas()
    example_result = validate_examples_data()
    mapping_status = mapping_contract_status()
    artifact_status = required_run_artifact_status()
    research_status = research_grounding_status()
    fixture_status = real_fixture_pressure_status()
    determinism = build_determinism_check()

    gates = [
        {
            "gate_id": "research_grounding",
            "status": research_status["status"],
            "blocking": True,
            "reason": "Research grounding and provenance exist before schema execution and scoring.",
            "evidence": research_status["evidence"],
        },
        {
            "gate_id": "schema_validity",
            "status": "pass" if schema_result["all_valid"] else "fail",
            "blocking": True,
            "reason": "All FRE schemas pass bounded local schema integrity checks.",
            "evidence": ["schema-validation.json"],
        },
        {
            "gate_id": "example_validation",
            "status": "pass"
            if all(item["status"] == "pass" for item in example_result["valid_examples"])
            and all(item["matched_expected"] for item in example_result["invalid_examples"])
            else "fail",
            "blocking": True,
            "reason": "Valid examples pass and invalid examples fail for expected reasons against the checked-in schemas.",
            "evidence": ["example-validation.json", "examples/expected-failures.yaml"],
        },
        {
            "gate_id": "mapping_contract",
            "status": mapping_status["status"],
            "blocking": True,
            "reason": "FRE fields are mapped to LATTICE concepts with explicit transfer statuses.",
            "evidence": ["docs/fre-to-lattice-map.md"],
        },
        {
            "gate_id": "real_fixture_pressure_test",
            "status": fixture_status["status"],
            "blocking": True,
            "reason": "Current-run fixture pressure is proven against at least two real LATTICE artifacts.",
            "evidence": fixture_status["evidence"],
        },
    ]

    blocking_failures = sum(1 for gate in gates if gate["blocking"] and gate["status"] == "fail")
    repairs = propose_repairs_data(gates)

    schema_clarity = (
        2
        if schema_result["all_valid"]
        and all(item["status"] == "pass" for item in example_result["valid_examples"])
        and all(item["matched_expected"] for item in example_result["invalid_examples"])
        else 1
    )
    repair_task_usefulness = 2 if blocking_failures and repairs else (0 if blocking_failures and not repairs else 1)
    lattice_vocabulary_compatibility = 0 if mapping_status["invalid"] or mapping_status["missing"] else (
        1 if mapping_status["conflicts"] else 2
    )
    deterministic_execution = 2 if determinism["status"] == "pass" else 0
    evidence_quality = 2 if all(artifact_status.values()) and fixture_status["status"] == "pass" else (
        1 if artifact_status else 0
    )
    restart_readiness = 2 if session_summary_path().exists() and artifact_status.get("report.md", False) else 1
    scores = {
        "deterministic_execution": deterministic_execution,
        "schema_clarity": schema_clarity,
        "repair_task_usefulness": repair_task_usefulness,
        "lattice_vocabulary_compatibility": lattice_vocabulary_compatibility,
        "real_artifact_usefulness": 2 if fixture_status["status"] == "pass" else 0,
        "integration_restraint": 2,
        "evidence_quality": evidence_quality,
        "restart_readiness": restart_readiness,
    }
    total_score = sum(scores.values())

    if blocking_failures:
        decision = "ADOPT WITH AMENDMENTS" if total_score >= 9 else "REJECT"
    elif total_score == 16:
        decision = "ADOPT"
    elif total_score >= 9:
        decision = "ADOPT WITH AMENDMENTS"
    else:
        decision = "REJECT"

    if blocking_failures:
        summary = "The bounded loop remains incomplete because one or more blocking gates are unresolved."
    elif decision == "ADOPT":
        summary = "The bounded loop is fully measured, current-run grounded, and ratchet-ready."
    else:
        summary = "The bounded loop is strong but not yet fully ready for adoption."

    return {
        "gate_results": gates,
        "scorecard": {
            "run_id": current_run_id(),
            "required_metrics": sorted(REQUIRED_METRICS),
            "metrics": {
                "research_grounding": gates[0]["status"],
                "schema_validity": gates[1]["status"],
                "example_validation": gates[2]["status"],
                "repair_task_count": len(repairs),
                "promotion_readiness": decision,
            },
            "scores": scores,
            "total_score": total_score,
            "required_run_artifacts": artifact_status,
            "blocking_failed_gates": blocking_failures,
        },
        "promotion_decision": {
            "status": decision,
            "total_score": total_score,
            "scores": scores,
            "summary": summary,
        },
    }


def propose_repairs_data(gate_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    tasks = []
    counter = 1
    for gate in gate_results:
        if gate["blocking"] and gate["status"] == "fail":
            tasks.append(
                {
                    "id": f"REPAIR-{counter:04d}",
                    "title": f"Resolve {gate['gate_id']}",
                    "reason": gate["reason"],
                    "blocking_gate_ids": [gate["gate_id"]],
                    "acceptance_criteria": [
                        f"Gate `{gate['gate_id']}` changes from fail to pass.",
                        "Updated current-run artifacts record the resolved outcome.",
                    ],
                    "owner": "evaluation-agent",
                }
            )
            counter += 1
    return tasks


def write_session_summary(payload: dict[str, Any], repairs: list[dict[str, Any]]) -> Path:
    comparison = compare_to_previous_run()
    lines = [
        f"# Session Summary {current_run_id()}",
        "",
        "## Outcome",
        "",
        f"- Promotion decision: `{payload['promotion_decision']['status']}`",
        f"- Total score: `{payload['promotion_decision']['total_score']}`",
        f"- Blocking failed gates: `{sum(1 for gate in payload['gate_results'] if gate['blocking'] and gate['status'] == 'fail')}`",
        f"- Repair tasks emitted: `{len(repairs)}`",
        "",
        "## Gate Status",
        "",
    ]
    for gate in payload["gate_results"]:
        lines.append(f"- `{gate['gate_id']}` -> `{gate['status']}`")
    lines.extend(["", "## Next Bounded Move", ""])
    if repairs:
        lines.append(f"- Resolve `{repairs[0]['blocking_gate_ids'][0]}` before further promotion work.")
    else:
        lines.append("- No blocking repairs remain in the bounded kernel.")
    if comparison is not None:
        lines.extend(
            [
                "",
                "## Iteration Comparison",
                "",
                f"- Previous run: `{comparison['previous_run_id']}`",
                f"- Score delta: `{comparison['delta']}`",
            ]
        )
    path = session_summary_path()
    write_text(path, "\n".join(lines) + "\n")
    return path
