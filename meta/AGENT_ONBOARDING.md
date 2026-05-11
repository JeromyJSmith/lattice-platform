# Agent Onboarding (5-minute read)

You're an AI agent picking up work in LATTICE. Read this top to bottom — then you can pick an issue and start.

## 1. What LATTICE is

A local-first AEC digital-twin platform: Vectorworks → IFC → Pixeltable → operator console (TanStack Start) → two render contexts (ThatOpen 3D + deck.gl analytical) → Cinema 4D handoff. Real agents (Claude via CLI subprocess) write back into Pixeltable as runs stream.

## 2. Boot the stack (do this before any task)

```bash
# Terminal 1 — sidecar (FastAPI + Pixeltable + worker)
cd pixeltable
make sidecar-up-tcp   # binds 127.0.0.1:7770

# Terminal 2 — frontend
bun run dev           # http://localhost:3000

# Verify
curl 127.0.0.1:7770/healthz
curl http://localhost:3000/runtime  # should be HTTP 200
```

If `make sidecar-up-tcp` fails on `PIXELTABLE_HOME not set`, prepend:
```bash
PIXELTABLE_HOME=/Volumes/PixelTable/.pixeltable make sidecar-up-tcp
```

## 3. What's in Pixeltable right now

**36 tables across 4 owned namespaces.** Full reference: [`meta/SCHEMA.md`](SCHEMA.md).

```
lattice/execution/          ← runtime ledger (owned)
  agent_threads / messages / runs / stream_events / artifacts / outcomes

lattice/bridge/             ← cross-system bridges (owned)
  vw/        vectorworks_exports
  ifc/       ifc_elements (26 cols — extended in 0012), ifc_property_sets
  itwin/     itwin_sync_jobs, itwin_changed_elements, connector_versions
  marpa/     marpa_parse_runs, marpa_projects
  semantic/  semantic_sidecars, landscape_entities  (+ pgvector indices)
  evidence/  promotion_events, harness_run_refs
  health/    schema_drift_events, bridge_gap_matrix
  project_georef    ← 67-col coordinate authority (0013)
  plant_assets, site_zones, reference_images  (0012)

lattice/genai/              ← local AI registry (owned, 0012)
  comfyui_jobs / model_registry / training_runs

lattice/reality/            ← reality capture (owned, 0013)
  drone_flights / drone_frames (pxt.Image) / gaussian_splats
  point_cloud_sessions / mirror_state (7 sync flags + divergence)

marpa/                      ← OWNED BY MARPA_PLATFORM (read-only here)
lattice/source, lattice/qa, lattice/budget, lattice/worksheet
                            ← other bodies (DO NOT WRITE)
```

## 3a. Current schema state — rules every agent must know

**Migration trail: 0001–0013** (write-once; never edit a landed migration).

- `0001`–`0011`: namespace + agent runtime + IFC/iTwin/MARPA/semantic/evidence/health tables + embedding indices
- `0012`: extended schema — 26 cols on `ifc_elements`, `plant_assets`, `marpa_projects`, `site_zones`, `reference_images`, full `lattice/genai/*`
- `0013`: georef + reality + mirror — `project_georef` (67 cols), full `lattice/reality/*` namespace

**The pxt.String-for-geometry rule.** Pixeltable 0.6.x has no `pxt.Geometry` type. All geometry columns are `pxt.String` storing WKT (e.g. `POINT(-122.4 37.8)`) or GeoJSON. PostGIS spatial queries layer on at the DuckDB WASM query layer downstream. **Never write `pxt.Geometry` in a migration — it will fail.**

**The migration path.** Migrations live in **`pixeltable/migrations/`** (top of the `pixeltable/` package). It is NOT `pixeltable/service/migrations/`. If you see the wrong path anywhere, fix it.

**The write-once migration rule.** Never edit a landed migration. Always increment the number. Migrations 0001–0013 are immutable; the next one is 0014.

**The owned-parents rule.** Before creating tables in a new namespace (e.g. `lattice/reality`), you must:
1. `pxt.create_dir()` every ancestor first (the helpers do this idempotently)
2. Add the new top-level namespace to `OWNED_PARENTS` in `pixeltable/migrations/_helpers.py`
3. Use `ensure_namespace()` + `ensure_table()` + `ensure_column()` helpers from `_helpers.py`

The ownership guard in `migrations/_helpers.py::assert_ownership` blocks any accidental writes outside the owned tree.

## 4. The sidecar endpoints you can call

**33 endpoints across 10 routers.** Full reference: [`meta/API.md`](API.md). Quick map:

