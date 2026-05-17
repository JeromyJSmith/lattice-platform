"""Harness routes for benchmark reports and single-file agent job surfaces."""

from __future__ import annotations

import json
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from fastapi import APIRouter, Body, Depends, HTTPException

from service.deps import require_local_socket_or_token

router = APIRouter(dependencies=[Depends(require_local_socket_or_token)])


SINGLE_FILE_AGENT_CATALOG: list[dict[str, Any]] = [
    {
        "id": "codebase-context-ripgrep",
        "source": "disler/single-file-agents:sfa_codebase_context_agent_w_ripgrep_v3.py",
        "lattice_target": "meta/harness/tools/codebase-context-agent.py",
        "surface": "sidecar_job",
        "state": "active",
        "endpoint_shape": "POST /v1/harness/single-file-agents/runs",
        "purpose": "Find task-relevant files before a bounded harness job.",
        "allowed_env": [],
    },
    {
        "id": "meta-prompt-generator",
        "source": "disler/single-file-agents:sfa_meta_prompt_openai_v1.py",
        "lattice_target": "meta/harness/tools/meta-prompt-agent.py",
        "surface": "sidecar_job",
        "state": "candidate",
        "endpoint_shape": "POST /v1/harness/single-file-agents/runs",
        "purpose": "Generate reusable prompt contracts from structured purpose and sections.",
    },
    {
        "id": "guardrailed-agent-runner",
        "source": "disler/single-file-agents:openai-agents-examples/10_agent_with_guardrails.py",
        "lattice_target": "meta/harness/tools/guardrailed-agent-runner.py",
        "surface": "sidecar_job",
        "state": "candidate",
        "endpoint_shape": "POST /v1/harness/single-file-agents/runs",
        "purpose": "Run a bounded agent behind input validation and safety guardrails.",
    },
    {
        "id": "duckdb-analysis-agent",
        "source": "disler/single-file-agents:sfa_duckdb_*",
        "lattice_target": "meta/harness/tools/duckdb-analysis-agent.py",
        "surface": "sidecar_job",
        "state": "candidate",
        "endpoint_shape": "POST /v1/harness/single-file-agents/runs",
        "purpose": "Analyze Pixeltable-exported Arrow or Parquet through DuckDB without making DuckDB durable storage.",
    },
]

REGISTERED_SINGLE_FILE_JOBS: dict[str, dict[str, Any]] = {
    item["id"]: item for item in SINGLE_FILE_AGENT_CATALOG if item["id"] == "codebase-context-ripgrep"
}

RUNNABLE_CAPABILITY_TASKS: dict[str, dict[str, Any]] = {
    "codebase-context-ripgrep": {
        "kind": "single_file_agent",
        "action_id": "run-codebase-context-ripgrep",
        "job_id": "codebase-context-ripgrep",
        "label": "Run proof",
        "endpoint": "POST /v1/harness/capabilities/runs",
        "task": (
            "Identify files relevant to adding or changing a FastAPI sidecar route "
            "for single-file harness agents and benchmark reports."
        ),
        "expect_paths": [
            "pixeltable/service/routes/harness.py",
            "meta/harness/single-file-harness-agents.md",
        ],
    },
    "python-docstring-rule": {
        "kind": "script_exit_code",
        "action_id": "run-python-docstring-rule",
        "job_id": "python-docstring-rule",
        "label": "Run proof",
        "endpoint": "POST /v1/harness/capabilities/runs",
        "command": ["uv", "run", "python", "scripts/check-python-docstrings.py"],
        "expected_returncode": 0,
    }
}

ALLOWED_PROOF_VERIFICATION_STATUSES = {"passed", "failed", "review_required", "unverified"}


