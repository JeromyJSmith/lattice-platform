# GitHub Copilot — workspace instructions for LATTICE

Before suggesting any code in this workspace, **read these two files first**:

1. [`AGENTS.md`](../AGENTS.md) — project-level rules, boundary invariants, locked stack versions.
2. [`CLAUDE.md`](../CLAUDE.md) — user-level conventions (uv, no-optional, security, etc.).

If you're picking up an issue, also read [`meta/AGENT_ONBOARDING.md`](../meta/AGENT_ONBOARDING.md) for the 5-minute boot guide and current priority queue.

## Locked stack (do not propose alternatives)

| Layer       | Choice                                            |
|-------------|---------------------------------------------------|
| JS runtime  | Bun                                               |
| Frontend    | TanStack Start + React 19 + Vite 8                |
| Sidecar     | FastAPI + uvicorn + asyncio (pinned `pixeltable==0.6.0`) |
| Python pkgs | **uv only** (never pip, conda, poetry, pipenv)    |
| 3D engine   | `@thatopen/components` 3.4.6 + Three.js 0.184     |
| Analytics   | deck.gl 9.3.2 + DuckDB WASM 1.33.1 + MapLibre 5  |
| iTwin       | `@itwin/core-geometry` 5.9.2 + `@itwin/core-common` — **never** `@itwin/core-backend** |
| Real agent  | `claude -p` CLI subprocess (Claude Max auth)      |

## Cardinal rules

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

## Style preferences

- Default to **no comments**. Add one only when the WHY is non-obvious (a hidden constraint, a workaround for a specific bug). Don't explain WHAT the code does.
- Prefer `Edit` to `Write` for existing files.
- New files should match existing conventions (see neighbouring files in the same directory).
- TanStack Start API: `.inputValidator()` not `.validator()` (renamed in 1.167+).
- `@tanstack/react-hotkeys`: config is `{hotkey, callback}` not `{key, handler}`, and use `Mod+` prefix (platform-auto).
- Sidecar communication: `resolveSidecarClient()` from `src/runtime/pixeltable/sidecar-client.ts`, never raw `fetch`.

## When in doubt

Stop and ask. Better to clarify than to violate an invariant that costs more to roll back.
