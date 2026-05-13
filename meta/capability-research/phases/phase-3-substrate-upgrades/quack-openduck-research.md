# Quack + OpenDuck — async remote DuckDB for the LATTICE substrate

**Logged:** 2026-05-13
**Status:** Research landed. Both adopted. SFAs to follow.
**Target SFA when wired:** `meta/harness/tools/sfa-eval/sfa_duckdb_local_v1.py` stays as the local-disk baseline. The remote variants land as new files (`sfa_duckdb_quack_v1.py`, `sfa_duckdb_openduck_v1.py`) — additive, never overwrites.

## Why this matters now

The current local-disk SFA does its job for single-player runs, and async remote DuckDB unlocks the next layer of the harness:

1. **Concurrent agents share one cache.** Autoresearch ratchet + dashboard + live operator all hit `sfa-eval.duckdb` at the same time without blocking each other.
2. **Persistent connection over the wire.** One round-trip, Arrow IPC batches streaming back. Drops the per-tool-call subprocess boot of the local CLI path entirely.
3. **Run anywhere.** Marimo WASM notebooks, in-tab Bonsai sessions, remote sidecars, and Docker containers all reach the same database over HTTP/gRPC without needing a shared volume mount.

All three are exactly what the LATTICE substrate needs as it fans out.

## The two adoptions — both ACTIVE in the plan

### Quack — official DuckDB client-server protocol

- **Upstream:** DuckDB Labs, `core_nightly` extension repo.
- **Status:** Available in DuckDB v1.5.2 today, stable in DuckDB v2.0.0 (September 2026).
- **Wire:** HTTP — works from anywhere, including browser-side DuckDB-WASM.
- **What it gives us:** Multiple concurrent writers as the headline feature. Official upstream support, ships with DuckDB, no extra extension allow-listing.

### OpenDuck — distributed DuckDB with differential storage

- **Upstream:** CITGuru.
- **Status:** Available now; built from source and loaded as a DuckDB extension.
- **Wire:** gRPC + Arrow IPC — fast binary streaming, protocol defined in `execution.proto`.
- **What it gives us:** Transparent remote `ATTACH` where remote tables are first-class catalog entries that participate in JOINs, CTEs, and the optimizer like local tables. Differential storage and dual execution. Any service that speaks gRPC + Arrow can serve as the backend, so the gateway is swappable.

### Why both

Each tool serves a different LATTICE surface:

| Surface | Tool that fits | Why |
|---|---|---|
| Browser / Marimo WASM execution | **Quack** | HTTP reaches DuckDB-WASM cleanly. |
| Concurrent multi-agent writes | **Quack** | Concurrent-writer support is the official headline. |
| Cross-source JOINs (local cache ⨝ remote operator state) | **OpenDuck** | Remote tables are first-class catalog entries; JOINs with local tables work transparently. |
| Differential storage / snapshot overlays per operator | **OpenDuck** | Differential storage is the headline. |
| Custom gRPC backends (e.g. Pixeltable-fronting query layer) | **OpenDuck** | Any Arrow+gRPC service can plug in. |

Both stay live. Adopting one does not preclude the other — they compose.

## Reference syntax

### Quack

HTTP-attach pattern, per upstream docs. Reaches the Quack server from any DuckDB
client (local, sidecar, WASM):

```python
import duckdb
con = duckdb.connect()
# Quack ships with DuckDB nightly — no manual LOAD needed.
con.execute("ATTACH 'quack://gateway.local:7878/sfa-eval' AS cloud;")
con.execute("SELECT * FROM cloud.plants WHERE height > 50").df()
```

### OpenDuck

```python
import duckdb
con = duckdb.connect(config={"allow_unsigned_extensions": "true"})
con.execute("LOAD '/path/to/openduck.duckdb_extension';")
con.execute(
    "ATTACH 'openduck:sfa-eval?endpoint=http://localhost:7878&token=xxx' AS cloud;"
)
con.execute("SELECT * FROM cloud.plants WHERE height > 50").df()
# Cross-source JOIN — local + remote in one query:
con.execute("""
    SELECT l.id, c.height
    FROM local_observations l
    JOIN cloud.plants c ON l.species = c.species
""").df()
```

## SFA shape when this gets wired

Three rows in the registry, all ACTIVE, all comparable on the same prompt:

| SFA | Connection | Evidence kind |
|---|---|---|
| `sfa_duckdb_local_v1.py` (existing) | Local file via subprocess CLI | Baseline — proves the agent loop |
| `sfa_duckdb_quack_v1.py` (new) | Quack over HTTP, persistent conn | Proves concurrent + browser reach |
| `sfa_duckdb_openduck_v1.py` (new) | OpenDuck over gRPC, persistent conn | Proves cross-source JOIN + differential storage |

The compute loop, tool surface, and Qwen-style fallback parser stay identical
across all three. Only the connection layer changes. That way A/B comparison
on the same prompt is honest and the local baseline never goes away.

## Connection layer sketch (Quack variant)

Drop-in replacement for `_duckdb_sh()`:

```python
_CONN: duckdb.DuckDBPyConnection | None = None

def _get_conn() -> duckdb.DuckDBPyConnection:
    global _CONN
    if _CONN is None:
        _CONN = duckdb.connect()
        _CONN.execute(f"ATTACH 'quack://{GATEWAY}/sfa-eval' AS cloud;")
    return _CONN

def _duck_query(sql: str) -> str:
    con = _get_conn()
    rewritten = _route_to_cloud(sql)  # SHOW TABLES → information_schema, etc.
    rows = con.execute(rewritten).fetchall()
    cols = [d[0] for d in con.description] if con.description else []
    if cols:
        return "\n".join(["\t".join(cols)] + ["\t".join(str(v) for v in r) for r in rows])
    return f"affected {len(rows)} rows"
```

The OpenDuck variant has the same shape — only the `ATTACH` URL and the
extension `LOAD` change.

## What lands first when this unblocks

1. Stand up the gateway (Quack server alongside llama-swap; OpenDuck gateway
   shortly after).
2. Write `sfa_duckdb_quack_v1.py`, run it end-to-end against bonsai-8b, capture
   marker JSON + session JSON.
3. Add the registry row with proof_evidence pointing at the session JSON.
4. Repeat for `sfa_duckdb_openduck_v1.py`.
5. Both rows ACTIVE alongside the local baseline. Three honest evidence kinds.

## Sources

- [Quack: The DuckDB Client-Server Protocol – DuckDB](https://duckdb.org/2026/05/12/quack-remote-protocol)
- [Quack Remote Protocol – DuckDB](https://duckdb.org/quack/)
- [duckdb/duckdb-quack on GitHub](https://github.com/duckdb/duckdb-quack)
- [Quack FAQ – DuckDB](https://duckdb.org/quack/faq)
- [If It Quacks Like a Duck — MotherDuck](https://motherduck.com/blog/duckdb-client-server/)
- [Hacker News discussion](https://news.ycombinator.com/item?id=48111765)
- [CITGuru/openduck on GitHub](https://github.com/CITGuru/openduck)
- [Attach to a DuckDB Database over HTTPS or S3 – DuckDB](https://duckdb.org/docs/stable/guides/network_cloud_storage/duckdb_over_https_or_s3)
- [DuckDB Concurrency docs](https://duckdb.org/docs/current/connect/concurrency)
