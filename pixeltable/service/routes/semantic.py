"""GET /v1/semantic/search — pixeltable-native similarity over text_blob.

Body:
    { "q": "drought tolerant California native shrub",
      "table": "lattice/bridge/semantic/semantic_sidecars" | "...landscape_entities",
      "k": 10,
      "filter": { "vw_export_hash": "..." }   # optional
    }
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException

from service.deps import get_pxt, require_local_socket_or_token

router = APIRouter(dependencies=[Depends(require_local_socket_or_token)])
log = logging.getLogger("vwbridge.semantic")

_ALLOWED = {
    "lattice/bridge/semantic/semantic_sidecars": "text_blob",
    "lattice/bridge/semantic/landscape_entities": "summary_text",
}


@router.post("/search")
def post_search(body: dict[str, Any] = Body(...), pxt = Depends(get_pxt)):
    table_path = body.get("table") or "lattice/bridge/semantic/semantic_sidecars"
    if table_path not in _ALLOWED:
        raise HTTPException(status_code=400, detail=f"table must be one of {sorted(_ALLOWED)}")
    col = _ALLOWED[table_path]
    q = body.get("q") or ""
    k = int(body.get("k") or 10)
    if not q:
        raise HTTPException(status_code=400, detail="q required")

    t = pxt.get_table(table_path)
    try:
        sim = getattr(t, col).similarity(q)
        rows = (
            t.order_by(sim, asc=False)
             .limit(k)
             .collect()
        )
        try:
            data = [dict(r) for r in rows]
        except Exception:
            data = list(rows)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"similarity failed: {exc!s}")

    return {"ok": True, "table": table_path, "k": k, "rows": data}