SAMPLE_BENCHMARK_REPORT: dict[str, Any] = {
    "benchmark_name": "Meta-Harness proof-run gate",
    "purpose": "Compare candidate models on one LATTICE capability proof task before registry promotion.",
    "base_prompt": (
        "Given a capability candidate, produce a verifier-ready proof report with invocation, "
        "expected outcome, evidence path, and promotion decision."
    ),
    "prompt_iterations": [
        {
            "capability": "benchy-console-report",
            "expected": "proof_run_required_before_registry_promotion",
        }
    ],
    "provenance": {
        "source": "sample",
        "trust": "synthetic",
        "label": "Synthetic sample report",
    },
    "verification": {
        "status": "unverified",
        "message": "Sample data only. Do not treat this report as live proof.",
    },
    "models": [
        {
            "model": "qwen3:14b",
            "provider": "ollama",
            "results": [
                {"prompt": "registry gate", "success": True, "latency_ms": 9400, "cost_usd": 0, "score": 0.72},
                {"prompt": "evidence shape", "success": True, "latency_ms": 8700, "cost_usd": 0, "score": 0.78},
                {"prompt": "failure taxonomy", "success": False, "latency_ms": 10100, "cost_usd": 0, "score": 0.41},
            ],
        },
        {
            "model": "claude-sonnet",
            "provider": "claude-cli",
            "results": [
                {"prompt": "registry gate", "success": True, "latency_ms": 5200, "cost_usd": 0.012, "score": 0.9},
                {"prompt": "evidence shape", "success": True, "latency_ms": 6100, "cost_usd": 0.014, "score": 0.88},
                {"prompt": "failure taxonomy", "success": True, "latency_ms": 5800, "cost_usd": 0.013, "score": 0.86},
            ],
        },
    ],
}


