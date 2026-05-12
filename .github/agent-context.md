## LATTICE Agent Context (v1, static)

Generated: 2026-05-12 (UTC)
Source of truth: `meta/harness/docs/` on `feature/meta-harness`
Sourced from: `.github/copilot-instructions.md` at PR #244 head `cfacd0c` (locked stack + cardinal rules)
Regeneration cadence: manual until Phase D docs site lands

This file is a flat, generated-once context export for downstream agents (Copilot, Cursor, Codex CLI, etc.) that cannot or should not traverse the full `meta/harness/` tree. It is NOT a replacement for `CLAUDE.md` or `AGENT.md` — it is a snapshot of the rules in effect at generation time.

## Locked Stack

| Layer       | Choice                                            |
|-------------|---------------------------------------------------|
| JS runtime  | Bun                                               |
| Frontend    | TanStack Start + React 19 + Vite 8                |
| Sidecar     | FastAPI + uvicorn + asyncio (pinned `pixeltable==0.6.0`) |
| Python pkgs | **uv only** (never pip, conda, poetry, pipenv)    |
| 3D engine   | `@thatopen/components` 3.4.6 + Three.js 0.184     |
| Analytics   | deck.gl 9.3.2 + DuckDB WASM 1.33.1 + MapLibre 5  |
| iTwin       | `@itwin/core-geometry` 5.9.2 + `@itwin/core-common` — never @itwin/core-backend |
| Real agent  | `claude -p` CLI subprocess (Claude Max auth)      |

## Cardinal Rules (1–23)

1. **Never propose `@itwin/core-backend`.** Pixeltable replaces SQLite/SnapshotDb/BriefcaseDb.
2. **Never import the Anthropic SDK in client code.** It's removed from `pixeltable/pyproject.toml` for this reason; the CLI subprocess is the live path.
3. **Never use pip, conda, poetry.** All Python ops go through `uv`.
4. **Never write to `marpa/*` or other foreign Pixeltable namespaces.** Ownership is enforced in `pixeltable/migrations/_helpers.py::assert_ownership`.
5. **No Revit, no DGN, no MicroStation.** IFC4.3 is the only authoring boundary.
6. **All coordinates EPSG-normalised** before writing to Pixeltable. Never raw VW internal coordinates.
7. **Plant Style Manager controls all instances.** Never hardcode geometry into individual symbols.
8. **Pixeltable is the only database.** No SQLite, no Postgres, no Redis as a
   primary store. Pixeltable owns all persistent state in this project.
9. **iTwin OSS self-hosted only.** Commercial iTwin tiers (pricing, BDN,
   Activate, Partner Program) are gated content under
   `meta/harness/docs/research/_gated/bentley-commercial/` and are
   DORMANT by default. Never architect against any commercial Bentley
   tier unless the human confirms a gate has fired (see
   `meta/harness/docs/research/_gated/README.md` for the five-gate policy).
10. **Cesium OSS self-hosted wherever possible.** CesiumJS, Cesium 3D Tiles
    OGC standard, and self-hosted terrain/imagery serving stay in the
    architecture. Cesium ion paid SaaS is gated under
    `meta/harness/docs/research/_gated/cesium-commercial/` and is DORMANT.
    Self-hosting expansion is mandatory per doctrine — cost is paid in
    upfront engineering, not recurring SaaS spend.
11. **deck.gl is the analytical overlay layer ONLY — never the 3D scene.**
    The 3D scene is `@thatopen/components` + Three.js (Context A).
    deck.gl operates in Context B as analytical 2.5D overlays.
12. **uv only for Python — uv tool install specifically.** Never pip, conda,
    poetry, pipenv, or pipx. Never `npm install -g` for any Python-adjacent
    tooling. Global installs of any kind are banned.
13. **Mac Apple Silicon first.** All bootstrap, embedding, and ML paths must
    work on M-series Macs. Linux CI is secondary.
14. **`pxt.Geometry` does NOT exist.** Use `pxt.String` (WKT) for all
    geometry columns in Pixeltable. This is enforced by the
    no-forbidden-strings job in docs-sync-check.yml.
15. **Migrations in `pixeltable/migrations/` are WRITE-ONCE.** Never edit
    landed migrations 0001–0016. To change schema, always create the next
    sequential number (currently 0017). Migrations live in
    `pixeltable/migrations/` — never `pixeltable/service/migrations/`
    (that path is in the forbidden-strings list).
16. **CLAUDE.md = plain markdown, NO YAML frontmatter.** Any tool that adds
    frontmatter to CLAUDE.md breaks the claude-md-rules-check job.
17. **SKILL.md = YAML frontmatter REQUIRED, and must be a directory** (i.e.,
    `.claude/skills/<skill-name>/SKILL.md`, never a bare file).
18. **Capability Harvest Protocol is mandatory before tool integration.**
    See `.claude/rules/capability-harvest-protocol.md`. No tool gets wired
    into the codebase without first being harvested into
    `analysis/capabilities/<tool>-capability-registry.yaml`.
