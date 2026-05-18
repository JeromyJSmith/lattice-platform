"""Validation helpers for the DDC estimation contract package."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

ESTIMATION_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ESTIMATION_ROOT.parents[1]
CONTRACT_DIR = ESTIMATION_ROOT / "contract"
FIXTURES_DIR = ESTIMATION_ROOT / "fixtures"
SOURCE_DIR = ESTIMATION_ROOT / "source"
KERNEL_DIR = ESTIMATION_ROOT / "kernel"
REPORTS_DIR = ESTIMATION_ROOT / "reports"
EVALUATION_DIR = ESTIMATION_ROOT / "evaluation"
PROMOTION_DIR = ESTIMATION_ROOT / "promotion"


@dataclass(frozen=True)
class FailureObservation:
    """Normalized validation failure record for fixture and contract checks."""

    failure_class: str
    field: str
    message: str


VALID_PAIRS = [
    ("worksheet.schema.json", "fixtures/rose_residence/worksheet.raw.json"),
    ("worksheet.normalized.schema.json", "fixtures/rose_residence/worksheet.normalized.json"),
    ("estimate-project.schema.json", "fixtures/rose_residence/estimate-project.json"),
    ("estimate-pricebook-item.schema.json", "fixtures/rose_residence/estimate-pricebook-item.json"),
    ("estimate-line-item.schema.json", "fixtures/rose_residence/estimate-line-item.json"),
    ("estimate-audit-run.schema.json", "fixtures/rose_residence/estimate-audit-run.json"),
    ("worksheet.schema.json", "fixtures/juniper_avenue/worksheet.raw.json"),
    ("worksheet.normalized.schema.json", "fixtures/juniper_avenue/worksheet.normalized.json"),
    ("estimate-project.schema.json", "fixtures/juniper_avenue/estimate-project.json"),
    ("estimate-pricebook-item.schema.json", "fixtures/juniper_avenue/estimate-pricebook-item.json"),
    ("estimate-line-item.schema.json", "fixtures/juniper_avenue/estimate-line-item.json"),
    ("estimate-audit-run.schema.json", "fixtures/juniper_avenue/estimate-audit-run.json"),
]


def read_text(path: Path) -> str:
    """Read a UTF-8 text file from the estimation contract package."""

    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> Any:
    """Read a JSON file from the estimation contract package."""

    return json.loads(read_text(path))


def read_yaml(path: Path) -> Any:
    """Read a YAML file from the estimation contract package."""

    return yaml.safe_load(read_text(path))


def check_all_schemas() -> dict[str, Any]:
    """Validate every estimation contract schema as Draft 2020-12."""

    results = []
    all_valid = True
    for path in sorted(CONTRACT_DIR.glob("*.json")):
        schema = read_json(path)
        issues: list[str] = []
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as exc:
            issues.append(str(exc))
        status = "pass" if not issues else "fail"
        all_valid = all_valid and status == "pass"
        results.append({"schema": path.name, "status": status, "issues": issues})
    return {"all_valid": all_valid, "schemas": results}


def _validator(schema_name: str) -> Draft202012Validator:
    return Draft202012Validator(read_json(CONTRACT_DIR / schema_name))


def _normalize_error(error: Any) -> FailureObservation:
    validator_name = getattr(error, "validator", "unknown")
    if validator_name == "required":
        message = str(error.message)
        match = re.search(r"'([^']+)' is a required property", message)
        field = match.group(1) if match else "(required)"
        failure_class = "REQUIRED_FIELD_MISSING"
    elif validator_name == "enum":
        field = ".".join(str(part) for part in getattr(error, "absolute_path", [])) or "(root)"
        failure_class = "ENUM_VIOLATION"
    else:
        field = ".".join(str(part) for part in getattr(error, "absolute_path", [])) or "(root)"
        failure_class = str(validator_name).upper()
    return FailureObservation(failure_class=failure_class, field=field, message=error.message)


def validate_instance(schema_name: str, payload: Any) -> list[FailureObservation]:
    """Validate one payload against one contract schema and normalize failures."""

    failures = [_normalize_error(error) for error in _validator(schema_name).iter_errors(payload)]
    return sorted(failures, key=lambda item: (item.field, item.failure_class, item.message))


def _custom_stale_capability_ids(payload: dict[str, Any]) -> list[FailureObservation]:
    if payload.get("matrix_capability_id") == payload.get("registry_capability_id"):
        return []
    return [
        FailureObservation(
            failure_class="CAPABILITY_ID_DRIFT",
            field="registry_capability_id",
            message="registry capability id drifted from the canonical matrix capability id",
        )
    ]


def _custom_verifier_evidence_required(payload: dict[str, Any]) -> list[FailureObservation]:
    if payload.get("status") != "green":
        return []
    evidence = payload.get("proof_evidence")
    if isinstance(evidence, list) and evidence:
        return []
    return [
        FailureObservation(
            failure_class="VERIFIER_EVIDENCE_MISSING",
            field="proof_evidence",
            message="green capability status claim requires verifier evidence",
        )
    ]


CUSTOM_VALIDATORS = {
    "stale_capability_ids": _custom_stale_capability_ids,
    "verifier_evidence_required": _custom_verifier_evidence_required,
}


def validate_examples_data() -> dict[str, Any]:
    """Validate the bounded valid and invalid estimation fixtures."""

    valid_results = []
    for schema_name, rel_path in VALID_PAIRS:
        failures = validate_instance(schema_name, read_json(ESTIMATION_ROOT / rel_path))
        valid_results.append(
            {
                "example": rel_path,
                "schema": schema_name,
                "status": "pass" if not failures else "fail",
                "failures": [failure.__dict__ for failure in failures],
            }
        )

    invalid_results = []
    payload = read_yaml(FIXTURES_DIR / "expected-failures.yaml")
    for entry in payload["expected_failures"]:
        example_path = REPO_ROOT / entry["example"]
        if "schema" in entry:
            failures = validate_instance(entry["schema"], read_json(example_path))
        else:
            validator = CUSTOM_VALIDATORS[entry["custom_validator"]]
            failures = validator(read_json(example_path))
        observed_classes = {failure.failure_class for failure in failures}
        observed_fields = {failure.field for failure in failures}
        expected_classes = set(entry.get("expected_failure_classes", []))
        expected_fields = set(entry.get("expected_fields", []))
        invalid_results.append(
            {
                "example": entry["example"],
                "schema": entry.get("schema", entry.get("custom_validator")),
                "status": "pass" if failures else "fail",
                "observed_failures": [failure.__dict__ for failure in failures],
                "matched_expected": bool(failures)
                and expected_classes.issubset(observed_classes)
                and expected_fields.issubset(observed_fields),
            }
        )
    return {"valid_examples": valid_results, "invalid_examples": invalid_results}


def validate_expected_failures_data() -> dict[str, Any]:
    """Confirm invalid fixtures fail for the exact expected reasons."""

    payload = validate_examples_data()
    return {
        "invalid_examples": payload["invalid_examples"],
        "all_expected_failures_match": all(
            item["status"] == "pass" and item["matched_expected"] is True
            for item in payload["invalid_examples"]
        ),
    }


def traceability_contract_status() -> dict[str, Any]:
    """Check that valid fixtures preserve workbook, formula, and source traceability."""

    formulas = {
        formula["id"]
        for formula in read_yaml(KERNEL_DIR / "formulas.yaml").get("formulas", [])
        if isinstance(formula, dict)
    }
    provenance = read_json(SOURCE_DIR / "provenance.json")
    provenance_source_ids = {
        artifact["artifact_id"]
        for artifact in provenance.get("source_artifacts", [])
        if isinstance(artifact, dict) and artifact.get("artifact_id")
    }
    errors: list[str] = []
    for fixture_name in ("rose_residence", "juniper_avenue"):
        worksheet = read_json(FIXTURES_DIR / fixture_name / "worksheet.raw.json")
        workbook_source_ids = {
            artifact["artifact_id"]
            for artifact in worksheet.get("source_artifacts", [])
            if isinstance(artifact, dict) and artifact.get("artifact_id")
        }
        line_item = read_json(FIXTURES_DIR / fixture_name / "estimate-line-item.json")
        traceability = line_item.get("traceability", {})
        workbook_ref = traceability.get("workbook_row_ref")
        if not isinstance(workbook_ref, str) or "!" not in workbook_ref:
            errors.append(f"{fixture_name}:traceability.workbook_row_ref is missing or malformed")
        missing_formulas = sorted(set(traceability.get("formula_refs", [])) - formulas)
        if missing_formulas:
            errors.append(f"{fixture_name}:missing formula refs {missing_formulas}")
        available_source_ids = workbook_source_ids | provenance_source_ids
        missing_sources = sorted(set(traceability.get("source_artifact_ids", [])) - available_source_ids)
        if missing_sources:
            errors.append(f"{fixture_name}:missing source artifact ids {missing_sources}")
    return {"status": "pass" if not errors else "fail", "errors": errors}


def source_packet_status() -> dict[str, Any]:
    """Check that the source packet preserves Juniper target and ROSE/Luke lineage."""

    inventory = read_json(SOURCE_DIR / "source-inventory.json")
    provenance = read_json(SOURCE_DIR / "provenance.json")
    errors: list[str] = []
    if inventory.get("operational_target") != "MARPA — 918 Juniper Avenue":
        errors.append("source inventory operational target drifted")
    if provenance.get("operational_target", {}).get("project_name") != "MARPA — 918 Juniper Avenue":
        errors.append("source provenance operational target drifted")
    if "ROSE Residence" not in str(inventory.get("pilot_lineage_only", [])):
        errors.append("ROSE pilot lineage missing from source inventory")
    if "Luke Spreadsheet Prototype" not in str(inventory.get("pilot_lineage_only", [])):
        errors.append("Luke workbook lineage missing from source inventory")
    return {"status": "pass" if not errors else "fail", "errors": errors}
