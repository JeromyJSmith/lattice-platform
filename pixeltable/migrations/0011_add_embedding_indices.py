"""Attach embedding indices to semantic_sidecars.text_blob and
landscape_entities.summary_text using sentence-transformers/all-mpnet-base-v2.

Idempotent: if an index named `text_blob_idx` / `summary_text_idx` already
exists on the table, this migration is a no-op.
"""

from __future__ import annotations

import os
from collections.abc import Iterable
from importlib import import_module

from migrations._helpers import banner

MIGRATION_ID = "0011_add_embedding_indices"

DEFAULT_MODEL_ID = os.environ.get(
    "EMBED_MODEL_ID", "sentence-transformers/all-mpnet-base-v2"
)


def _existing_index_names(table) -> set[str]:
    """pixeltable 0.6.0 exposes index metadata via `table._tbl_version`. We use
    the public `list_indices()` API when available and fall back to attribute
    introspection so this migration stays portable across patch releases.
    """
    fn = getattr(table, "list_indices", None)
    if callable(fn):
        try:
            rows = fn()
            if not isinstance(rows, Iterable):
                return set()
            names = {
                name
                for row in rows
                if isinstance(row, dict)
                for name in [row.get("name")]
                if isinstance(name, str)
            }
            return names
        except Exception:
            pass
    raw = getattr(table, "_indices", None) or {}
    return set(raw.keys()) if isinstance(raw, dict) else set()


def apply(pxt, dry_run: bool) -> dict:
    banner("0011 embedding indices", dry_run=dry_run)
    hf = import_module("pixeltable.functions.huggingface")
    sentence_transformer = getattr(hf, "sentence_transformer")

    out: dict = {}
    targets = [
        ("lattice/bridge/semantic/semantic_sidecars",  "text_blob",    "text_blob_idx"),
        ("lattice/bridge/semantic/landscape_entities", "summary_text", "summary_text_idx"),
    ]

    embed_fn = sentence_transformer.using(model_id=DEFAULT_MODEL_ID)

    for tbl_path, col, idx_name in targets:
        try:
            t = pxt.get_table(tbl_path)
        except Exception as exc:
            print(f"  {tbl_path}: missing table ({exc!s}); skipping")
            out[tbl_path] = {"action": "skipped-missing-table"}
            continue

        existing = _existing_index_names(t)
        if idx_name in existing:
            print(f"  {tbl_path}.{col} -> exists (idx={idx_name})")
            out[tbl_path] = {"action": "exists", "idx": idx_name}
            continue

        if dry_run:
            print(f"  {tbl_path}.{col} -> would create (idx={idx_name}, model={DEFAULT_MODEL_ID})")
            out[tbl_path] = {"action": "would create", "idx": idx_name}
            continue

        t.add_embedding_index(
            column=col,
            string_embed=embed_fn,
            idx_name=idx_name,
            if_exists="ignore",
        )
        print(f"  {tbl_path}.{col} -> created (idx={idx_name}, model={DEFAULT_MODEL_ID})")
        out[tbl_path] = {"action": "created", "idx": idx_name}

    return out
