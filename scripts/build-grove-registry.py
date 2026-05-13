#!/usr/bin/env python3
"""Build analysis/capabilities/grove-harness-capability-registry.yaml from
the harvest + matrix markdown tables.

Bootstrap rule (per analysis/capabilities/README.md and
.claude/rules/capability-harvest-protocol.md):

- Every capability is DEFERRED at bootstrap (no proofs yet)
- Each DEFERRED row carries `reason`, `target_phase`, `tracking_issue`
- The state is later promoted to ACTIVE in the same commit as the proof
  evidence (handled outside this script)

Runs as:  uv run --no-project python scripts/build-grove-registry.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HARVEST = REPO / "analysis/capabilities/grove-harness-capability-harvest.md"
MATRIX = REPO / "analysis/capabilities/grove-harness-capability-matrix.md"
OUT = REPO / "analysis/capabilities/grove-harness-capability-registry.yaml"

# Map matrix decision + tracking column → curated reason + target_phase
PHASE_MAP = {
    "Phase 2 — VW Bridge": "phase-2-vw-bridge",
    "Phase 2": "phase-2-vw-bridge",
    "Phase 3": "phase-3-3d-assets",
    "Phase 4 — DDC": "phase-4-ddc-integration",
    "Phase 4": "phase-4-ddc-integration",
    "Phase 5": "phase-5-local-ai-genai",
    "Phase 6": "phase-6-production-hardening",
    "post-Phase-2": "post-phase-2",
    "post-Phase-1": "post-phase-1",
}

# Allowed DEFERRED reasons per audit-dead-dna.sh
ALLOWED_REASONS = {
    "awaiting-upstream-dep",
    "cost-prohibitive",
    "out-of-scope-for-current-phase",
    "redundant-with-other-tool",
}

ROW_RE = re.compile(r"^\| `([^`]+)` \| (.*) \|$")


def parse_pipe_row(line: str) -> list[str] | None:
    """Split a markdown table row on `|` boundaries; return cells trimmed.

    Returns None for non-table lines.
    """
    if not line.startswith("| ") or not line.rstrip().endswith(" |"):
        return None
    inner = line.strip().strip("|")
    cells = [c.strip() for c in inner.split("|")]
    return cells


def strip_backticks(s: str) -> str:
    return s.strip().strip("`").strip()


def parse_harvest(path: Path) -> dict[str, dict]:
    """Return { capability_id: {surface, name, source, raw, notes} }."""
    rows: dict[str, dict] = {}
    in_table = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## ") and "Surfaces" in line:
            in_table = True
            continue
        if in_table and line.startswith("## "):
            break
        cells = parse_pipe_row(line)
        if not cells:
            continue
        if len(cells) < 6:
            continue
        cap_id = strip_backticks(cells[0])
        if not cap_id.startswith("grove-"):
            continue
        rows[cap_id] = {
            "surface": strip_backticks(cells[1]),
            "name": strip_backticks(cells[2]),
            "source": strip_backticks(cells[3]),
            "raw": cells[4].strip(),
            "notes": cells[5].strip(),
        }
    return rows


def parse_matrix(path: Path) -> dict[str, dict]:
    """Return { capability_id: {harness, value, risk, decision, verification, tracking} }."""
    rows: dict[str, dict] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = parse_pipe_row(line)
        if not cells:
            continue
        if len(cells) < 9:
            continue
        cap_id = strip_backticks(cells[0])
        if not cap_id.startswith("grove-"):
            continue
        rows[cap_id] = {
            "harness": strip_backticks(cells[1]),
            "value": strip_backticks(cells[2]),
            "risk": strip_backticks(cells[3]),
            "decision": strip_backticks(cells[4]),
            "proof_run": strip_backticks(cells[5]),
            "registry_state_after_proof": strip_backticks(cells[6]),
            "verification": cells[7].strip(),
            "tracking": cells[8].strip(),
        }
    return rows


def reason_for(decision: str, tracking_col: str) -> tuple[str, str]:
    """Decide (reason, target_phase) from matrix row.

    The matrix often encodes the reason in the verification/tracking columns;
    we infer from keywords with a defensive fallback.
    """
    tl = tracking_col.lower()
    if "phase 2" in tl or "vw-itwin" in tl or "vw bridge" in tl or "vwx-mcp" in tl:
        return "awaiting-upstream-dep", "phase-2-vw-bridge"
    if "phase 3" in tl or "3d-assets" in tl:
        return "out-of-scope-for-current-phase", "phase-3-3d-assets"
    if "phase 4" in tl or "ddc" in tl:
        return "out-of-scope-for-current-phase", "phase-4-ddc-integration"
    if "phase 5" in tl or "local-ai" in tl or "genai" in tl:
        return "out-of-scope-for-current-phase", "phase-5-local-ai-genai"
    if "browser-harness" in tl or "browser" in tl:
        return "awaiting-upstream-dep", "phase-2-vw-bridge"
    if "wrapper" in tl:
        return "awaiting-upstream-dep", "phase-2-vw-bridge"
    if "marimo" in tl or "frontend" in tl:
        return "out-of-scope-for-current-phase", "phase-2-frontend-substrate"
    # Default: candidate rows (decision=candidate) get a "promote when proven" target
    return "out-of-scope-for-current-phase", "next-meta-harness-proof-cycle"


def yaml_escape(s: str) -> str:
    """Minimal YAML scalar escaping.

    For complex strings, emit as a double-quoted scalar; otherwise as-is.
    """
    if s == "":
        return "''"
    # If string has special chars, quote it
    if any(c in s for c in [":", "#", "'", '"', "\n", "[", "]", "{", "}", "&", "*", "!", "|", ">", "%", "@", "`"]):
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    if s.lower() in ("true", "false", "yes", "no", "null", "~"):
        return "'" + s + "'"
    # Numeric scalars need quoting if we want them to stay strings
    if re.match(r"^-?\d+(\.\d+)?$", s):
        return "'" + s + "'"
    return s


def fold(s: str, indent: int) -> str:
    """Emit a long string as a single-line YAML scalar with double quotes."""
    pad = " " * indent
    return pad + yaml_escape(s)


def write_registry(harvest: dict, matrix: dict, out: Path) -> int:
    """Emit the registry YAML; return the number of rows."""
    today = "2026-05-13"
    header = (
        "# spec-verified: GROVE_HARNESS/juniper2026 e282f49 2026-05-13\n"
        "tool: grove-harness\n"
        "tool_version: e282f49\n"
        "canonical_docs: /Volumes/PixelTable/GROVE_HARNESS/juniper2026/SPEC_INDEX.md\n"
        f"last_harvested: {today}\n"
        "harvested_by: claude-sonnet-4-6\n"
        "generated_from:\n"
        "  harvest: analysis/capabilities/grove-harness-capability-harvest.md\n"
        "  matrix: analysis/capabilities/grove-harness-capability-matrix.md\n"
        "  builder: scripts/build-grove-registry.py\n"
        "\n"
        "capabilities:\n"
    )

    body: list[str] = []
    n_active = 0
    n_deferred = 0

    for cap_id, h in harvest.items():
        m = matrix.get(cap_id, {})
        surface = h["surface"]
        name = h["name"]
        description = h["raw"]
        notes = h["notes"]
        source = h["source"]
        decision = m.get("decision", "defer")
        tracking_col = m.get("tracking", "")
        harness = m.get("harness", "meta-harness")
        value = m.get("value", "medium")
        risk = m.get("risk", "low")

        # Bootstrap: every row is DEFERRED until a proof run promotes it
        state = "DEFERRED"
        reason, target_phase = reason_for(decision, tracking_col)
        # Sanity: must be in curated list
        if reason not in ALLOWED_REASONS:
            reason = "out-of-scope-for-current-phase"
        tracking_issue = f"TBD-{cap_id}"
        n_deferred += 1

        # Emit YAML row
        body.append(f"  - id: {cap_id}")
        body.append(f"    surface: {surface}")
        body.append(f"    name: {yaml_escape(name)}")
        body.append(f"    state: {state}")
        body.append(f"    description: {yaml_escape(description)}")
        body.append(f"    source: {yaml_escape(source)}")
        body.append(f"    owner_harness: {harness}")
        body.append(f"    matrix_decision: {decision}")
        body.append(f"    value: {value}")
        body.append(f"    risk: {risk}")
        body.append(f"    reason: {reason}")
        body.append(f"    target_phase: {target_phase}")
        body.append(f"    tracking_issue: {yaml_escape(tracking_issue)}")
        if notes:
            body.append(f"    notes: {yaml_escape(notes)}")
        body.append("")

    out.write_text(header + "\n".join(body), encoding="utf-8")
    return n_deferred


def main() -> int:
    if not HARVEST.is_file():
        print(f"missing {HARVEST}", file=sys.stderr)
        return 1
    if not MATRIX.is_file():
        print(f"missing {MATRIX}", file=sys.stderr)
        return 1
    harvest = parse_harvest(HARVEST)
    matrix = parse_matrix(MATRIX)
    if not harvest:
        print("no harvest rows parsed", file=sys.stderr)
        return 1
    n = write_registry(harvest, matrix, OUT)
    print(f"wrote {OUT}")
    print(f"  rows={n}  harvest_rows={len(harvest)}  matrix_rows={len(matrix)}")
    if len(harvest) != len(matrix):
        print(f"  WARNING: harvest ({len(harvest)}) and matrix ({len(matrix)}) row counts differ", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
