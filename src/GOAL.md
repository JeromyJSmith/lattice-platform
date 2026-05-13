# Frontend Harness — LATTICE Meta-Harness Control

Owns TanStack Start operator UI: routes in `src/routes/`, server functions in `src/server/runtime/`, TanStack DB collections, React 19 components, Tailwind CSS styling.

## Fitness Function

Score frontend health against **route completeness**, **server function contract**, and **client purity**:

1. **Route inventory**: `find src/routes -name "*.tsx" -o -name "*.ts" | wc -l` matches expected route count (currently 11: home, runtime, viewer, analysis, globe, admin, notebooks, threads, agents, runs, evidence)
2. **No Anthropic SDK in client**: `git grep "import.*Anthropic" -- src/**.tsx src/**.ts | grep -v "^\s*//\" | grep -v "server-only"` returns empty
3. **Every route has a loader**: `git grep -L "loader:" -- src/routes/**.tsx src/routes/**/route.tsx` returns empty (all routes load data)
4. **Server functions return JSON**: all functions in `src/server/runtime/*.ts` call `dispatchRun()` or fetch via `useQuery`, no raw XML/HTML
5. **TanStack DB collections registered**: `src/db/collections.ts` exists and is imported in `src/client.ts`
6. **No `@itwin/core-backend` imports**: `git grep "@itwin/core-backend" -- src/` returns empty

**Baseline score**: `scripts/score-frontend.sh` runs in < 3s, outputs JSON with `routes_live`, `server_functions_valid`, `client_purity`, `loader_coverage`.

## Improvement Loop

Autoresearch loop (on every commit to `src/`):

1. Run `scripts/score-frontend.sh` → baseline snapshot
2. Auto-read `src/routes/` directory, verify each `.tsx` has a loader function or explicit `noLoader` annotation
3. Spawn `claude -p` subprocess to audit import statements, flag Anthropic/backend imports, suggest server-side migrations
4. Write reasoning + refactoring suggestions to `runtime-runs/<run-id>/frontend-lint.md`
5. If `score_after > score_before`, commit; else rollback
6. Flock concurrency: max 1 lint job at a time via `/tmp/vwbridge-frontend.lock`

## Action Catalog

- **Route audit**: `ls -la src/routes/` and verify each has a corresponding entry in router config
- **Loader check**: `git grep -l "loader:" -- src/routes/**/route.tsx | wc -l` should equal non-placeholder route count
- **Import scan**: `git grep -h "^import" -- src/**.tsx | sort -u` review for backend/SDK contamination
- **Component test**: `npm run test --workspace src` runs vitest on component suite (TBD, placeholder for now)
- **Bundle health**: `bun build src/client.ts --external:react --analyze` reports unused dependencies

## Operating Mode

- **Dev server**: `bun dev` starts Vite + TanStack Start with HMR, proxies `/api/` to sidecar at port 8001
- **Build**: `bun build` creates static SSR output in `dist/`, no runtime compilation
- **Client routing**: TanStack Router file-based conventions; `/` = home, `/viewer` = 3D, `/analysis` = deck.gl, `/globe` = Cesium
- **Server functions**: called via `@tanstack/start` adapters, routed to `pixeltable/service` via fetch middleware in `src/middleware.ts`
- **State management**: TanStack Query for async server state, TanStack Store for UI state, no Redux/Zustand
- **Failure mode**: loader fails → error boundary catches, renders fallback UI + offers refresh; server function fails → React Query retry logic (3x exponential backoff)