| Router | Endpoints | Notes |
|---|---|---|
| app-level | `/healthz`, `/version` | liveness + build info |
| `/v1/runtime` | 4 endpoints | `events` ingest + `runs` list + `stream-events` (poll) + `stream-events/sse` (push) |
| `/v1/vw` | 1 endpoint | `POST /sidecars` — VW IFC ingest |
| `/v1/itwin` | 3 endpoints | sync-jobs / changed-elements / poll |
| `/v1/marpa` | 1 endpoint | parse-runs |
| `/v1/semantic` | 1 endpoint | semantic search |
| `/v1/evidence` | 1 endpoint | promotions |
| `/v1/health` | 2 endpoints | drift / gap-matrix |
| `/v1/georef` | 11 endpoints | 8 stub-501 ingest + 3 live reads (boundary GeoJSON, transforms, full row) |
| `/v1/reality` | 7 endpoints | 5 stub-501 ingest + 2 live mirror reads |

The TypeScript-side wrapper is at [`src/runtime/pixeltable/sidecar-client.ts`](../src/runtime/pixeltable/sidecar-client.ts) — auto idempotency-key, UDS/TCP modes. **Use it, don't roll your own fetch.**

## 5. How to pick up work

1. Find an issue labelled [`agent-ready`](https://github.com/JeromyJSmith/lattice-platform/issues?q=is%3Aopen+label%3Aagent-ready) (also filter by your area label — `data-layer`, `3d-viewer`, etc.).
2. Create a branch: `agent/<issue-number>-<short-slug>` off `main`.
3. Implement against the acceptance criteria in the issue body.
4. Tests: at minimum `make test-no-pxt`. If you touched `pixeltable/` also run `make test-pxt` locally.
5. Open a PR — `agent-pr-review.yml` will auto-comment with classification.

## 6. What's queued up

The full prioritised backlog is [`meta/FEATURE_BACKLOG.md`](FEATURE_BACKLOG.md). The current priority queue lives at the top of that file. Every unchecked item should have a corresponding GitHub issue with the same title.

## 7. If something is broken

| Symptom | First check |
|---|---|
| Sidecar won't start | `tail /tmp/vwbridge-sidecar.log` — usually `PIXELTABLE_HOME` not exported |
| `claude -p` not found | `which claude` — worker falls back to mock automatically, agent_kind=`mock` |
| HTTP 500 on `/runtime` | `tail /tmp/vwbridge-frontend.log` — most failures are stale module cache, restart bun dev |
| No deltas in EventTimeline | Open devtools Network → EventSource — should see `/v1/runtime/stream-events/sse` open |
| Pixeltable schema drift | `cd pixeltable && make verify` — exits non-zero if live vs snapshot diverge |

The session memory at `~/.claude/projects/-Volumes-PixelTable-VW-iTWIN-Bridge/memory/` has detailed pattern docs for: boot sequence, TanStack Start quirks, sidecar wiring, streaming pipeline, SSE stream events.

## 8. Cardinal rules (see CONTRIBUTING.md for the full list)

1. No `@itwin/core-backend` — Pixeltable owns persistence.
2. No Anthropic SDK in client code — server functions only.
3. uv only for Python — never pip / conda / poetry.
4. IFC4.3 at the boundary — no Revit, no DGN.
5. Pixeltable is the only database.
6. **pxt.String for geometry** — never `pxt.Geometry` (it doesn't exist in 0.6.x).
7. **Write-once migrations** — never edit a landed migration; increment the number.
8. **Owned parents** — adding a new top-level namespace requires extending `OWNED_PARENTS` in `_helpers.py`.

## 9. Mandatory workflow contract

Every agent MUST follow this sequence before ANY commit:

1. Do your work (code, schema, routes, scaffold, etc.)
2. Run the docs-sync check: `bash scripts/pre-commit-docs-check.sh`
3. If it fails → fix the docs first, THEN commit
4. Commit with a message that accurately describes what changed
5. Push

This is non-negotiable. The `docs-sync-check.yml` CI workflow enforces the same checks and will block your PR from merging if you skip step 2–3.

### What the check enforces

- `SCHEMA.md`, `ARCHITECTURE.md`, and root `CLAUDE.md` all declare consistent migration + table counts
- `API.md` and `ARCHITECTURE.md` declare consistent endpoint counts
- Root `CLAUDE.md` contains all 4 mandatory rules (`pxt.String`, `pixeltable/migrations/`, write-once, `create_dir`)
- `FEATURE_BACKLOG.md` retains all required section headers (`GEOREF SYSTEM`, `REALITY CAPTURE`, `DIGITAL TWIN MIRROR`, `3D ASSET PIPELINE`, `LOCAL LLMs`)
- No forbidden strings in changed files: `revit`, `microstation`, `dgnconverter`, `rvtconverter`, `@itwin/core-backend`, `SnapshotDb`, `import Anthropic` (in `.ts`/`.tsx`), `pxt.Geometry`, `pixeltable/service/migrations`

### When you add a migration

You MUST update: `SCHEMA.md`, `ARCHITECTURE.md`, root `CLAUDE.md`, `HANDOFF.md` — all in the same commit as the migration file. The pre-commit hook will catch it if you don't.

### When you add endpoints

You MUST update: `API.md` and `ARCHITECTURE.md` — same commit. The hook checks the counts match.
