"""Semantic actions for marpa.landscape.v1.

Each action consumes a token tuple and returns a structured Python dict that
is stored verbatim in `marpa_parse_runs.partial_parse_json`. The actions are
deliberately defensive: any KeyError or ValueError lowers the ambiguity score
and tags the record as `partial`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class ActionResult:
    parse_status: str         # 'success' | 'partial' | 'fail'
    ambiguity_score: float
    record: dict[str, Any]


def planting(tokens: list[str]) -> ActionResult:
    if len(tokens) < 5:
        return ActionResult("partial", 0.4, {"raw": tokens})
    _, genus, species, size, qty, *rest = tokens + [""]
    cultivar = ""
    notes = ""
    for i, t in enumerate(rest):
        if t.startswith("'") and t.endswith("'"):
            cultivar = t.strip("'")
        elif t == "notes:" and i + 1 < len(rest):
            notes = rest[i + 1]
    return ActionResult(
        "success",
        0.0,
        {
            "kind": "planting",
            "botanical_name": f"{genus} {species}".strip(),
            "cultivar": cultivar,
            "container_size": size,
            "quantity": int(qty) if qty.isdigit() else None,
            "notes": notes,
        },
    )


def irrigation(tokens: list[str]) -> ActionResult:
    if len(tokens) < 5:
        return ActionResult("partial", 0.5, {"raw": tokens})
    _, zone, emitters, flow, drip = tokens[:5]
    return ActionResult(
        "success",
        0.0,
        {
            "kind": "irrigation",
            "zone": zone,
            "emitter_count": int(emitters) if emitters.isdigit() else None,
            "flow_rate": flow,
            "drip_type": drip,
        },
    )


def topography(tokens: list[str]) -> ActionResult:
    if len(tokens) < 5:
        return ActionResult("partial", 0.5, {"raw": tokens})
    _, slope, e_start, e_end, material = tokens[:5]
    return ActionResult(
        "success",
        0.0,
        {
            "kind": "topography",
            "slope": slope,
            "elevation_start": e_start,
            "elevation_end": e_end,
            "material": material,
        },
    )


def hardscape(tokens: list[str]) -> ActionResult:
    if len(tokens) < 5:
        return ActionResult("partial", 0.5, {"raw": tokens})
    _, surface, dx, dy, perm = tokens[:5]
    return ActionResult(
        "success",
        0.0,
        {
            "kind": "hardscape",
            "surface_type": surface,
            "dimension_x": dx,
            "dimension_y": dy,
            "permeability": perm,
        },
    )


DISPATCH: dict[str, Callable[[list[str]], ActionResult]] = {
    "planting": planting,
    "irrigation": irrigation,
    "topography": topography,
    "hardscape": hardscape,
}


@dataclass
class RunResult:
    parse_status: str
    ambiguity_score: float
    record: dict[str, Any] | None
    error_message: str


def parse_record(tokens: list[str], grammar_version: str = "marpa.landscape.v1.0.0") -> RunResult:
    """Entry point used by service.marpa_runner.

    The first token is expected to be the rule name (planting/irrigation/
    topography/hardscape). Anything else returns an error result.
    """
    if not tokens:
        return RunResult("fail", 1.0, None, "empty token stream")
    head = tokens[0].lower()
    fn = DISPATCH.get(head)
    if fn is None:
        return RunResult(
            "fail", 1.0, None,
            f"unknown rule head {head!r}; expected one of {sorted(DISPATCH)}",
        )
    try:
        ar = fn(tokens)
    except Exception as exc:
        return RunResult("fail", 1.0, None, f"{type(exc).__name__}: {exc}")
    return RunResult(ar.parse_status, ar.ambiguity_score, ar.record, "")

