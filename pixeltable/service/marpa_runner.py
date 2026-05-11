"""MARPA runner with two backends.

Preferred: spawn a Python subprocess that calls into a libmarpa binding
(`pip install marpa` / `marpa-python`) when available. Fallback: pure-
Python parser implemented in `grammars/marpa.landscape.v1.actions.py` that
walks the simple landscape grammar by hand.

The fallback is exact-equivalent for the `marpa.landscape.v1.0.0` grammar
we ship; it exists so that CI and local dev never depend on a native dep.
"""

from __future__ import annotations

import importlib.util
import logging
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

log = logging.getLogger("vwbridge.marpa")

_HERE = Path(__file__).resolve().parent.parent
ACTIONS_PATH = _HERE / "grammars" / "marpa.landscape.v1.actions.py"
VERSION_PATH = _HERE / "grammars" / "VERSION"


@dataclass
class MarpaResult:
    parse_status: str
    ambiguity_score: float
    record: dict[str, Any] | None
    error_message: str
    runner_kind: str


def _grammar_version() -> str:
    if VERSION_PATH.exists():
        return VERSION_PATH.read_text().strip()
    return "marpa.landscape.v1.0.0"


_ACTIONS_MODULE_NAME = "marpa_actions_v1"


def _load_actions_module():
    """Load grammars/marpa.landscape.v1.actions.py as a module.

    The file lives outside any Python package because its name contains dots.
    We use `spec_from_file_location` and **must** register the resulting
    module in `sys.modules` before `exec_module` — otherwise `@dataclass`
    inside the file fails with `'NoneType' object has no attribute '__dict__'`
    when CPython's dataclass machinery probes `sys.modules[cls.__module__]`
    to detect KW_ONLY types. Cached after first load so re-imports are free.
    """
    cached = sys.modules.get(_ACTIONS_MODULE_NAME)
    if cached is not None:
        return cached
    spec = importlib.util.spec_from_file_location(_ACTIONS_MODULE_NAME, ACTIONS_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load actions module from {ACTIONS_PATH}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[_ACTIONS_MODULE_NAME] = mod
    try:
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
    except Exception:
        sys.modules.pop(_ACTIONS_MODULE_NAME, None)
        raise
    return mod


def _try_subprocess(tokens: list[str], grammar_version: str) -> MarpaResult | None:
    """Future hook: when a libmarpa binding is installed, shell out to a
    helper script. For v0.1.0 we always return None and use the fallback.
    """
    if not shutil.which("marpa-r3"):
        return None
    return None


def _python_fallback(tokens: list[str], grammar_version: str) -> MarpaResult:
    try:
        actions = _load_actions_module()
    except Exception as exc:
        return MarpaResult(
            parse_status="fail",
            ambiguity_score=1.0,
            record=None,
            error_message=f"actions load failed: {exc!s}",
            runner_kind="python.fallback",
        )

    parse_record = getattr(actions, "parse_record", None)
    if parse_record is None:
        return MarpaResult(
            parse_status="fail",
            ambiguity_score=1.0,
            record=None,
            error_message="actions.parse_record not defined",
            runner_kind="python.fallback",
        )

    try:
        ar = parse_record(tokens, grammar_version=grammar_version)
    except Exception as exc:
        return MarpaResult(
            parse_status="fail",
            ambiguity_score=1.0,
            record=None,
            error_message=str(exc),
            runner_kind="python.fallback",
        )

    return MarpaResult(
        parse_status=getattr(ar, "parse_status", "fail"),
        ambiguity_score=float(getattr(ar, "ambiguity_score", 0.0) or 0.0),
        record=getattr(ar, "record", None),
        error_message=getattr(ar, "error_message", "") or "",
        runner_kind="python.fallback",
    )


def run_marpa(tokens: list[str], grammar_version: str | None = None) -> MarpaResult:
    gv = grammar_version or _grammar_version()
    sub = _try_subprocess(tokens, gv)
    if sub is not None:
        return sub
    return _python_fallback(tokens, gv)
