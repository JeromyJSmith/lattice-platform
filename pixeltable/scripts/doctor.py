"""Environment diagnostics for the bridge sidecar.

Checks:
  - PIXELTABLE_HOME exists and is writable
  - pixeltable importable and pinned at 0.6.0
  - ifcopenshell, sentence_transformers, fastapi, uvicorn importable
  - sidecar UNIX socket dir is writable
  - Optional: Bentley iTwin client_id/secret presence
"""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

from scripts._pxt_env import resolve_home  # noqa: E402

REQUIRED = [
    ("pixeltable", "0.6.0"),
    ("ifcopenshell", None),
    ("sentence_transformers", None),
    ("fastapi", None),
    ("uvicorn", None),
    ("httpx", None),
    ("yaml", None),
    ("pydantic", None),
    ("typer", None),
    ("rich", None),
]


def check_pkg(name: str, want: str | None) -> tuple[str, bool, str]:
    try:
        mod = importlib.import_module(name)
    except Exception as exc:
        return name, False, f"missing ({exc!s})"
    ver = getattr(mod, "__version__", "?")
    if want and ver != want:
        return name, False, f"installed={ver} pinned={want}"
    return name, True, ver


def main() -> int:
    rc = 0
    print("== bridge doctor ==\n")

    home = resolve_home()
    print(f"PIXELTABLE_HOME = {home}")
    if not home.exists():
        print("  NOT a directory; will be created on first migrate")
    elif not os.access(home, os.W_OK):
        print("  NOT writable")
        rc = 1
    print()

    print("packages:")
    for name, want in REQUIRED:
        n, ok, msg = check_pkg(name, want)
        marker = "OK " if ok else "FAIL"
        print(f"  [{marker}] {n:25s} {msg}")
        if not ok and name in {"pixeltable", "fastapi", "uvicorn"}:
            rc = 1
    print()

    sock = Path(os.environ.get("PXT_BRIDGE_SOCKET", "/tmp/vwbridge-pxt.sock"))
    sock_dir = sock.parent
    print(f"sidecar socket: {sock}")
    print(f"  parent dir writable: {os.access(sock_dir, os.W_OK)}")
    print()

    print("iTwin (optional):")
    for env in ("BENTLEY_CLIENT_ID", "BENTLEY_CLIENT_SECRET", "BENTLEY_SCOPES"):
        v = os.environ.get(env)
        marker = "set" if v else "missing"
        masked = (v[:4] + "***") if v and env.endswith("SECRET") else (v or "")
        print(f"  {env:24s} {marker}  {masked}")

    if rc:
        print("\nfix the FAIL items above before running migrations.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
