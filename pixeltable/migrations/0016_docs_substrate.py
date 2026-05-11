"""0016 — Documentation Meta-Harness substrate (Amendment 08, 9th section).

Adds 3 tables + 1 view to the existing `lattice/knowledge/` namespace
(created in 0015). Does NOT recreate any 0015 table — `ensure_namespace`
and `ensure_table` are idempotent ("exists" returned for pre-existing).

What this migration creates:

  lattice/knowledge/docs              — pxt.Document corpus per upstream tool doc
  lattice/knowledge/doc_chunks        — DocumentSplitter view + embedding index
  lattice/knowledge/doc_sync_log      — one row per sync operation
  lattice/knowledge/doc_coverage_gaps — detected coverage gaps (tool surface, code, missing doc)

Post-migration table count in lattice/knowledge/ = 8 (3 tables + 2 views from 0015
+ 3 tables from 0016).

Type-surface notes (verified):
  - pxt.Document is real
  - No native geometry type — n/a here
  - Migration is write-once (this file is 0016; do not edit after apply)
"""

from __future__ import annotations

from migrations._helpers import (
    OWNED_PARENTS,
    assert_ownership,
    banner,
    ensure_namespace,
    ensure_table,
)

MIGRATION_ID = "0016_docs_substrate"


def _docs_schema(pxt) -> dict[str, object]:
    return {
        "id":            pxt.String,
        "document":      pxt.Document,
        "source_path":   pxt.String,
        "tool_name":     pxt.String,
        "doc_category":  pxt.String,   # see scripts/doc-mirror-manifest.yaml category_map values
        "page_url":      pxt.String,
        "page_title":    pxt.String,
        "git_sha":       pxt.String,
        "synced_at":     pxt.Timestamp,
        "tool_version":  pxt.String,
    }


def _doc_sync_log_schema(pxt) -> dict[str, object]:
    return {
        "id":                pxt.String,
        "tool_name":         pxt.String,
        "mirror_path":       pxt.String,
        "git_sha_before":    pxt.String,
        "git_sha_after":     pxt.String,
        "pages_added":       pxt.Int,
        "pages_updated":     pxt.Int,
        "pages_deleted":     pxt.Int,
        "sync_at":           pxt.Timestamp,
        "sync_status":       pxt.String,    # ok | partial | failed
        "error_message":     pxt.String,
    }


def _doc_coverage_gaps_schema(pxt) -> dict[str, object]:
    return {
        "id":                pxt.String,
        "tool_name":         pxt.String,
        "gap_type":          pxt.String,    # missing-api-ref | missing-tutorial | stale-doc | broken-link
        "description":       pxt.String,
        "codebase_ref":      pxt.String,    # file:line where the un-documented surface is used
        "doc_ref":           pxt.String,    # which doc *should* cover this
        "severity":          pxt.String,    # critical | high | medium | low
        "detected_at":       pxt.Timestamp,
        "detection_run":     pxt.String,
        "resolved_at":       pxt.Timestamp,
        "resolution_note":   pxt.String,
    }


def _wire_doc_chunks_view(pxt, dry_run: bool) -> dict:
    """DocumentSplitter view + embedding index. Same e5-large-v2 as 0015's
    research_chunks for retrieval consistency."""
    out: dict[str, str] = {}
    if dry_run:
        out["lattice/knowledge/doc_chunks"] = (
            "would create (DocumentSplitter iterator on docs.document with overlap=50) "
            "+ embedding index (e5-large-v2)"
        )
        return out

    from pixeltable.iterators.document import DocumentSplitter
    from pixeltable.functions.huggingface import sentence_transformer

    embed = sentence_transformer.using(model_id="intfloat/e5-large-v2")

    docs = pxt.get_table("lattice/knowledge/docs")
    chunk_view = pxt.create_view(
        "lattice/knowledge/doc_chunks",
        docs,
        iterator=DocumentSplitter.create(
            document=docs.document, separators="paragraph", overlap=50
        ),
        if_exists="ignore",
    )
    chunk_view.add_embedding_index("text", embedding=embed, if_exists="ignore")
    out["lattice/knowledge/doc_chunks"] = "created + embedding index"
    return out


def apply(pxt, dry_run: bool) -> dict:
    assert_ownership(pxt, OWNED_PARENTS)
    banner("0016 docs substrate (Amendment 08, 9th section)", dry_run=dry_run)
    out: dict = {}

    # 1. Ancestor namespaces — idempotent (created by 0001 / 0015).
    out["lattice"] = ensure_namespace(pxt, "lattice", dry_run)
    out["lattice/knowledge"] = ensure_namespace(pxt, "lattice/knowledge", dry_run)
    print(f"  lattice                                      -> {out['lattice']}")
    print(f"  lattice/knowledge                            -> {out['lattice/knowledge']}")

    # 2. New tables (3).
    tables = {
        "lattice/knowledge/docs":                _docs_schema(pxt),
        "lattice/knowledge/doc_sync_log":        _doc_sync_log_schema(pxt),
        "lattice/knowledge/doc_coverage_gaps":   _doc_coverage_gaps_schema(pxt),
    }
    for path, schema in tables.items():
        out[path] = ensure_table(pxt, path, schema, dry_run)
        print(f"  {path:46s} -> {out[path]} ({len(schema)} cols)")

    # 3. doc_chunks view + embedding index.
    out["views"] = _wire_doc_chunks_view(pxt, dry_run)
    for k, v in out["views"].items():
        print(f"  {k:46s} -> {v}")

    return out
