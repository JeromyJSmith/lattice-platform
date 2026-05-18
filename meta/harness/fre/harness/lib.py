"""Validation helpers for the FRE main contract slice."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

FRE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = FRE_ROOT.parents[2]
SCHEMA_DIR = FRE_ROOT / "schemas"
EXAMPLE_DIR = FRE_ROOT / "examples"
DOCS_DIR = FRE_ROOT / "docs"
SOURCE_DIR = FRE_ROOT / "source"
REQUIRED_DOCUMENT_CONTRACT_PATHS = {
    "GOAL.md",
    "GOLDENPATH.md",
}
REQUIRED_MAPPING_ROWS = {
    "gate_id": "clean",
    "repair_task": "clean",
    "promotion_decision": "partial",
    "scorecard": "clean",
    "validation_pass_criteria": "clean",
    "source_record": "partial",
    "artifact": "partial",
}
REQUIRED_COMPARISON_ENGINE = "infranodus"
REQUIRED_COMPARISON_GATES = {"verification", "health", "promotion"}
REQUIRED_PROMPT_CONTRACT_REFS = [
    "meta/harness/docs/specs/agent-heavy-run-prompt-index.md",
    "meta/harness/docs/specs/agent-heavy-run-prompt-schema.md",
    "meta/harness/docs/specs/agent-heavy-run-prompt.schema.json",
    "meta/harness/docs/specs/agent-heavy-run-prompt.template.yaml",
    "meta/harness/docs/copilot-prompting-playbook.md",
]
REQUIRED_SCOPE_ROWS = {
    "comparison_core": {
        "difference_between_texts",
        "generate_content_gaps",
        "generate_contextual_hint",
    },
    "supporting_skills": {
        "ontology-creator-skill",
        "graph-rag-skill",
        "content-gap-skill",
    },
    "explicit_non_scope": {
        "generate_seo_report",
        "analyze_google_search_results",
    },
}
REQUIRED_PARTS = {
    "source",
    "schema",
    "examples",
    "expected_failures",
    "tests",
    "evaluation",
    "promotion",
}
REQUIRED_HOOK_POINT_FILES = {
    "meta/harness/fre/source/provenance.json",
    "meta/harness/fre/source/prompt-contract-trace.json",
    "meta/harness/fre/schemas/front-matter.schema.json",
    "meta/harness/fre/schemas/gate-progress.schema.json",
    "meta/harness/fre/schemas/bridge-record.schema.json",
    "meta/harness/fre/evaluation/artifacts-inventory.json",
    "meta/harness/fre/promotion/artifacts-inventory.json",
}


@dataclass(frozen=True)
class FailureObservation:
    """A normalized example-validation failure."""

    failure_class: str
    field: str
    message: str


def read_text(path: Path) -> str:
    """Read UTF-8 text from a file."""

    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> Any:
    """Read a JSON file."""

    return json.loads(read_text(path))


def read_yaml(path: Path) -> Any:
    """Read a YAML file."""

    return yaml.safe_load(read_text(path))


def extract_front_matter(text: str) -> dict[str, Any] | None:
    """Extract YAML front matter from a markdown document."""

    if not text.startswith("---\n"):
        return None
    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        return None
    payload = _normalize_yaml_scalars(yaml.safe_load(parts[0][4:]))
    return payload if isinstance(payload, dict) else None


def extract_bottom_matter(text: str) -> dict[str, Any] | None:
    """Extract the governed bottom-matter block from a markdown document."""

    marker = "\n---bottom-matter---\n"
    if marker not in text:
        return None
    payload = _normalize_yaml_scalars(yaml.safe_load(text.split(marker, 1)[1]))
    return payload if isinstance(payload, dict) else None


def check_all_schemas() -> dict[str, Any]:
    """Validate all FRE schema files as Draft 2020-12 schemas."""

    results = []
    all_valid = True
    for path in sorted(SCHEMA_DIR.glob("*.json")):
        schema = read_json(path)
        issues: list[str] = []
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as exc:  # jsonschema.SchemaError subclasses Exception
            issues.append(str(exc))
        status = "pass" if not issues else "fail"
        all_valid = all_valid and status == "pass"
        results.append({"schema": path.name, "status": status, "issues": issues})
    return {"all_valid": all_valid, "schemas": results}


def validate_examples_data() -> dict[str, Any]:
    """Validate all example fixtures against the canonical schema family."""

    valid_pairs = [
        ("front-matter.schema.json", "front-matter.valid.json"),
        ("gate-progress.schema.json", "gate-progress.valid.json"),
        ("bottom-matter.schema.json", "bottom-matter.valid.json"),
        ("bridge-record.schema.json", "bridge-record.valid.json"),
    ]
    valid_results = []
    for schema_name, example_name in valid_pairs:
        failures = validate_instance(schema_name, read_json(EXAMPLE_DIR / example_name))
        valid_results.append(
            {
                "example": example_name,
                "schema": schema_name,
                "status": "pass" if not failures else "fail",
                "failures": [failure.__dict__ for failure in failures],
            }
        )

    invalid_results = []
    payload = read_yaml(EXAMPLE_DIR / "expected-failures.yaml")
    for entry in payload["expected_failures"]:
        failures = validate_instance(entry["schema"], read_json(FRE_ROOT / entry["example"]))
        observed_classes = {failure.failure_class for failure in failures}
        observed_fields = {failure.field for failure in failures}
        expected_classes = set(entry.get("expected_failure_classes", []))
        expected_fields = set(entry.get("expected_fields", []))
        invalid_results.append(
            {
                "example": entry["example"],
                "schema": entry["schema"],
                "status": "pass" if failures else "fail",
                "observed_failures": [failure.__dict__ for failure in failures],
                "matched_expected": bool(failures)
                and expected_classes.issubset(observed_classes)
                and expected_fields.issubset(observed_fields),
            }
        )

    return {"valid_examples": valid_results, "invalid_examples": invalid_results}


def document_contract_status() -> dict[str, Any]:
    """Validate the bounded FRE markdown contract documents."""

    results = []
    parse_errors: list[str] = []
    missing_front_matter: list[str] = []
    missing_bottom_matter: list[str] = []
    for rel in sorted(REQUIRED_DOCUMENT_CONTRACT_PATHS):
        path = FRE_ROOT / rel
        text = read_text(path)
        front_matter = extract_front_matter(text)
        bottom_matter = extract_bottom_matter(text)
        front_failures = validate_instance("front-matter.schema.json", front_matter) if front_matter else []
        bottom_failures = validate_instance("bottom-matter.schema.json", bottom_matter) if bottom_matter else []
        if front_matter is None:
            missing_front_matter.append(rel)
        if bottom_matter is None:
            missing_bottom_matter.append(rel)
        parse_errors.extend(f"{rel}:front:{failure.message}" for failure in front_failures)
        parse_errors.extend(f"{rel}:bottom:{failure.message}" for failure in bottom_failures)
        results.append(
            {
                "path": rel,
                "has_front_matter": front_matter is not None,
                "has_bottom_matter": bottom_matter is not None,
                "front_matter_valid": not front_failures,
                "bottom_matter_valid": not bottom_failures,
            }
        )
    inventory = validate_part_inventory()
    return {
        "status": "pass"
        if not parse_errors and not missing_front_matter and not missing_bottom_matter and inventory["status"] == "pass"
        else "fail",
        "parse_errors": parse_errors,
        "missing_front_matter": missing_front_matter,
        "missing_bottom_matter": missing_bottom_matter,
        "missing_part_paths": inventory["missing_paths"],
        "documents": results,
    }


def mapping_rows() -> dict[str, str]:
    """Read the governed translation-map rows needed by contract tests."""

    text = read_text(DOCS_DIR / "fre-to-lattice-map.md")
    rows = {}
    for field in REQUIRED_MAPPING_ROWS:
        match = re.search(rf"\| `{re.escape(field)}` \| [^|]+ \| ([^|]+) \|", text)
        rows[field] = match.group(1).strip() if match else ""
    return rows


def validate_part_inventory() -> dict[str, Any]:
    """Check that the local proof-package inventory points at real files."""

    provenance = read_json(SOURCE_DIR / "provenance.json")
    missing_paths = []
    for part, paths in provenance["parts"].items():
        for rel in paths:
            if not (REPO_ROOT / rel).exists():
                missing_paths.append({"part": part, "path": rel})
    return {"status": "pass" if not missing_paths else "fail", "missing_paths": missing_paths}


def comparison_contract_status() -> dict[str, Any]:
    """Validate that comparison-bearing FRE surfaces point at InfraNodus cleanly."""

    provenance = read_json(SOURCE_DIR / "provenance.json")
    prompt_trace = read_json(SOURCE_DIR / "prompt-contract-trace.json")
    evaluation = read_json(FRE_ROOT / "evaluation" / "artifacts-inventory.json")
    promotion = read_json(FRE_ROOT / "promotion" / "artifacts-inventory.json")
    goal_bottom = extract_bottom_matter(read_text(FRE_ROOT / "GOAL.md")) or {}
    golden_bottom = extract_bottom_matter(read_text(FRE_ROOT / "GOLDENPATH.md")) or {}

    errors: list[str] = []

    if REQUIRED_COMPARISON_ENGINE not in str(provenance.get("authority_contracts", {}).get("comparison_engine", [])):
        errors.append("provenance:missing_infranodus_authority_refs")
    if prompt_trace.get("prompt_contract_refs") != REQUIRED_PROMPT_CONTRACT_REFS:
        errors.append("prompt_trace:wrong_prompt_contract_refs")
    if prompt_trace.get("comparison_hook", {}).get("engine") != REQUIRED_COMPARISON_ENGINE:
        errors.append("prompt_trace:wrong_comparison_engine")
    phase_names = {item.get("phase") for item in prompt_trace.get("lifecycle_phases", [])}
    if phase_names != {"harvest", "registry", "manifest", "schema", "tests", "evaluation", "promotion"}:
        errors.append("prompt_trace:wrong_lifecycle_phases")
    if evaluation.get("comparison_engine") != REQUIRED_COMPARISON_ENGINE:
        errors.append("evaluation:wrong_comparison_engine")
    if promotion.get("comparison_engine") != REQUIRED_COMPARISON_ENGINE:
        errors.append("promotion:wrong_comparison_engine")
    for label, payload, required_rows in (
        (
            "evaluation",
            evaluation.get("comparison_dependencies", {}),
            {"difference_between_texts", "generate_content_gaps", "generate_contextual_hint"},
        ),
        (
            "promotion",
            promotion.get("comparison_dependencies", {}),
            {"generate_content_gaps", "retrieve_from_knowledge_base"},
        ),
    ):
        if payload.get("manifest_surface") != "analysis/infranodus/infranodus-capability-manifest.yaml":
            errors.append(f"{label}:missing_manifest_surface")
        if payload.get("scope_ref") != "meta/harness/fre/source/provenance.json#/infranodus_scope/comparison_core":
            errors.append(f"{label}:wrong_scope_ref")
        if not required_rows.issubset(set(payload.get("required_rows", []))):
            errors.append(f"{label}:missing_required_rows")
        if not payload.get("required_artifacts"):
            errors.append(f"{label}:missing_required_artifacts")

    hook_files = {entry.get("file") for entry in provenance.get("harvested_hook_points", [])}
    if not REQUIRED_HOOK_POINT_FILES.issubset(hook_files):
        errors.append("provenance:missing_harvested_hook_points")

    infranodus_scope = provenance.get("infranodus_scope", {})
    for scope_name, required_rows in REQUIRED_SCOPE_ROWS.items():
        if not required_rows.issubset(set(infranodus_scope.get(scope_name, []))):
            errors.append(f"provenance:{scope_name}:missing_scope_rows")

    part_dependencies = provenance.get("part_dependencies", {})
    if set(part_dependencies) != REQUIRED_PARTS:
        errors.append("provenance:wrong_part_dependencies")
    for part in REQUIRED_PARTS.intersection(part_dependencies):
        dependency = part_dependencies.get(part, {})
        if dependency.get("comparison_engine") != REQUIRED_COMPARISON_ENGINE:
            errors.append(f"provenance:{part}:wrong_comparison_engine")
        if not dependency.get("required_rows"):
            errors.append(f"provenance:{part}:missing_required_rows")
        if not dependency.get("required_artifacts"):
            errors.append(f"provenance:{part}:missing_required_artifacts")

    for label, payload in (("goal", goal_bottom), ("golden", golden_bottom)):
        for entry in payload.get("gate_progress", []):
            gate_id = entry.get("gate_id")
            if gate_id in REQUIRED_COMPARISON_GATES:
                if entry.get("comparison_required") is not True:
                    errors.append(f"{label}:{gate_id}:comparison_not_required")
                if entry.get("comparison_engine") != REQUIRED_COMPARISON_ENGINE:
                    errors.append(f"{label}:{gate_id}:wrong_comparison_engine")
                if not entry.get("comparison_artifacts"):
                    errors.append(f"{label}:{gate_id}:missing_comparison_artifacts")

    return {"status": "pass" if not errors else "fail", "errors": errors}


def validate_instance(schema_name: str, payload: Any) -> list[FailureObservation]:
    """Validate one payload against one named schema."""

    validator = _validator_for_schema(schema_name)
    failures = [_normalize_error(error) for error in validator.iter_errors(payload)]
    return sorted(failures, key=lambda item: (item.field, item.failure_class, item.message))


def _build_registry() -> Registry:
    """Build a schema registry for local Draft 2020-12 references."""

    registry = Registry()
    for path in sorted(SCHEMA_DIR.glob("*.json")):
        schema = read_json(path)
        registry = registry.with_resource(schema["$id"], Resource.from_contents(schema))
    return registry


def _schema(schema_name: str) -> dict[str, Any]:
    """Load one schema payload."""

    payload = read_json(SCHEMA_DIR / schema_name)
    if not isinstance(payload, dict):
        raise TypeError(f"{schema_name} must be a JSON object schema")
    return payload


def _validator_for_schema(schema_name: str) -> Draft202012Validator:
    """Construct a validator for one schema."""

    schema = _schema(schema_name)
    return Draft202012Validator(schema, registry=_build_registry())


def _normalize_error(error: Any) -> FailureObservation:
    """Convert a jsonschema error into a stable observation."""

    validator = error.validator
    if validator == "required":
        match = re.search(r"'([^']+)' is a required property", error.message)
        missing = match.group(1) if match else ""
        field = _join_path(list(error.absolute_path) + ([missing] if missing else []))
        return FailureObservation("REQUIRED_FIELD_MISSING", field, error.message)
    if validator == "additionalProperties":
        match = re.search(r"'([^']+)' was unexpected", error.message)
        field = _join_path(list(error.absolute_path) + ([match.group(1)] if match else []))
        return FailureObservation("ADDITIONAL_PROPERTY_NOT_ALLOWED", field, error.message)
    if validator == "enum":
        return FailureObservation("ENUM_VIOLATION", _join_path(error.absolute_path), error.message)
    if validator == "minItems":
        return FailureObservation("MIN_ITEMS_VIOLATION", _join_path(error.absolute_path), error.message)
    if validator == "contains":
        return FailureObservation("ARRAY_CONTAINS_VIOLATION", _join_path(error.absolute_path), error.message)
    if validator == "format":
        return FailureObservation("FORMAT_VIOLATION", _join_path(error.absolute_path), error.message)
    return FailureObservation(str(validator).upper(), _join_path(error.absolute_path), error.message)


def _join_path(parts: Any) -> str:
    """Convert an error path into dotted form."""

    values = [str(part) for part in parts]
    return ".".join(values) if values else "$"


def _normalize_yaml_scalars(payload: Any) -> Any:
    """Convert YAML-native dates back into JSON-compatible scalar values."""

    if isinstance(payload, dict):
        return {key: _normalize_yaml_scalars(value) for key, value in payload.items()}
    if isinstance(payload, list):
        return [_normalize_yaml_scalars(item) for item in payload]
    if isinstance(payload, datetime):
        return payload.isoformat()
    if isinstance(payload, date):
        return payload.isoformat()
    return payload
