#!/usr/bin/env python3
"""Verify the governed Juniper quantity-takeoff and estimation proof path."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
PIXELTABLE_ROOT = REPO_ROOT / "pixeltable"
if REPO_ROOT.as_posix() not in sys.path:
    sys.path.insert(0, REPO_ROOT.as_posix())
if PIXELTABLE_ROOT.as_posix() not in sys.path:
    sys.path.insert(0, PIXELTABLE_ROOT.as_posix())

from ddc.estimation.quantity_takeoff_runtime import (  # noqa: E402
    PROJECT_TARGET,
    SUPPORTED_BY as QUANTITY_SUPPORTED_BY,
    run_quantity_takeoff_proof,
)

MATRIX_PATH = REPO_ROOT / "ddc" / "capability-matrix.yaml"
REGISTRY_PATH = REPO_ROOT / "analysis" / "capabilities" / "ddc-capability-registry.yaml"
TS_MATRIX_PATH = REPO_ROOT / "src" / "data" / "ddc-capability-matrix.ts"
DDC_GOAL_PATH = REPO_ROOT / "ddc" / "GOAL.md"
ESTIMATION_GOAL_PATH = REPO_ROOT / "ddc" / "estimation" / "GOAL.md"
ESTIMATION_GOLDENPATH_PATH = REPO_ROOT / "ddc" / "estimation" / "GOLDENPATH.md"
ESTIMATION_README_PATH = REPO_ROOT / "ddc" / "estimation" / "README.md"
DDC_MAPPING_PATH = REPO_ROOT / "meta" / "DDC_MAPPING.md"
ESTIMATION_SOURCE_PATH = REPO_ROOT / "ddc" / "estimation" / "source" / "source-inventory.json"
ESTIMATION_PROVENANCE_PATH = REPO_ROOT / "ddc" / "estimation" / "source" / "provenance.json"
ESTIMATION_EVALUATION_DIR = REPO_ROOT / "ddc" / "estimation" / "evaluation"
ESTIMATION_PROMOTION_DIR = REPO_ROOT / "ddc" / "estimation" / "promotion"
PROOF_PATHS = {
    "cwicr-seed": REPO_ROOT / "meta" / "harness" / "docs" / "sessions" / "2026-05-18-cwicr-seed-proof.json",
    "cwicr-qdrant-cost-search": REPO_ROOT
    / "meta"
    / "harness"
    / "docs"
    / "sessions"
    / "2026-05-18-cwicr-qdrant-cost-search-proof.json",
    "ifc-cost-enrichment": REPO_ROOT
    / "meta"
    / "harness"
    / "docs"
    / "sessions"
    / "2026-05-18-ifc-cost-enrichment-proof.json",
    "boq-sync": REPO_ROOT / "meta" / "harness" / "docs" / "sessions" / "2026-05-18-boq-sync-proof.json",
    "boq-read": REPO_ROOT / "meta" / "harness" / "docs" / "sessions" / "2026-05-18-boq-read-proof.json",
    "boq-export": REPO_ROOT / "meta" / "harness" / "docs" / "sessions" / "2026-05-18-boq-export-proof.json",
    "phases-sync": REPO_ROOT / "meta" / "harness" / "docs" / "sessions" / "2026-05-18-phases-sync-proof.json",
}
CONTRACT_SUPPORTED_IDS = [*QUANTITY_SUPPORTED_BY, "phases-sync", "quantity-takeoff-agent"]
BLOCKED_IDS: list[str] = []
ROSE_LINEAGE = "ROSE Residence"
FARBER_LINEAGE = "Farber-Haines 2521 IFC source lineage"


def _load_estimation_contract_lib():
    harness_path = REPO_ROOT / "ddc" / "estimation" / "harness" / "lib.py"
    spec = importlib.util.spec_from_file_location("ddc_estimation_contract_lib", harness_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("ddc estimation harness lib could not be loaded")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--capability",
        required=True,
        choices=("quantity-takeoff-agent", "ddc-estimation-contract"),
    )
    return parser.parse_args()


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"{path.relative_to(REPO_ROOT).as_posix()} did not parse as an object")
    return payload


def _yaml_capability(path: Path, capability_id: str) -> dict[str, Any]:
    payload = _load_yaml(path)
    for capability in payload.get("capabilities", []) or []:
        if isinstance(capability, dict) and capability.get("id") == capability_id:
            return capability
    raise RuntimeError(f"{capability_id} missing from {path.relative_to(REPO_ROOT).as_posix()}")


def _ts_entry(capability_id: str) -> str:
    text = TS_MATRIX_PATH.read_text(encoding="utf-8")
    match = re.search(
        rf'\{{\s*id: "{re.escape(capability_id)}",(.*?)\n\s*\}},',
        text,
        flags=re.DOTALL,
    )
    if match is None:
        raise RuntimeError(f"{capability_id} missing from {TS_MATRIX_PATH.relative_to(REPO_ROOT).as_posix()}")
    return match.group(1)


def _ts_status(entry: str) -> str | None:
    match = re.search(r'status:\s*"([^"]+)"', entry)
    return match.group(1) if match else None


def _ts_array(entry: str, field: str) -> list[str]:
    match = re.search(rf"{field}:\s*\[([^\]]*)\]", entry, flags=re.DOTALL)
    if match is None:
        return []
    return re.findall(r'"([^"]+)"', match.group(1))


def _proof_status(path: Path) -> str:
    payload = json.loads(path.read_text(encoding="utf-8"))
    verification = payload.get("verification")
    if not isinstance(verification, dict):
        raise RuntimeError(f"{path.relative_to(REPO_ROOT).as_posix()} is missing verification metadata")
    status = verification.get("status")
    if not isinstance(status, str):
        raise RuntimeError(f"{path.relative_to(REPO_ROOT).as_posix()} is missing verification.status")
    return status


def _collect_list_after_line(text: str, marker: str) -> list[str]:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() != marker:
            continue
        values: list[str] = []
        for next_line in lines[index + 1 :]:
            stripped = next_line.strip()
            if not stripped:
                if values:
                    break
                continue
            if stripped.startswith("#"):
                break
            if stripped.startswith("- "):
                values.extend(re.findall(r"`([^`]+)`", stripped))
                continue
            numbered = re.match(r"\d+\.\s+(.*)", stripped)
            if numbered:
                values.extend(re.findall(r"`([^`]+)`", numbered.group(1)))
                continue
            if values:
                break
        return values
    raise RuntimeError(f"marker {marker!r} missing")


def _collect_inline_ids(text: str, marker: str) -> list[str]:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(marker):
            return re.findall(r"`([^`]+)`", stripped)
    raise RuntimeError(f"marker {marker!r} missing")


def _collect_goal_helpers(text: str) -> list[str]:
    marker = "2. **Dependency-chain truthfulness**:"
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith(marker):
            continue
        return re.findall(r"`([^`]+)`", stripped)
    raise RuntimeError(f"marker {marker!r} missing")


def _verify_alignment() -> list[str]:
    blockers: list[str] = []
    contract_lib = _load_estimation_contract_lib()
    contract_matrix = _yaml_capability(MATRIX_PATH, "ddc-estimation-contract")
    contract_registry = _yaml_capability(REGISTRY_PATH, "ddc-estimation-contract")
    quantity_matrix = _yaml_capability(MATRIX_PATH, "quantity-takeoff-agent")
    quantity_registry = _yaml_capability(REGISTRY_PATH, "quantity-takeoff-agent")
    contract_ts = _ts_entry("ddc-estimation-contract")
    quantity_ts = _ts_entry("quantity-takeoff-agent")

    if contract_matrix.get("project_target") != PROJECT_TARGET or contract_registry.get("project_target") != PROJECT_TARGET:
        blockers.append("Juniper operational target drifted out of the matrix or registry.")
    estimation_readme = ESTIMATION_README_PATH.read_text(encoding="utf-8")
    if PROJECT_TARGET not in estimation_readme:
        blockers.append("Juniper operational target drifted out of ddc/estimation/README.md.")
    if ROSE_LINEAGE not in estimation_readme:
        blockers.append("ROSE pilot-proof lineage drifted out of ddc/estimation/README.md.")
    if FARBER_LINEAGE not in " ".join(contract_registry.get("proof_lineage", [])):
        blockers.append("Farber-Haines repo-local lineage drifted out of the capability registry.")

    if contract_matrix.get("supported_by") != CONTRACT_SUPPORTED_IDS:
        blockers.append("ddc/capability-matrix.yaml supported_by no longer matches the canonical helper set.")
    if contract_registry.get("supported_by") != CONTRACT_SUPPORTED_IDS:
        blockers.append("analysis/capabilities/ddc-capability-registry.yaml supported_by no longer matches the canonical helper set.")
    if _ts_array(contract_ts, "supportedBy") != CONTRACT_SUPPORTED_IDS:
        blockers.append("src/data/ddc-capability-matrix.ts supportedBy no longer matches the canonical helper set.")

    if contract_matrix.get("blocked_by") != BLOCKED_IDS:
        blockers.append("ddc/capability-matrix.yaml blocked_by no longer matches the canonical blocker set.")
    if contract_registry.get("blocking_capabilities") != BLOCKED_IDS:
        blockers.append("analysis/capabilities/ddc-capability-registry.yaml blocking_capabilities no longer matches the canonical blocker set.")
    if _ts_array(contract_ts, "blockedBy") != BLOCKED_IDS:
        blockers.append("src/data/ddc-capability-matrix.ts blockedBy no longer matches the canonical blocker set.")

    ddc_goal_helpers = _collect_goal_helpers(DDC_GOAL_PATH.read_text(encoding="utf-8"))
    estimation_goal_helpers = _collect_list_after_line(
        ESTIMATION_GOAL_PATH.read_text(encoding="utf-8"),
        "### Reused helpers already helping",
    )
    estimation_goal_blockers = _collect_list_after_line(
        ESTIMATION_GOAL_PATH.read_text(encoding="utf-8"),
        "### Blocking prerequisites",
    )
    readme_helpers = _collect_list_after_line(
        estimation_readme,
        "### Already helping now",
    )
    readme_blockers = _collect_list_after_line(
        estimation_readme,
        "### Still blocking promotion",
    )
    goldenpath_helpers = _collect_list_after_line(
        ESTIMATION_GOLDENPATH_PATH.read_text(encoding="utf-8"),
        "The golden path must reuse these capabilities as dependencies:",
    )
    goldenpath_blockers = _collect_list_after_line(
        ESTIMATION_GOLDENPATH_PATH.read_text(encoding="utf-8"),
        "It must also confront these blocked prerequisites directly:",
    )
    mapping_text = DDC_MAPPING_PATH.read_text(encoding="utf-8")
    mapping_helpers = _collect_inline_ids(mapping_text, "- already helping now:")
    mapping_blockers = _collect_inline_ids(mapping_text, "- still blocking promotion:")

    for label, actual in (
        ("ddc/GOAL.md helper list", ddc_goal_helpers),
        ("ddc/estimation/GOAL.md helper list", estimation_goal_helpers),
        ("ddc/estimation/README.md helper list", readme_helpers),
        ("ddc/estimation/GOLDENPATH.md helper list", goldenpath_helpers),
        ("meta/DDC_MAPPING.md helper list", mapping_helpers),
    ):
        if actual != CONTRACT_SUPPORTED_IDS:
            blockers.append(f"{label} no longer matches the canonical helper set.")

    for label, actual in (
        ("ddc/estimation/GOAL.md blocker list", estimation_goal_blockers),
        ("ddc/estimation/README.md blocker list", readme_blockers),
        ("ddc/estimation/GOLDENPATH.md blocker list", goldenpath_blockers),
        ("meta/DDC_MAPPING.md blocker list", mapping_blockers),
    ):
        if actual != BLOCKED_IDS:
            blockers.append(f"{label} no longer matches the canonical blocker set.")

    if _ts_status(contract_ts) != str(contract_matrix.get("status")):
        blockers.append("TypeScript matrix status drifted from ddc/capability-matrix.yaml for ddc-estimation-contract.")
    if _ts_status(quantity_ts) != str(quantity_matrix.get("status")):
        blockers.append("TypeScript matrix status drifted from ddc/capability-matrix.yaml for quantity-takeoff-agent.")
    if str(quantity_registry.get("state")) != "ACTIVE":
        blockers.append("Registry state drifted for quantity-takeoff-agent.")
    if str(contract_registry.get("state")) != "ACTIVE":
        blockers.append("Registry state drifted for ddc-estimation-contract.")
    if not ESTIMATION_SOURCE_PATH.exists():
        blockers.append("ddc/estimation/source/source-inventory.json is missing.")
    if not ESTIMATION_PROVENANCE_PATH.exists():
        blockers.append("ddc/estimation/source/provenance.json is missing.")
    if contract_lib.check_all_schemas().get("all_valid") is not True:
        blockers.append("DDC estimation contract schemas are not all valid Draft 2020-12 schemas.")
    example_payload = contract_lib.validate_examples_data()
    if not all(item["status"] == "pass" for item in example_payload["valid_examples"]):
        blockers.append("DDC estimation valid fixtures do not all pass schema validation.")
    if not all(item["status"] == "pass" and item["matched_expected"] is True for item in example_payload["invalid_examples"]):
        blockers.append("DDC estimation invalid fixtures do not all fail for the expected reasons.")
    if contract_lib.traceability_contract_status().get("status") != "pass":
        blockers.append("DDC estimation traceability contract is not satisfied.")
    if contract_lib.source_packet_status().get("status") != "pass":
        blockers.append("DDC estimation source packet drifted from the Juniper/ROSE/Luke truth contract.")
    return blockers


def _quantity_report() -> tuple[int, dict[str, Any]]:
    matrix_row = _yaml_capability(MATRIX_PATH, "quantity-takeoff-agent")
    registry_row = _yaml_capability(REGISTRY_PATH, "quantity-takeoff-agent")
    blockers = _verify_alignment()
    dependency_status = {
        "cwicr-seed": _yaml_capability(MATRIX_PATH, "cwicr-seed").get("status"),
        "cwicr-qdrant-cost-search": _yaml_capability(MATRIX_PATH, "cwicr-qdrant-cost-search").get("status"),
        "ifc-cost-enrichment": _yaml_capability(MATRIX_PATH, "ifc-cost-enrichment").get("status"),
        "boq-sync": _yaml_capability(MATRIX_PATH, "boq-sync").get("status"),
        "boq-read": _yaml_capability(MATRIX_PATH, "boq-read").get("status"),
        "boq-export": _yaml_capability(MATRIX_PATH, "boq-export").get("status"),
        "quantity-takeoff-agent": matrix_row.get("status"),
    }
    for capability_id, status in dependency_status.items():
        if capability_id != "quantity-takeoff-agent" and status != "green":
            blockers.append(f"{capability_id} is not green yet, so governed quantity orchestration cannot stay promotable.")
    if matrix_row.get("status") != "green":
        blockers.append("quantity-takeoff-agent is not green in ddc/capability-matrix.yaml.")
    proof: dict[str, Any] | None = None
    if not blockers:
        try:
            proof = run_quantity_takeoff_proof(REPO_ROOT)
        except Exception as exc:
            blockers.append(str(exc))
    if blockers:
        report = {
            "capability_id": "quantity-takeoff-agent",
            "status": "blocked",
            "matrix_status": matrix_row.get("status"),
            "registry_state": registry_row.get("state"),
            "dependency_status": dependency_status,
            "blockers": blockers,
        }
        return 1, report
    report = {
        **(proof or {}),
        "capability_id": "quantity-takeoff-agent",
        "status": "passed",
        "matrix_status": matrix_row.get("status"),
        "registry_state": registry_row.get("state"),
        "dependency_status": dependency_status,
    }
    return 0, report


def _contract_report() -> tuple[int, dict[str, Any]]:
    matrix_row = _yaml_capability(MATRIX_PATH, "ddc-estimation-contract")
    registry_row = _yaml_capability(REGISTRY_PATH, "ddc-estimation-contract")
    blockers = _verify_alignment()
    dependency_status = {
        capability_id: _yaml_capability(MATRIX_PATH, capability_id).get("status")
        for capability_id in CONTRACT_SUPPORTED_IDS + ["ddc-estimation-contract"]
    }
    helper_proof_status: dict[str, str] = {}
    for capability_id, path in PROOF_PATHS.items():
        try:
            helper_proof_status[capability_id] = _proof_status(path)
        except Exception as exc:
            blockers.append(str(exc))
    for capability_id, status in dependency_status.items():
        if capability_id != "ddc-estimation-contract" and status != "green":
            blockers.append(f"{capability_id} is not green, so end-to-end governed orchestration is still incomplete.")
    for capability_id, status in helper_proof_status.items():
        if status != "passed":
            blockers.append(f"{capability_id} proof artifact is not passing.")
    if matrix_row.get("status") != "green":
        blockers.append("ddc-estimation-contract is not green in ddc/capability-matrix.yaml.")
    quantity_proof: dict[str, Any] | None = None
    if not blockers:
        try:
            quantity_proof = run_quantity_takeoff_proof(REPO_ROOT, idempotency_key="ddc-estimation-contract-proof-0001")
        except Exception as exc:
            blockers.append(str(exc))
    if blockers:
        report = {
            "capability_id": "ddc-estimation-contract",
            "status": "blocked",
            "matrix_status": matrix_row.get("status"),
            "registry_state": registry_row.get("state"),
            "dependency_status": dependency_status,
            "proof_status": helper_proof_status,
            "project_target": matrix_row.get("project_target"),
            "supported_by": matrix_row.get("supported_by"),
            "blocked_by": matrix_row.get("blocked_by"),
            "blockers": blockers,
        }
        return 1, report
    report = {
        "capability_id": "ddc-estimation-contract",
        "status": "passed",
        "matrix_status": matrix_row.get("status"),
        "registry_state": registry_row.get("state"),
        "dependency_status": dependency_status,
        "proof_status": helper_proof_status,
        "project_target": matrix_row.get("project_target"),
        "supported_by": matrix_row.get("supported_by"),
        "blocked_by": matrix_row.get("blocked_by"),
        "quantity_takeoff_proof": quantity_proof,
    }
    return 0, report


def main() -> int:
    """Run one governed-estimation blocker verifier and return a verifier exit code."""
    args = _parse_args()
    try:
        exit_code, report = (
            _quantity_report()
            if args.capability == "quantity-takeoff-agent"
            else _contract_report()
        )
    except Exception as exc:
        report = {
            "capability_id": args.capability,
            "status": "blocked",
            "blockers": [str(exc)],
        }
        print(json.dumps(report, indent=2), file=sys.stderr)
        return 1
    stream = sys.stdout if exit_code == 0 else sys.stderr
    print(json.dumps(report, indent=2), file=stream)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
