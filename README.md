# VW_iTwin_Bridge Runtime MVP

Filesystem-native MetaHarness runtime built on TanStack Start + Router with a reproducibility layer (runtime events, evidence ledger, replay) and a Pixeltable ingestion boundary.

## Scaffold Provenance

Requested command:

```bash
npx @tanstack/cli@latest create VW_iTwin_Bridge --agent --add-ons ai,shadcn,store,better-auth
```

TanStack CLI currently disallows capitals in project names, so scaffold was performed as `vw_itwin_bridge` and then renamed to `VW_iTwin_Bridge`.

## Required Commands

```bash
bun install
bun run dev
```

Build and verify:

```bash
bun run build
bun run verify:runtime
```

TanStack Intent:

```bash
bun run intent:install
bun run intent:list
```

## Environment Variables

Copy `.env.example` to `.env.local` and set values:

- `OPENROUTER_API_KEY`
- `OPENROUTER_DEFAULT_MODEL`
- `BETTER_AUTH_SECRET`
- `BETTER_AUTH_URL`
- `PIXELTABLE_SERVICE_URL`
- `PIXELTABLE_ENABLED`
- `CLAUDE_CODE_BIN`
- `PI_BIN`
- `HERMES_BIN`
- `RUNTIME_RUNS_DIR`

## Security Notes

- OpenRouter calls are server-owned via `@openrouter/sdk`.
- Browser code calls app-owned API routes only.
- Do not expose provider keys in client bundles.

## Runtime Surfaces

- `/runtime`: operator console (Store + Query + Form + Table + Virtual + Hotkeys + Pacer + AI)
- `/threads`, `/threads/$threadId`
- `/agents`, `/agents/$agentId`
- `/runs`, `/runs/$runId`
- `/evidence`, `/evidence/$artifactId`
- `/replay/$runId`
- `/settings/providers`, `/settings/auth`, `/settings/pixeltable`, `/settings/db`, `/settings/intent`

## Reproducibility Artifacts

Each runtime run writes evidence to `runtime-runs/<run-id>/` including:

- `run.yaml`
- `prompt.md`
- `events.jsonl`
- `outcome.md`
- `evidence-manifest.yaml`

Pixeltable ingestion contract lives in `pixeltable/ingestion-contract.yaml`.
