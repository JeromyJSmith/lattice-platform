# Cloudflare Workers agent — what you can and cannot do in LATTICE

A Cloudflare Worker is an excellent fit for **edge-side** work in this repo. It is the **wrong tool** for anything that touches the local Pixeltable instance, the Vectorworks bridge, or the IfcOpenShell CLI.

## ✅ What Cloudflare Workers CAN handle

| Capability                              | Why it fits at the edge                                                                 |
|-----------------------------------------|------------------------------------------------------------------------------------------|
| Linear ↔ GitHub webhook relay           | Pure HTTP, no local state — see `.github/workflows/linear-sync.yml` for the GH side    |
| Public API for read-only Parquet artifacts | Workers KV / R2 can serve `public/data/*.parquet` exports                              |
| Auth proxy for the operator console     | Better Auth's HTTP API can be fronted by a Worker for SSO / token rotation              |
| Asset CDN for Potree tiles + GLB models | R2 + Workers is the canonical path for serving `public/potree/**` and `public/exports/` |
| Rate-limiter / waiting room             | Edge KV makes per-IP rate limits trivial                                                |
| Scheduled trigger for digest emails     | `cron` triggers are first-class                                                         |
| Forward sanitised analytics             | Pipe operator events to a hosted analytics endpoint without exposing internals          |

## ❌ What Cloudflare Workers CANNOT handle (and why)

| Capability                                | Why it doesn't fit                                                              |
|-------------------------------------------|----------------------------------------------------------------------------------|
| Pixeltable writes                         | Pixeltable runs on the local Mac (embedded PG 16 + PostGIS + pgvector). No remote driver exists. |
| Running `claude -p`                        | The CLI uses local Claude Max auth via keychain — no edge access.                |
| Running Claude Code via `.claude/bin/claude-cli` | Even with a paid-API key set, the worker.py asyncio subprocess model expects a local process. |
| Running IfcOpenShell                       | Native binary + WASM model that depends on a local Python runtime.               |
| Running the FastAPI sidecar                | Sidecar holds the only open Pixeltable session — single-process invariant.       |
| Vectorworks bridge (vwx-mcp / C++ plugin)  | VW is a desktop application; no remote API.                                      |
| LiDAR / point cloud processing (PDAL, Open3D, PotreeConverter) | Native binaries, large file I/O, GB-scale memory.            |
| Cinema 4D / Redshift rendering            | Maxon products run only on desktop.                                              |

## The split, in one line

> **Anything that touches a row in `lattice/*` or a file on Jero's Mac → not Cloudflare.**

## Suggested Cloudflare deployments (when we go remote)

1. `lattice-edge` Worker — proxies the operator console origin, terminates TLS, adds Better Auth headers.
2. `lattice-assets` Worker + R2 bucket — public read for Parquet exports + Potree octrees, signed for write.
3. `lattice-webhooks` Worker — receives GitHub / Linear webhooks, relays to the local sidecar via a Cloudflare Tunnel when the Mac is online.
4. `lattice-cron` Worker — nightly schema drift summary email, BOQ change digest, sidecar uptime monitor.

None of those exist yet. When they do, they live in a sibling Cloudflare Workers repo, not in this one.
