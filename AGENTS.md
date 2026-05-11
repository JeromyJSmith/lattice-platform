<!-- intent-skills:start -->
## Skill Loading

Before substantial work:
- Skill check: run `npx @tanstack/intent@latest list`, or use skills already listed in context.
- Skill guidance: if one local skill clearly matches the task, run `npx @tanstack/intent@latest load <package>#<skill>` and follow the returned `SKILL.md`.
- Monorepos: when working across packages, run the skill check from the workspace root and prefer the local skill for the package being changed.
- Multiple matches: prefer the most specific local skill for the package or concern you are changing; load additional skills only when the task spans multiple packages or concerns.
<!-- intent-skills:end -->

## AGENTS.md — TanStack MetaHarness Runtime MVP

This project is the first runtime/control surface for the VW iTwin Bridge MetaHarness.

## Commands run
Scaffold (requested command; fails because TanStack CLI disallows capitals):
`npx @tanstack/cli@latest create VW_iTwin_Bridge --agent --add-ons ai,shadcn,store,better-auth`

Workaround used to satisfy final path request:
1. `npx @tanstack/cli@latest create vw_itwin_bridge --agent --add-ons ai,shadcn,store,better-auth`
2. Rename folder to `VW_iTwin_Bridge`

Intent:
- `npx @tanstack/intent@latest install`
- `npx @tanstack/intent@latest list`

## Required TanStack surface
- TanStack Start
- TanStack Router
- TanStack CLI
- TanStack Intent
- TanStack Query
- TanStack Table
- TanStack Form
- TanStack Store
- TanStack DB
- TanStack AI
- TanStack Hotkeys
- TanStack Pacer
- TanStack Virtual

## Runtime purpose
The app routes agent work between:
- Claude Code CLI
- Pi runtime
- Hermes runtime
- OpenRouter server-side provider adapter

All runs must be represented as normalized `RuntimeEvent` records.

## Reproducibility
Every task run should produce:
- run directory
- `events.jsonl`
- `prompt.md`
- `outcome.md`
- `evidence-manifest.yaml`

Pixeltable boundary artifacts:
- `pixeltable/tables.yaml`
- `pixeltable/ingestion-contract.yaml`

## Pixeltable bridge sub-project (`pixeltable/`)

The harness no longer talks to Pixeltable directly. All ledger writes go through a Python sidecar that owns the `lattice/execution/*` and `lattice/bridge/*` namespaces. The sidecar lives in `pixeltable/` and is governed by:

- `pixeltable/pyproject.toml` — pinned to `pixeltable==0.6.0` to match the live `/Volumes/PixelTable/.pixeltable` instance and the `MARPA_PLATFORM` body.
- `pixeltable/migrations/0001-0011_*.py` — idempotent, ownership-asserted Pixeltable schema. `migrations/_helpers.py::assert_ownership` blocks any write outside the owned namespaces (`marpa/*` and other foreign roots are never touched).
- `pixeltable/contracts/*.yaml` + `pixeltable/contracts/sidecar.schema.json` — the public ingestion contract. Bumping a contract requires bumping the matching migration.
- `pixeltable/grammars/marpa.landscape.v1.bnf` + `actions.py` + `marpa_seed_psets.yaml` — landscape grammar + seed PSET registry.
- `pixeltable/service/` — FastAPI sidecar (default UDS `/tmp/vwbridge-pxt.sock`, TCP fallback). The harness reaches it through `src/runtime/pixeltable/sidecar-client.ts` (auto SHA256 idempotency keys).
- `pixeltable/scripts/{bootstrap,verify,doctor,load_fixtures}.py` + `Makefile` — local control plane (`make bootstrap migrate-dryrun migrate fixture-load verify`).
- `pixeltable/.schema-snapshot.yaml` — schema drift baseline, enforced by `.github/workflows/pixeltable.yml`.

### Ownership rules (do not violate)
- `lattice/execution/*` and `lattice/bridge/*` are owned by **this** harness.
- `marpa/*` is owned by `MARPA_PLATFORM` and is read-only here.
- Cross-namespace joins use `vw_export_hash` (VW side) and `source_element_id` (IFC GUID, iTwin side).
- `evidence/manifest.yaml` artifacts surface in Pixeltable as rows in `lattice/bridge/evidence/promotion_events`; they are not duplicated, only referenced via `harness_run_refs`.

### Test tiers
- `pixeltable/tests/no_pxt/*` — pure-Python; runs on every PR (`make test-no-pxt`).
- `pixeltable/tests/pxt/*` — full integration against an ephemeral `PXT_HOME` created by the `ephemeral_pxt_home` fixture; runs on every PR through CI and locally via `make test-pxt`.
- `src/runtime/pixeltable/sidecar-client.test.ts` — vitest contract for the harness-side client.

### CI gate
`.github/workflows/pixeltable.yml` runs three jobs on any change under `pixeltable/`, `src/runtime/pixeltable/`, or the ingest script:
1. `no-pxt` — `pytest -m "not pxt"` over `tests/no_pxt`.
2. `pxt-integration` — provisions an ephemeral `PXT_HOME`, runs `bootstrap.py --dry-run` then `bootstrap.py` (with `BRIDGE_SKIP_EMBEDDINGS=1` so 0011 doesn't pull HF weights), `load_fixtures.py`, `verify.py`, then `pytest tests/pxt`.
3. `harness-vitest` — `vitest run src/runtime/pixeltable/sidecar-client.test.ts`.

Schema drift surfaces as a non-zero exit from `verify.py` (with a unified diff in the log).

## Safety
- Never expose `OPENROUTER_API_KEY` to client code.
- OpenRouter is a server-side provider adapter, not the terminal-agent router.
- Preserve generated TanStack conventions and add-ons.

## Deployment Notes
- Build: `bun run build`
- Preview: `bun run preview`
- Runtime evidence path defaults to `./runtime-runs` unless `RUNTIME_RUNS_DIR` is set.
- Pixeltable ingestion is contract-first in this MVP (`pixeltable/ingestion-contract.yaml`) and should be wired to your service endpoint separately.

## Known Gotchas
- TanStack CLI currently rejects project names with uppercase characters; scaffold lowercase then rename folder if uppercase path is required.
- Keep OpenRouter usage in server modules/routes only.
- TanStack Intent output can change as dependencies update; rerun `bun run intent:list` after package upgrades.

## Next Steps
1. Replace adapter placeholders with real Claude/Pi/Hermes process streaming.
2. Connect `scripts/ingest-run-to-pixeltable.ts` to the actual Pixeltable ingestion service.
3. Add auth-gated operator mode using Better Auth session checks.
