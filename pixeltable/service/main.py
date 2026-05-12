"""FastAPI application — the Pixeltable bridge sidecar.

Run locally (UNIX socket):
    uv run uvicorn service.main:app --uds /tmp/vwbridge-pxt.sock --reload

Run locally (TCP, for testing):
    uv run uvicorn service.main:app --host 127.0.0.1 --port 8765 --reload

All routes return JSON. All write routes require an `Idempotency-Key`
header (8..256 chars). Replays of a key in the last 24h are returned from
cache without re-writing Pixeltable.
"""

from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager
from importlib import import_module
from pathlib import Path

try:
    FastAPI = import_module("fastapi").FastAPI
except ModuleNotFoundError as exc:  # pragma: no cover - environment wiring guard
    raise RuntimeError(
        "fastapi is required for pixeltable/service main; run `uv sync` in `pixeltable/`."
    ) from exc

# Make `service` and `scripts` importable when uvicorn imports us as a module.
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

from scripts._pxt_env import get_client, resolve_home  # noqa: E402
from service import logging as logmod  # noqa: E402
from service.idempotency import IdempotencyStore  # noqa: E402
from service.routes import (
    evidence as r_evidence,
    erp as r_erp,
    georef as r_georef,
    health as r_health,
    itwin as r_itwin,
    marpa as r_marpa,
    reality as r_reality,
    runtime as r_runtime,
    semantic as r_semantic,
    vw as r_vw,
)
from service.settings import Settings, load as load_settings  # noqa: E402
from service.worker import worker_loop  # noqa: E402

import asyncio  # noqa: E402

log = logging.getLogger("vwbridge")


def _autoload_dotenv() -> None:
    """Load `.env.local` from the harness root, then `pixeltable/.env`.

    Both are best-effort; missing files are not errors. Existing env vars
    win (so an explicit `ANTHROPIC_API_KEY=...` from the shell isn't
    overwritten).
    """
    try:
        from dotenv import load_dotenv
    except ModuleNotFoundError:
        return
    harness_env = _HERE.parent.parent / ".env.local"
    sidecar_env = _HERE.parent / ".env"
    for path in (harness_env, sidecar_env):
        if path.exists():
            load_dotenv(path, override=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    _autoload_dotenv()
    logmod.configure()
    settings = load_settings()
    home = resolve_home()
    log.info("starting up; PIXELTABLE_HOME=%s settings=%s", home, settings)
    app.state.settings = settings
    app.state.pxt = get_client()
    app.state.idem = IdempotencyStore(home / ".bridge-idempotency.json")

    stop_event = asyncio.Event()
    app.state.worker_stop = stop_event
    app.state.worker_task = asyncio.create_task(worker_loop(app.state.pxt, stop_event))

    yield

    log.info("shutting down")
    stop_event.set()
    try:
        await asyncio.wait_for(app.state.worker_task, timeout=5.0)
    except asyncio.TimeoutError:
        app.state.worker_task.cancel()


app = FastAPI(
    title="vw-itwin-bridge sidecar",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — local dev only. The browser at localhost:3000 needs to reach the
# sidecar directly for the EventSource (SSE) stream, since TanStack Start
# server functions can't proxy streaming responses cleanly. Lock this down
# behind a real auth token before exposing on a network interface.
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/healthz")
def healthz():
    return {"ok": True, "service": "vw-itwin-bridge", "version": "0.1.0"}


@app.get("/version")
def version():
    return {
        "service":  "vw-itwin-bridge",
        "version":  "0.1.0",
        "contract": "pixeltable.runtime_ledger.v1+vwx-sidecar.v1",
    }


app.include_router(r_runtime.router,  prefix="/v1/runtime",  tags=["runtime"])
app.include_router(r_vw.router,       prefix="/v1/vw",       tags=["vw"])
app.include_router(r_itwin.router,    prefix="/v1/itwin",    tags=["itwin"])
app.include_router(r_marpa.router,    prefix="/v1/marpa",    tags=["marpa"])
app.include_router(r_semantic.router, prefix="/v1/semantic", tags=["semantic"])
app.include_router(r_evidence.router, prefix="/v1/evidence", tags=["evidence"])
app.include_router(r_erp.router,      prefix="/v1/erp",      tags=["erp"])
app.include_router(r_health.router,   prefix="/v1/health",   tags=["health"])
app.include_router(r_georef.router,   prefix="/v1/georef",   tags=["georef"])
app.include_router(r_reality.router,  prefix="/v1/reality",  tags=["reality"])
