---
description: Author TanStack Start routes and server functions for the LATTICE operator UI, enforce client purity (no Anthropic SDK, no @itwin/core-backend), and validate loader coverage. # allow-forbidden
---

# LATTICE TanStack Start Frontend

The frontend section owns the operator UI under `src/routes/` (11 routes), server
functions under `src/server/runtime/`, TanStack DB collections in
`src/db/collections.ts`, and all React 19 components. The scoring script
`scripts/score-frontend.sh` checks route inventory, loader coverage, client purity,
and server function contract. The dev server starts with `bun dev`.

## When this skill applies

- Adding a new route to `src/routes/` or modifying an existing route
- Adding or refactoring a server function in `src/server/runtime/`
- Fixing a client-purity violation (Anthropic SDK or `@itwin/core-backend` import found) # allow-forbidden
- Running the frontend section cycle: `bash meta/harness/bootstrap/run-autoresearch.sh frontend`
- Route count drifts from the declared 11 in `src/GOAL.md`
- A route is missing a loader function

## How it works

1. Start dev server (if not running):
   ```bash
   bun dev
   ```
   Vite proxies `/api/` to sidecar at `http://localhost:8001`.

2. Audit route inventory:
   ```bash
   find src/routes -name "*.tsx" -o -name "*.ts" | wc -l
   ```
   Expected: 11 routes (home, runtime, viewer, analysis, globe, admin, notebooks,
   threads, agents, runs, evidence).

3. Check every route has a loader:
   ```bash
   git grep -L "loader:" -- src/routes/**/*.tsx src/routes/**/route.tsx
   ```
   Must return empty. Routes without loaders need an explicit `noLoader` annotation
   or a real `loader:` function.

4. Scan for client-purity violations:
   ```bash
   git grep "import.*Anthropic" -- "src/**/*.tsx" "src/**/*.ts" | grep -v "^\s*//"
   git grep "@itwin/core-backend" -- src/ # allow-forbidden
   ```
   Both must return empty.

5. Add a new route following TanStack Router file-based conventions:
   - File: `src/routes/<path>/route.tsx`
   - Must export a `Route` object with `component` and `loader` fields.
   - Async data fetching via `@tanstack/react-query` using `useQuery`.
   - Server-side data via `@tanstack/start` server functions only.

6. Add a server function in `src/server/runtime/<topic>.ts`:
   - Must import from `@tanstack/start` adapters, not from Anthropic SDK directly.
   - Must call `dispatchRun()` or fetch via `useQuery`; return JSON only.

7. Verify TanStack DB collections:
   ```bash
   grep -l "collections" src/db/collections.ts src/client.ts
   ```
   Both files must exist and `collections.ts` must be imported in `client.ts`.

8. Check bundle health:
   ```bash
   bun build src/client.ts --external:react --analyze
   ```
   Review for unexpected dependencies before shipping.

## Files used

- `src/routes/**/*.tsx` — TanStack Router file-based route definitions
- `src/server/runtime/*.ts` — server functions dispatching to sidecar
- `src/db/collections.ts` — TanStack DB collection registry (local, ephemeral)
- `src/client.ts` — client entry point, imports collections
- `src/middleware.ts` — fetch middleware routing to `pixeltable/service`
- `src/GOAL.md` — frontend section fitness function
- `scripts/score-frontend.sh` — section scoring script
- `scripts/pre-commit-docs-check.sh` — docs-drift validator
- `vite.config.ts` — Vite proxy config for `/api/` to sidecar

## Constraints

- Never import Anthropic SDK directly in any `src/` file. Server functions use
  `@tanstack/ai` adapters or the `Codex -p` subprocess via the Python sidecar.
- Never import `@itwin/core-backend` in `src/`. Use `@itwin/core-geometry`, # allow-forbidden
  `@itwin/core-common`, and `@itwin/core-quantity` only.
- All async server state uses `@tanstack/react-query` — no Redux or Zustand.
- `runtime-runs/` is a transient working directory; do not write permanent state there.
- TanStack DB collections are local and ephemeral — they are not a replacement for
  Pixeltable persistence.
- Loader failure must be caught by error boundaries that render fallback UI and
  offer a refresh action, not a blank screen.
- Package management uses `bun` for all JS/TS; `uv` for Python only.