19. **Zero Dead DNA Rule.** See `.claude/rules/zero-dead-dna.md`. Unused
    vendored skills, unreferenced YAML, dead imports, and abandoned modules
    are flagged by `scripts/audit-dead-dna.sh` and must be either justified
    or removed.
20. **Anti-Amnesia Rule.** See `.claude/rules/anti-amnesia.md`. Before
    suggesting code for any tool tracked in `scripts/doc-mirror-manifest.yaml`,
    Copilot should reference the doc mirror at similarity threshold 0.7.
    (Note: this is currently inert — see rule 22.)
21. **Embedding model: `intfloat/e5-large-v2`** via the `EMBEDDING_MODEL_ID`
    constant in `pixeltable/_helpers.py`. Never propose alternatives.
22. **PHASE B HAS NOT RUN.** The Pixeltable knowledge substrate exists in
    code (`pixeltable/knowledge/tools.py`) but the tables it queries
    (`research_docs`, `tutorials`, `docs`, `api_reference`, `skills_registry`,
    `doc_coverage_gaps`) have never been created. Calling
    `search_tutorials`, `search_research`, `search_docs`,
    `search_api_reference`, or `get_coverage_gaps` raises
    `TableNotFoundError` today. Until the human confirms Phase B M3 Max
    bootstrap has completed successfully, treat these functions as INERT
    and do NOT propose code that depends on them returning data. Operate
    against the static `.github/agent-context.md` export instead (to be
    added in a later PR).
23. **Pre-merge testing rule.** Nothing merges to `main` until end-to-end
    tested. PR #230 (`feature/meta-harness`) is intentionally kept in Draft
    state until Phase B bootstrap verifies. Do not propose marking it
    Ready-for-Review.

## Substrate Map

- `.claude/rules/`         — runtime rule loader inputs
- `analysis/capabilities/` — capability registry (Harvest Protocol outputs)
- `meta/harness/docs/`     — 9-section meta-harness specification
- `scripts/doc-mirror-manifest.yaml` — docs-sync source of truth
- `pixeltable/knowledge/tools.py`    — knowledge tool registry
- `migrations/0001–0016`   — write-once schema history

## Prohibited

- Revit / DGN / MicroStation imports (IFC4.3 only at boundary)
- Any database other than Pixeltable
- iTwin or Cesium commercial SaaS without Five-Gate Dormancy approval
- deck.gl as a 3D scene layer (analytical overlay only)
- Anthropic SDK in client code (Claude CLI is the agent backend)
- `pxt.Geometry` (does not exist — use `pxt.String` WKT)
- Editing migrations 0001–0016 (write-once)
- YAML frontmatter in CLAUDE.md
- SKILL.md as a single file (must be a directory)

## Reference Docs

The numbered docs spec'd by the original B1 design has not yet been created on `feature/meta-harness`. Pending docs are flagged; live docs that serve the equivalent purpose are linked alongside.

- `meta/harness/docs/01-overview.md` — **pending PR #230 merge**. Live substitute: `meta/harness/docs/README.md` (navigation index) + `meta/harness/HANDOFF-PHASE-2.md` (cold-start orientation).
- `meta/harness/docs/02-capability-harvest-protocol.md` — **pending PR #230 merge**. Live substitute: `.claude/rules/capability-harvest-protocol.md`.
- `meta/harness/docs/03-anti-amnesia.md` — **pending PR #230 merge**. Live substitute: `.claude/rules/anti-amnesia.md`.
- `meta/harness/docs/04-zero-dead-dna.md` — **pending PR #230 merge**. Live substitute: `.claude/rules/zero-dead-dna.md`.
- `meta/harness/docs/05-five-gate-dormancy.md` — **pending PR #230 merge**. Live substitute: `meta/harness/docs/research/_gated/README.md`.
- `meta/harness/docs/06-embedding-policy.md` — **pending PR #230 merge**. Live substitute: `pixeltable/migrations/_helpers.py` (`EMBEDDING_MODEL_ID` shared constant + rationale comment block).
- `meta/harness/docs/07-migration-discipline.md` — **pending PR #230 merge**. Live substitute: cardinal rule 15 above + `pixeltable/migrations/_helpers.py::OWNED_PARENTS` + `assert_ownership`.
- `meta/harness/docs/08-doc-mirror.md` — **pending PR #230 merge**. Live substitute: `scripts/doc-mirror-manifest.yaml` + `meta/harness/docs/AGENT.md` (docs-harness section AGORA spec).
- `meta/harness/docs/09-agent-routing.md` — **pending PR #230 merge**. Live substitute: `.claude/rules/vendored-skills.md` + `meta/harness/PLAN/09-POLYMORPHIC-ARCHITECTURE-AMENDMENT.md`.

When PR #230 merges to `main`, this section will be regenerated to point at the canonical numbered docs.