def normalize_report_provenance(
    report: dict[str, Any],
    *,
    ingest_source: str = "uploaded",
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Normalize benchmark provenance and verification into an explicit trust contract."""
    provenance = report.get("provenance")
    verification = report.get("verification")

    if not isinstance(provenance, dict):
        provenance = {}
    if not isinstance(verification, dict):
        verification = {}

    source = provenance.get("source")
    trust = provenance.get("trust")
    label = provenance.get("label")
    artifact = provenance.get("artifact")
    verified_at = provenance.get("verified_at")
    verification_status = verification.get("status")
    verification_message = verification.get("message")

    if ingest_source == "sample" or source == "sample":
        normalized_provenance = {
            "source": "sample",
            "trust": "synthetic",
            "label": str(label or "Synthetic sample report"),
        }
        normalized_verification = {
            "status": "unverified",
            "message": str(verification_message or "Sample data only. Do not treat this report as live proof."),
        }
        return normalized_provenance, normalized_verification

    if (
        ingest_source in {"sidecar_live_run", "sidecar_import"}
        and source in {"sidecar_live_run", "sidecar_import"}
        and verification_status in {"passed", "failed"}
    ):
        normalized_provenance = {
            "source": ingest_source,
            "trust": "live_verified" if verification_status == "passed" else "live_failed",
            "label": str(
                label
                or ("Live verified sidecar proof" if verification_status == "passed" else "Live failed sidecar proof")
            ),
        }
        if isinstance(artifact, str) and artifact:
            normalized_provenance["artifact"] = artifact
        if isinstance(verified_at, str) and verified_at:
            normalized_provenance["verified_at"] = verified_at
        normalized_verification = {
            "status": verification_status,
            "message": str(
                verification_message
                or (
                    "Sidecar-backed proof report is verified."
                    if verification_status == "passed"
                    else "Sidecar-backed proof report failed verification."
                )
            ),
        }
        return normalized_provenance, normalized_verification

    normalized_provenance = {
        "source": "uploaded" if ingest_source == "uploaded" else ingest_source,
        "trust": "uploaded_unverified",
        "label": str(label or "Uploaded unverified report"),
    }
    normalized_verification = {
        "status": "unverified",
        "message": str(
            verification_message
            or "Uploaded JSON is structurally valid but is not live verified proof."
        ),
    }
    return normalized_provenance, normalized_verification


@router.get("/single-file-agents/catalog")
def list_single_file_agent_catalog() -> dict[str, Any]:
    """Return the LATTICE candidate catalog for single-file harness agents."""
    return {
        "ok": True,
        "source_repo": "https://github.com/disler/single-file-agents",
        "incorporation_mode": "lattice-owned-adapted-scripts",
        "agents": SINGLE_FILE_AGENT_CATALOG,
    }


def repo_root() -> Path:
    """Return the LATTICE repository root from this route module."""
    return Path(__file__).resolve().parents[3]


def resolve_repo_path(root: Path, candidate: str) -> Path:
    """Resolve a repository-relative path and reject path escapes."""
    path = (root / candidate).resolve()
    if root != path and root not in path.parents:
        raise HTTPException(status_code=400, detail=f"path escapes repository root: {candidate}")
    return path


def path_exists(root: Path, candidate: str) -> bool:
    """Return true when a repository-relative path exists."""
    if not isinstance(candidate, str) or not candidate:
        return False
    try:
        return resolve_repo_path(root, candidate).exists()
    except HTTPException:
        return False


def normalize_list(value: Any) -> list[str]:
    """Normalize a registry scalar or list field to strings."""
    if isinstance(value, list):
        return [str(item) for item in value]
    if value is None:
        return []
    return [str(value)]


def collect_proof_paths(proof_evidence: Any) -> list[str]:
    """Return proof evidence paths from registry proof metadata."""
    if isinstance(proof_evidence, dict):
        return [
            str(value)
            for key, value in proof_evidence.items()
            if isinstance(value, str) and not str(key).startswith("_")
        ]
    if isinstance(proof_evidence, list):
        return [str(value) for value in proof_evidence]
    if isinstance(proof_evidence, str):
        return [proof_evidence]
    return []


def _is_int_returncode(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _artifact_matches_candidate(root: Path, candidate: str, artifact: str) -> bool:
    try:
        return resolve_repo_path(root, artifact) == resolve_repo_path(root, candidate)
    except HTTPException:
        return False


def proof_verification_status(
    root: Path,
    proof_paths: list[str],
    *,
    expected_capability_id: str | None = None,
) -> dict[str, Any]:
    """Inspect JSON proof artifacts for explicit verification statuses when available."""
    statuses: list[dict[str, str]] = []
    unreadable: list[str] = []
    unverified_json: list[str] = []
    non_json: list[str] = []
    artifact_mismatch: list[str] = []
    capability_mismatch: list[str] = []
    for candidate in proof_paths:
        try:
            path = resolve_repo_path(root, candidate)
        except HTTPException:
            continue
        if not path.exists():
            continue
        if path.suffix != ".json":
            non_json.append(candidate)
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            unreadable.append(candidate)
            continue
        capability_id = payload.get("capability_id")
        artifact = payload.get("artifact")
        verification = payload.get("verification")
        if isinstance(verification, dict):
            status = verification.get("status")
            returncode = verification.get("returncode")
            if not isinstance(status, str) or not status:
                unverified_json.append(candidate)
                continue
            if status not in ALLOWED_PROOF_VERIFICATION_STATUSES:
                statuses.append({"path": candidate, "status": status})
                continue
            if not isinstance(capability_id, str) or not capability_id:
                unverified_json.append(candidate)
                continue
            if expected_capability_id is not None and capability_id != expected_capability_id:
                capability_mismatch.append(candidate)
                continue
            if not isinstance(artifact, str) or not artifact:
                unverified_json.append(candidate)
                continue
            if not _artifact_matches_candidate(root, candidate, artifact):
                artifact_mismatch.append(candidate)
                continue
            if status == "passed" and (not _is_int_returncode(returncode) or returncode != 0):
                unverified_json.append(candidate)
                continue
            if status != "passed" and returncode is not None and not _is_int_returncode(returncode):
                unverified_json.append(candidate)
                continue
            if status in ALLOWED_PROOF_VERIFICATION_STATUSES:
                statuses.append({"path": candidate, "status": status})
                continue
        unverified_json.append(candidate)

    failing = [item["path"] for item in statuses if item["status"] == "failed"]
    review_required = [
        item["path"] for item in statuses if item["status"] in {"review_required", "unverified"}
    ]
    unknown_status = [
        item["path"]
        for item in statuses
        if item["status"] not in {"passed", "failed", "review_required", "unverified"}
    ]
    passed = [item["path"] for item in statuses if item["status"] == "passed"]
    return {
        "statuses": statuses,
        "passed": passed,
        "review_required": review_required + unverified_json + unknown_status + artifact_mismatch + capability_mismatch,
        "failed": failing,
        "unreadable": unreadable,
        "unverified_json": unverified_json,
        "unknown_status": unknown_status,
        "non_json": non_json,
        "artifact_mismatch": artifact_mismatch,
        "capability_mismatch": capability_mismatch,
    }


def infer_serves(capability: dict[str, Any]) -> list[str]:
    """Return LATTICE surfaces served by a capability."""
    explicit = normalize_list(
        capability.get("serves")
        or capability.get("connected_to")
        or capability.get("lattice_serves")
    )
    if explicit:
        return explicit

    surfaces: list[str] = []
    candidates = normalize_list(capability.get("wired_at")) + normalize_list(capability.get("invoked_by"))
    checks = [
        ("meta-harness docs", "meta/harness/"),
        ("capability registry", "analysis/capabilities/"),
        ("FastAPI sidecar", "pixeltable/service/"),
        ("operator console", "src/routes/"),
        ("runtime client", "src/runtime/"),
        ("verification scripts", "scripts/"),
        ("browser benchmark console", "/harness/benchmarks"),
        ("single-file harness jobs", "single-file"),
        ("model-fit loop", "model-fit"),
        ("pre-commit verification", "pre-commit"),
    ]
    for label, needle in checks:
        if any(needle in item for item in candidates) and label not in surfaces:
            surfaces.append(label)
    return surfaces or ["unmapped"]


def run_action(capability: dict[str, Any]) -> dict[str, Any] | None:
    """Return a runnable action descriptor for executable capability rows."""
    capability_id = str(capability.get("id", ""))
    action = RUNNABLE_CAPABILITY_TASKS.get(capability_id)
    if action is None:
        return None
    return {
        "kind": action["kind"],
        "action_id": action["action_id"],
        "capability_id": capability_id,
        "job_id": action["job_id"],
        "label": action["label"],
        "method": "POST",
        "endpoint": "/v1/harness/capabilities/runs",
    }


def run_contract(capability: dict[str, Any]) -> dict[str, Any] | None:
    """Return the explicit allowlisted run contract for executable capability rows."""
    capability_id = str(capability.get("id", ""))
    action = RUNNABLE_CAPABILITY_TASKS.get(capability_id)
    if action is None:
        return None
    return {
        "runnable": True,
        "capability_id": capability_id,
        "action_id": action["action_id"],
        "kind": action["kind"],
        "method": "POST",
        "endpoint": "/v1/harness/capabilities/runs",
        "request": {
            "capability_id": capability_id,
            "timeout_seconds": 60,
        },
        "command": action.get("command"),
        "returns": {
            "ok": "boolean",
            "capability_id": "string",
            "artifact": "repository-relative path",
            "stdout": "string",
            "stderr": "string",
            "verification": {
                "status": "passed | failed",
                "message": "string",
            },
        },
    }


def utc_timestamp() -> str:
    """Return an ISO-8601 UTC timestamp for evidence artifacts."""
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def timestamp_slug() -> str:
    """Return a filesystem-safe UTC timestamp slug."""
    return datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z").replace(":", "-")


def diagnostic_status(root: Path, capability: dict[str, Any]) -> dict[str, Any]:
    """Compute visible diagnostic status for one capability row."""
    state = str(capability.get("state", "")).upper()
    wired_at = normalize_list(capability.get("wired_at"))
    proof_paths = collect_proof_paths(capability.get("proof_evidence"))
    missing_contract = state == "ACTIVE" and not wired_at
    missing_proof_contract = state == "ACTIVE" and not proof_paths
    missing_wires = [path for path in wired_at if "/" in path and not path_exists(root, path)]
    missing_proof = [path for path in proof_paths if not path_exists(root, path)]
    proof_verification = proof_verification_status(
        root,
        proof_paths,
        expected_capability_id=str(capability.get("id", "")) or None,
    )

    if (
        state == "ACTIVE"
        and not missing_contract
        and not missing_proof_contract
        and not missing_wires
        and not missing_proof
        and not proof_verification["failed"]
        and not proof_verification["review_required"]
        and not proof_verification["unreadable"]
        and not proof_verification["non_json"]
        and not proof_verification["artifact_mismatch"]
        and not proof_verification["capability_mismatch"]
    ):
        color = "green"
        label = "pass"
        troubleshooting = (
            "Contract wires and proof evidence are present."
            if not proof_verification["passed"]
            else "Contract wires and proof evidence are present, and verification artifacts passed."
        )
    elif state == "ACTIVE" and proof_verification["unreadable"]:
        color = "red"
        label = "fail"
        troubleshooting = "Proof evidence exists, but at least one artifact is unreadable or malformed JSON."
    elif state == "ACTIVE" and proof_verification["non_json"]:
        color = "amber"
        label = "review-required"
        troubleshooting = "Proof evidence exists, but at least one artifact is non-JSON and cannot be verifier-backed proof."
    elif state == "ACTIVE" and proof_verification["failed"]:
        color = "red"
        label = "fail"
        troubleshooting = "Proof evidence exists, but at least one verifier reported failed."
    elif state == "ACTIVE" and proof_verification["review_required"]:
        color = "amber"
        label = "review-required"
        troubleshooting = "Proof evidence exists, but at least one artifact is review-only, unverified, or fails proof identity checks."
    elif state == "ACTIVE" and missing_proof_contract and not missing_contract and not missing_wires:
        color = "amber"
        label = "contract-only"
        troubleshooting = "Contract wires are present, but no proof evidence is recorded yet."
    elif state == "ACTIVE":
        color = "red"
        label = "fail"
        troubleshooting = "ACTIVE row is missing a contract wire or declared proof evidence artifact."
    elif state == "DEFERRED":
        color = "amber"
        label = "deferred"
        troubleshooting = "Capability is intentionally deferred; check target phase or tracking issue."
    elif state == "BLOCKED":
        color = "red"
        label = "blocked"
        troubleshooting = "Capability is externally blocked; check blocker details before dispatch."
    else:
        color = "red"
        label = "invalid"
        troubleshooting = "Capability has an invalid or missing state."

    return {
        "label": label,
        "color": color,
        "missing_wires": missing_wires,
        "missing_proof": missing_proof,
        "proof_verification": proof_verification,
        "troubleshooting": troubleshooting,
    }


@router.get("/capabilities/matrix")
def get_capability_matrix() -> dict[str, Any]:
    """Return capability registries as a pre-flight diagnostic matrix."""
    root = repo_root()
    registry_dir = root / "analysis" / "capabilities"
    registries: list[dict[str, Any]] = []
    summary = {"green": 0, "amber": 0, "red": 0, "total": 0}

    for path in sorted(registry_dir.glob("*-capability-registry.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        capabilities: list[dict[str, Any]] = []
        for capability in data.get("capabilities", []) or []:
            if not isinstance(capability, dict):
                continue
            status = diagnostic_status(root, capability)
            summary[status["color"]] += 1
            summary["total"] += 1
            capabilities.append(
                {
                    "id": capability.get("id"),
                    "name": capability.get("name"),
                    "surface": capability.get("surface"),
                    "state": capability.get("state"),
                    "description": capability.get("description"),
                    "wired_at": normalize_list(capability.get("wired_at")),
                    "invoked_by": normalize_list(capability.get("invoked_by")),
                    "serves": infer_serves(capability),
                    "proof_evidence": collect_proof_paths(capability.get("proof_evidence")),
                    "run_contract": run_contract(capability),
                    "run_action": run_action(capability),
                    "status": status,
                }
            )
        registries.append(
            {
                "tool": data.get("tool") or path.name.removesuffix("-capability-registry.yaml"),
                "tool_version": data.get("tool_version"),
                "canonical_docs": data.get("canonical_docs"),
                "source_mirror": data.get("source_mirror"),
                "registry_path": path.relative_to(root).as_posix(),
                "capabilities": capabilities,
            }
        )

    return {
        "ok": True,
        "summary": summary,
        "registries": registries,
    }


def build_single_file_agent_run_body(capability_id: str, body: dict[str, Any]) -> dict[str, Any]:
    """Build an allowlisted single-file-agent run body for a runnable capability."""
    action = RUNNABLE_CAPABILITY_TASKS.get(capability_id)
    if action is None:
        raise HTTPException(status_code=400, detail="registered runnable capability_id is required")

    return {
        "job_id": action["job_id"],
        "task": body.get("task", action["task"]),
        "repo_root": body.get("repo_root", "."),
        "output": body.get(
            "output",
            f"meta/harness/docs/sessions/sidecar-{capability_id}-proof-run.json",
        ),
        "expect_paths": body.get("expect_paths", action["expect_paths"]),
        "timeout_seconds": body.get("timeout_seconds", 60),
    }


def validate_timeout_seconds(body: dict[str, Any], default: int = 60) -> int:
    """Return a bounded timeout value accepted by harness runners."""
    timeout_seconds = int(body.get("timeout_seconds", default))
    if timeout_seconds < 1 or timeout_seconds > 120:
        raise HTTPException(status_code=400, detail="timeout_seconds must be between 1 and 120")
    return timeout_seconds


def run_single_file_agent_job(
    body: dict[str, Any],
    capability_id: str | None = None,
) -> dict[str, Any]:
    """Run one registered single-file harness job and return inline-renderable output."""
    job_id = body.get("job_id") or body.get("id")
    if not isinstance(job_id, str) or job_id not in REGISTERED_SINGLE_FILE_JOBS:
        raise HTTPException(status_code=400, detail="registered job_id is required")

    task = body.get("task")
    if not isinstance(task, str) or not task.strip():
        raise HTTPException(status_code=400, detail="task is required")

    timeout_seconds = validate_timeout_seconds(body, default=30)

    root = repo_root()
    job = REGISTERED_SINGLE_FILE_JOBS[job_id]
    script = resolve_repo_path(root, job["lattice_target"])
    output = resolve_repo_path(
        root,
        body.get("output", "meta/harness/docs/sessions/sidecar-codebase-context-proof-run.json"),
    )
    repo = resolve_repo_path(root, body.get("repo_root", "."))
    expect_paths = body.get("expect_paths", [])
    if not isinstance(expect_paths, list) or not all(isinstance(item, str) for item in expect_paths):
        raise HTTPException(status_code=400, detail="expect_paths must be a list of strings")

    command = [
        "uv",
        "run",
        script.as_posix(),
        "--task",
        task,
        "--repo-root",
        repo.as_posix(),
        "--output",
        output.as_posix(),
    ]
    for expected in expect_paths:
        command.extend(["--expect-path", expected])

    started = time.monotonic()
    result = subprocess.run(command, cwd=root, capture_output=True, text=True, check=False, timeout=timeout_seconds)
    latency_ms = int((time.monotonic() - started) * 1000)

    verify_command = ["uv", "run", script.as_posix(), "--verify", output.as_posix(), "--repo-root", repo.as_posix()]
    verify_result = subprocess.run(
        verify_command,
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout_seconds,
    )
    verification_passed = verify_result.returncode == 0

    return {
        "ok": result.returncode == 0 and verification_passed,
        "capability_id": capability_id or job_id,
        "job_id": job_id,
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "latency_ms": latency_ms,
        "artifact": output.relative_to(root).as_posix(),
        "verification": {
            "status": "passed" if verification_passed else "failed",
            "message": "Verifier returned zero." if verification_passed else "Verifier returned a non-zero exit code.",
            "command": verify_command,
            "returncode": verify_result.returncode,
            "stdout": verify_result.stdout,
            "stderr": verify_result.stderr,
        },
    }


def run_script_exit_code_capability(capability_id: str, body: dict[str, Any]) -> dict[str, Any]:
    """Run one allowlisted script contract and persist a proof artifact."""
    action = RUNNABLE_CAPABILITY_TASKS.get(capability_id)
    if action is None or action.get("kind") != "script_exit_code":
        raise HTTPException(status_code=400, detail="registered script capability_id is required")

    command = action.get("command")
    if not isinstance(command, list) or not all(isinstance(item, str) for item in command):
        raise HTTPException(status_code=500, detail=f"invalid command contract for {capability_id}")

    timeout_seconds = validate_timeout_seconds(body)
    root = repo_root()
    output = resolve_repo_path(
        root,
        body.get(
            "output",
            f"meta/harness/docs/sessions/{timestamp_slug()}-{capability_id}-proof.json",
        ),
    )
    output.parent.mkdir(parents=True, exist_ok=True)

    started_at = utc_timestamp()
    started = time.monotonic()
    try:
        result = subprocess.run(
            command,
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout_seconds,
        )
        returncode = result.returncode
        stdout = result.stdout
        stderr = result.stderr
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        returncode = -1
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else f"Timed out after {timeout_seconds} seconds."
        timed_out = True

    latency_ms = int((time.monotonic() - started) * 1000)
    completed_at = utc_timestamp()
    expected_returncode = int(action.get("expected_returncode", 0))
    ok = not timed_out and returncode == expected_returncode
    artifact = output.relative_to(root).as_posix()
    verification = {
        "status": "passed" if ok else "failed",
        "message": (
            f"Command returned expected exit code {expected_returncode}."
            if ok
            else f"Command returned {returncode}, expected {expected_returncode}."
        ),
        "returncode": returncode,
        "expected_returncode": expected_returncode,
        "stdout": stdout,
        "stderr": stderr,
    }
    evidence = {
        "schema_version": 1,
        "capability_id": capability_id,
        "job_id": action["job_id"],
        "run_id": f"{capability_id}-{timestamp_slug()}",
        "started_at": started_at,
        "completed_at": completed_at,
        "ok": ok,
        "command": command,
        "cwd": root.as_posix(),
        "artifact": artifact,
        "returncode": returncode,
        "stdout": stdout,
        "stderr": stderr,
        "verification": verification,
        "metrics": {
            "latency_ms": latency_ms,
            "cost_usd": 0,
            "model": "deterministic",
        },
    }
    output.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    return evidence


@router.post("/capabilities/runs")
def run_capability(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Run one allowlisted harness capability and return inline row output."""
    capability_id = body.get("capability_id") or body.get("capabilityId")
    if not isinstance(capability_id, str):
        raise HTTPException(status_code=400, detail="capability_id is required")
    action = RUNNABLE_CAPABILITY_TASKS.get(capability_id)
    if action is None:
        raise HTTPException(status_code=400, detail="registered runnable capability_id is required")
    if action.get("kind") == "script_exit_code":
        return run_script_exit_code_capability(capability_id, body)
    run_body = build_single_file_agent_run_body(capability_id, body)
    return run_single_file_agent_job(run_body, capability_id=capability_id)


@router.post("/single-file-agents/runs")
def run_single_file_agent(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Run one registered single-file harness agent as a bounded sidecar job."""
    return run_single_file_agent_job(body)


@router.get("/benchmarks/sample-report")
def get_benchmark_sample_report() -> dict[str, Any]:
    """Return a Benchy-compatible sample report for console rendering."""
    provenance, verification = normalize_report_provenance(
        SAMPLE_BENCHMARK_REPORT,
        ingest_source="sample",
    )
    report = dict(SAMPLE_BENCHMARK_REPORT)
    report["provenance"] = provenance
    report["verification"] = verification
    return {"ok": True, "report": report}


@router.post("/benchmarks/reports/validate")
def validate_benchmark_report(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Validate the minimal Benchy-compatible benchmark report shape."""
    report = body.get("report", body)
    if not isinstance(report, dict):
        raise HTTPException(status_code=400, detail="report must be a JSON object")
    benchmark_name = report.get("benchmark_name")
    models = report.get("models")
    if not isinstance(benchmark_name, str) or not benchmark_name.strip():
        raise HTTPException(status_code=400, detail="report.benchmark_name is required")
    if not isinstance(models, list):
        raise HTTPException(status_code=400, detail="report.models must be a list")

    run_count = 0
    for index, model in enumerate(models):
        if not isinstance(model, dict):
            raise HTTPException(status_code=400, detail=f"models[{index}] must be an object")
        if not isinstance(model.get("model"), str) or not model.get("model"):
            raise HTTPException(status_code=400, detail=f"models[{index}].model is required")
        results = model.get("results")
        if not isinstance(results, list):
            raise HTTPException(status_code=400, detail=f"models[{index}].results must be a list")
        run_count += len(results)

    normalized_provenance, normalized_verification = normalize_report_provenance(
        report,
        ingest_source="uploaded",
    )
    normalized_report = dict(report)
    normalized_report["provenance"] = normalized_provenance
    normalized_report["verification"] = normalized_verification

    return {
        "ok": True,
        "benchmark_name": benchmark_name,
        "model_count": len(models),
        "run_count": run_count,
        "provenance": normalized_provenance,
        "verification": normalized_verification,
        "report": normalized_report,
    }
