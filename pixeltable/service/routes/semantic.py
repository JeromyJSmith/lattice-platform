"""GET /v1/semantic/search — pixeltable-native similarity over text_blob.

Body:
    { "q": "drought tolerant California native shrub",
      "table": "lattice/bridge/semantic/semantic_sidecars" | "...landscape_entities",
      "k": 10,
      "filter": { "vw_export_hash": "..." }   # optional
    }
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException

from service.deps import get_pxt, require_local_socket_or_token

router = APIRouter(dependencies=[Depends(require_local_socket_or_token)])
log = logging.getLogger("vwbridge.semantic")

_ALLOWED = {
    "lattice/bridge/semantic/semantic_sidecars": "text_blob",
    "lattice/bridge/semantic/landscape_entities": "summary_text",
}
_REPO_ROOT = Path(__file__).resolve().parents[3]
_DDC_RUN_ID = "ddc-skills-seed-v1"


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


@router.post("/seed-ddc-skills")
def post_seed_ddc_skills(pxt=Depends(get_pxt)):
    corpus_root = _REPO_ROOT / "skills" / "ddc"
    skill_files = sorted(corpus_root.rglob("SKILL.md"))
    if not skill_files:
        raise HTTPException(status_code=404, detail=f"No SKILL.md files found under {corpus_root}")

    table = pxt.get_table("lattice/bridge/semantic/semantic_sidecars")
    table.delete(table.harness_run_id == _DDC_RUN_ID)

    rows: list[dict[str, Any]] = []
    for skill_file in skill_files:
        rel = skill_file.relative_to(_REPO_ROOT).as_posix()
        source_id = hashlib.sha1(rel.encode("utf-8")).hexdigest()[:16]
        title = skill_file.parent.name
        content = skill_file.read_text(encoding="utf-8", errors="replace")
        rows.append(
            {
                "id": f"ddc-skill::{source_id}",
                "vw_export_hash": "ddc-skill-corpus-v1",
                "source_element_id": rel,
                "ifc_class": "ddc_skill",
                "common_name": title,
                "botanical_name": "",
                "container_size": "",
                "irrigation_zone": "",
                "phenology_notes": "",
                "marpa_seed": False,
                "marpa_status": "not_run",
                "marpa_record": {"source": "skills/ddc", "path": rel, "kind": "ddc_skill"},
                "text_blob": f"{title}\n{content}",
                "raw_sidecar_slice": {"path": rel, "kind": "ddc_skill"},
                "harness_run_id": _DDC_RUN_ID,
                "ingested_at": datetime.now(timezone.utc),
            }
        )

    batch_size = 200
    inserted = 0
    for idx in range(0, len(rows), batch_size):
        batch = rows[idx : idx + batch_size]
        table.insert(batch)
        inserted += len(batch)

    return {"ok": True, "inserted": inserted, "harness_run_id": _DDC_RUN_ID}
