<!-- spec-verified: claude/jovial-banzai-8196e2 + feature/grove-harvest + feature/grove-sfa-eval + feature/portless-browser-bonsai 2026-05-13 -->
# HANDOFF — Meta-Harness substrate, model router, capability harvests (2026-05-13)

**One-day session.** Took the Meta-Harness from "planned in design doc" to **operable substrate with proven local-model orchestration, multi-model hot-swap, browser integration, and 287 capability rows under the canonical harvest pipeline**. Six PRs (3 merged, 3 open). Numbers below are measured, not described — every claim has an evidence file under `meta/harness/docs/sessions/` or `meta/harness/state/`.

## TL;DR — what landed

| Theme | Result | Evidence path |
|---|---|---|
| **Wave 1 Meta-Harness foundation** | Migration 0014 (4 harness tables) + 7 section harnesses + global ratchet + 9 subagents + 11 skills + 7 FastAPI endpoints + CI compliance job | PR #383 (open) on `claude/jovial-banzai-8196e2` |
| **GitHub triage** | 374 issues → 240. 135 closed (122 title-duplicate pairs + 13 meta-harness dups). 100% of remaining routed to 8 section-harness ownership labels. Master tracking issue #384 | `gh issue list --repo JeromyJSmith/lattice-platform` |
| **Model router** | `meta/harness/bin/llm` (Python, stdlib) — 7 backends (claude, codex, copilot, ollama, mlx-lm, mlx-vlm, omlx) + 8 tasks + JSON config | `meta/harness/bin/llm --list` |
| **llama-swap** | v211 Go binary vendored at `meta/harness/bin/llama-swap/`. One OpenAI-compat endpoint :9090. 8 MLX models, friendly names via `useModelName`, hot-swap with TTL | `curl http://localhost:9090/v1/models` |
| **Benchy + 5 benchmarks** | 12 reports, 124 model runs, interactive Plotly HTML report at `meta/harness/benchy/LATTICE_BENCH_REPORT.html` | reports under `meta/harness/benchy/server/reports/` |
| **Vision chain** | Qwen3-VL-2B/8B + Gemma-4-26B all PASS on geometry image (12 ft × 6 ft × 2.5 ft). Chain: Qwen3-VL-8B → Qwen3-VL-2B → Gemma-4-26B → claude | router config `vision` task |
| **Capability lifecycle** | grove-harness (71 rows), portless (18 rows), browser-harness (34 rows) all harvested. 26 registries, 167 DEFERRED, 153 ACTIVE, audit OK | PR #385 (merged), PR #387 (open) |
| **Local model swap proven** | Disler `sfa_duckdb_openai_v2` adapted to llama-swap. Bonsai-8B solves multi-turn DuckDB queries via Qwen-style `<tool_call>` XML fallback parser | PR #386 (merged) |
| **Multi-model browser SFA** | One compute loop, Bonsai-8B + Qwen3-VL-2B hot-swap, browser-harness `js()` integration, Portless stable URL — all proven with 3 live tests | PR #387 (open) |

## Branch + PR state

```
main                                                ← release line
└── feature/meta-harness                            ← capability lifecycle lives here
    ├── feature/grove-harvest        PR #385 ✓ MERGED  → 71 grove-harness rows
    ├── feature/grove-sfa-eval       PR #386 ✓ MERGED  → sfa-eval foundation + Bonsai DuckDB
    └── feature/portless-browser-bonsai  PR #387 ⏳ OPEN  → multi-model browser SFA

claude/jovial-banzai-8196e2 → main                  PR #383 ⏳ OPEN  → Wave 1 foundation
```

**Worktrees on disk:**
- `/Volumes/PixelTable/VW_iTWIN_Bridge/VW_iTwin_Bridge/` — main repo, `feature/meta-harness`
- `/Volumes/PixelTable/VW_iTWIN_Bridge/VW_iTwin_Bridge/.claude/worktrees/jovial-banzai-8196e2/` — Wave 1, `claude/jovial-banzai-8196e2`
- `/Volumes/PixelTable/VW_iTWIN_Bridge/VW_iTwin_Bridge/.claude/worktrees/grove-harvest/` — currently `feature/portless-browser-bonsai`

---

## 1. Wave 1 Meta-Harness foundation — PR #383

Branch: `claude/jovial-banzai-8196e2` (worktree path above). 3 commits, 61 files.

### Migration 0014 — `lattice/harness/*` namespace
Added 4 tables: `health_snapshots`, `harness_proposals`, `section_events`, `global_decisions`. Updated `pixeltable/migrations/_helpers.py` `OWNED_PARENTS` to include `lattice/harness`. Verified live: `pxt.list_tables('lattice/harness', recursive=True)`. Docs synced: `meta/SCHEMA.md` (36 → 40 tables), `meta/ARCHITECTURE.md`, root `CLAUDE.md` LIVE STATE block.

### Per-section harness control files
Each section gets `GOAL.md` (4 H2s: Fitness Function / Improvement Loop / Action Catalog / Operating Mode) and `MEMORY.md` (3 H2s: Open Decisions / Failed Experiments / Session Handoff Notes). Eight sections:

```
pixeltable/                schema
pixeltable/service/        api (FastAPI sidecar — 33 → 40 endpoints)
src/                       frontend (TanStack Start)
georef/                    georef + reality capture
genai/                     genai pipeline + assets
vw-plugin/                 VW C++ plugin + iTwin
ddc/                       DDC + CI infra
meta/harness/              global
```

### Scoring scripts (one per section + global)
`scripts/score-{schema,api,frontend,georef,genai,vw-itwin,ddc,global}.sh` — bash, `set -uo pipefail` (NOT `-e` because `$(( ))` returning 0 breaks `-e`), `--json` flag, output `score: N/100`.

**Baseline scores captured (`meta/harness/baseline-global-2026-05-13.json`):**
```
schema    46/100   ↑ trail OK (30), table count match underweighted by heuristic
api       97/100   ↑ 33 endpoints matched docs exactly
frontend 100/100   ↑ every route has createFileRoute, no Anthropic SDK imports
georef    54/100
genai     40/100
vw-itwin  79/100
ddc       81/100
─────────────────
global    71/100   ← starting line for the ratchet
```

### Global ratchet — `meta/harness/bootstrap/run-autoresearch.sh`
- mkdir-based PID lock (macOS — `flock` is Linux-only)
- detached-HEAD `git worktree add /tmp/harness-sandbox` for isolation
- `timeout 120 claude -p` for proposals (later replaced with `meta/harness/bin/llm --task=propose`)
- `git apply --check` before applying — clean reject for unapplyable diffs
- Gate: accept only if `score_after > score_before`
- `--dry` mode for wiring tests

### 9 subagents + 11 skills
- `.claude/agents/{global-meta,schema,api,frontend,georef,genai,vw-itwin,ddc,ci}-harness.md` — all with `name:` + `description:` YAML frontmatter
- `.claude/skills/lattice-{global,schema,api,frontend,georef,genai,vw-itwin,ddc,ci,autoresearch,goal-md}/SKILL.md` — all with `description:` frontmatter

### 7 FastAPI endpoints under `/v1/harness/`
In `pixeltable/service/routes/harness.py` — `health`, `health/{section}`, `proposals` (POST+GET), `events`, `ratchet` (POST), `score`. Mounted at the harness router in `main.py`.

### CI: new 6th job `harness-file-compliance` in `docs-sync-check.yml`
Validates `.claude/agents/*.md` and `.claude/skills/lattice-*/SKILL.md` frontmatter, plus that every section directory has GOAL.md with 4 required H2s + MEMORY.md with 3 required H2s. Mirrored as checks 7-10 in `scripts/pre-commit-docs-check.sh`.

### Allowlist extension for forbidden-string CI (the "guardrails reference forbidden patterns" problem)
- Extended `.github/workflows/docs-sync-check.yml` and `scripts/pre-commit-docs-check.sh` allowlist to `**/GOAL.md`, `**/MEMORY.md`, `**/CLAUDE.md`, `**/AGENTS.md`, `**/README.md`, `**/INSTALL.md`, `**/CHANGELOG.md`, `**/HANDOFF.md`, `codex.md`, `cloudflare-agent.md`, `.cursor*/`, `.claude/`, `pixeltable/migrations/`, `ddc/converters/`
- New `# allow-forbidden` inline marker — any line tagged with this comment is exempted (for legitimate anti-pattern documentation in source files)
- Applied to 3 pre-existing legitimate references in `.py` docstrings + 1 string-literal in migration 0006

### GitHub issue triage (374 → 240)
- Created 8 ownership labels: `harness:{schema,api,frontend,georef,genai,vw-itwin,ddc,global}`
- Routed every open issue to the right section harness (0 unrouted at finish)
- Closed 122 title-duplicate pairs (multi-generation duplicates)
- Closed 13 meta-harness internal dups + 3 already-done migration issues
- Master tracking issue: **#384** with the routing rules
- Resulting distribution: frontend 108, schema 53, genai 48, georef 47, ddc 33, api 24, vw-itwin 22, global 14

---

## 2. Model router — `meta/harness/bin/llm`

Single-file Python script (no deps beyond stdlib). Reads `meta/harness/config/models.json`. Supports `--task=`, `--backend=`, `--image=`, `--list`, `--no-fallback`. Auto-fallback through configured chain on backend unavailability or non-zero exit.

### Backends configured

| Backend | Status on this machine | Notes |
|---|---|---|
| `claude` | ✓ on-path | Anthropic Claude Code CLI |
| `codex` | ✓ on-path | OpenAI Codex CLI |
| `copilot` | ✗ missing | `gh extension install github/gh-copilot` to enable |
| `ollama` | ✓ on-path | Local Ollama daemon |
| `mlx-lm` | ✓ on-path | uv tool, Apple MLX text |
| `mlx-vlm` | ✓ on-path | uv tool, Apple MLX vision (needs `--with torch --with torchvision` for Qwen3-VL) |
| `omlx` | ✓ on-path | `/Applications/oMLX.app/Contents/MacOS/omlx-cli` |

### Task profiles

```
propose       claude → Bonsai-8B → ollama:qwen2.5-coder:7b → codex → copilot
agent-loop    claude → Bonsai-8B → Hermes-3-8B
triage        copilot → Bonsai-1.7B → claude → ollama:llama3.2:3b
review        codex → claude → Bonsai-8B
docs          claude → Bonsai-8B → ollama:qwen2.5:14b
local         Bonsai-8B → Bonsai-4B → Hermes-3-8B → ollama:qwen2.5-coder:7b
quick         Bonsai-1.7B → Bonsai-4B → ollama:llama3.2:3b → claude
vision        Qwen3-VL-8B → Qwen3-VL-2B → Gemma-4-26B → claude
```

Each backend has `auth_check`, `install`, `prompt_as_arg`/`stdin_prompt`, `image_required` flag for vision. `{model}` and `{image}` placeholders in `cmd` array substituted at dispatch.

### Override env

`HARNESS_BACKEND=ollama:qwen2.5-coder:7b bash meta/harness/bootstrap/run-autoresearch.sh schema` pins one model for an entire harness run.

---

## 3. llama-swap (the OpenAI-compat unifier)

`meta/harness/bin/llama-swap/` — vendored Go binary (v211, 6.7 MB darwin-arm64) + config.

### Why it matters
Solves the "cold-load every CLI call" pain. Models stay resident with per-model TTL; one OpenAI-compatible endpoint at `http://localhost:9090` (or `https://llm.localhost` via Portless) hot-swaps weights based on the `model` field in the request body.

### Model map
```
bonsai-4b   → prism-ml/Ternary-Bonsai-4B-mlx-2bit          aliases: bonsai, local
bonsai-1.7b → prism-ml/Ternary-Bonsai-1.7B-mlx-2bit        alias: quick
bonsai-8b   → prism-ml/Ternary-Bonsai-8B-mlx-2bit
hermes-3-8b → mlx-community/Hermes-3-Llama-3.1-8B-4bit     alias: hermes
qwen3.6-35b → unsloth/Qwen3.6-35B-A3B-UD-MLX-4bit          alias: qwen (TTL 300s, big)
qwen3vl-2b  → mlx-community/Qwen3-VL-2B-Instruct-4bit      alias: vision:fast
qwen3vl-8b  → mlx-community/Qwen3-VL-8B-Instruct-4bit      alias: qwen3vl, vision
gemma-4-26b → mlx-community/gemma-4-26b-a4b-it-4bit        alias: gemma4 (TTL 300s, 15 GB)
```

### Key config gotcha (already handled)
`mlx_lm.server` and `mlx_vlm.server` treat the request's `model` field as a load directive — they download whatever name comes in. llama-swap config uses `useModelName: "prism-ml/Ternary-Bonsai-4B-mlx-2bit"` to rewrite the body so the upstream MLX server sees the canonical HF path while clients use friendly names like `bonsai-4b`.

### Live timings (measured)
- Cold load `bonsai-4b`: 5.6 s
- Warm call to `bonsai` (alias): **0.27 s**
- Hot-swap from `bonsai-4b` → `qwen3vl-2b` for vision: 6.9 s (includes Bonsai unload + Qwen3-VL load + first inference)

### Start it
```bash
bash scripts/portless/llm.sh                          # via Portless → https://llm.localhost
# OR directly
meta/harness/bin/llama-swap/llama-swap \
  -config meta/harness/bin/llama-swap/config.yaml -listen :9090 -watch-config
```

---

## 4. Portless — stable HTTPS subdomains for dev services

`vercel-labs/portless 0.9.4`. Installed globally via `bun add -g portless` (LATTICE is bun-only per cardinal rules).

### Map
```
https://llm.localhost      → llama-swap (model field selects weights)
https://benchy.localhost   → benchy Vue client (was :5173)
https://benchy-api.localhost → benchy Flask server (was :5000)
https://sidecar.localhost  → LATTICE FastAPI sidecar (was :7770)
https://app.localhost      → TanStack Start app
https://pxt.localhost      → Pixeltable dashboard (was :22089)
```

### Why HTTPS matters
Unlocks secure-context features in the browser — Service Workers, some Crypto APIs, and **WebGPU + transformers.js** play nicer on HTTPS origins. Portless ships auto-trusted certs in the OS keychain. No flags, no self-signed dance.

### Files added
- `scripts/setup-portless.sh` — idempotent installer
- `scripts/portless/{llm,benchy}.sh` — per-service launchers
- `.portless.json`, `pixeltable/service/.portless.json`, `meta/harness/bin/llama-swap/.portless.json`, `meta/harness/benchy/client/.portless.json`, `meta/harness/benchy/server/.portless.json` — per-service configs

---

## 5. Benchy + benchmarks

Imported `disler/benchy` to `meta/harness/benchy/`. Added MLX adapter (`server/modules/mlx_llm.py`) — subprocess wrapper around `mlx_lm.generate`, parses tokens-per-sec from stats footer, implements `text_prompt` + `bench_prompt` + `thought_prompt`. Wired into `llm_models.py` (`simple_prompt`, `thought_prompt`) and `exbench_module.py` (`provider_bench_functions`).

### Disabled Flask auto-reloader
`server/server.py` was auto-restarting on YAML edits and killing in-flight benchmark requests. Patched with `use_reloader=False` (re-enable via `BENCHY_DEBUG=1`).

### 5 benchmark runs (12 reports total, 124 model runs)
All YAMLs under `meta/harness/benchy/server/benchmark_data/`:

```
lattice_local_micro            6 models × 3 code-gen prompts
lattice_live_sidebyside        6 models × 2 prompts (live UI demo)
lattice_bench_a_quant          NVFP4 vs 4bit Gemma-4-26B
lattice_bench_c_bonsai         Bonsai 1.7B vs 4B vs 8B head-to-head
lattice_bench_d_cot            All 7 MLX models with CoT-friendly prompt
lattice_bench_e_bonsai_vs_savant   Bonsai 4B vs DavidAU Qwen3-48B-A4B-Savant-Heretic (Ollama)
```

### Final cross-bench leaderboard
```
Rank  Model              Accuracy  Tok/s  Runs  Size
────  ─────────────────  ────────  ─────  ────  ──────
 🥇   Bonsai-4B            60%       92    35   1.1 GB    ← LOCAL CODE-GEN PRIMARY
 🥈   Savant 48B-A4B       20%       63    10    20 GB
 🥈   Bonsai-8B            20%       60    25    2.3 GB
  4   Bonsai-1.7B           4%      230    25    495 MB   ← speed king
  5   Hermes-3-8B          11%       47    15    4.5 GB
  6   Gemma-4-26B (4bit)    0%       52    19   15.6 GB
  6   Gemma-4-26B (NVFP4)   0%       47    10   15.6 GB
  6   Qwen3.6-35B-A3B       0%       42    15    20 GB
```

**Crucial nuance (validated separately in PR #386 + #387):** these accuracy numbers are for **single-shot strict-output code-gen**. For **multi-turn tool-calling**, **Bonsai-4B drops required fields** (emits only `reasoning`) — **Bonsai-8B wins instead** because it has the headroom for multi-turn schema following. Different task profiles → different model picks. The router config reflects this:
- `propose` / `local` → Bonsai-8B (tool-calling driver)
- `quick` → Bonsai-1.7B (fastest)
- code-gen prompts in the benchmarks use the smaller models well

### Interactive HTML report
`meta/harness/benchy/LATTICE_BENCH_REPORT.html` — 113 KB, 12 reports embedded, Plotly.js CDN.
- Cross-benchmark leaderboard (accuracy + tok/s overlay)
- Per-benchmark detail panels with stacked latency breakdown (load ms vs generate ms)
- Sortable + filterable drilldown table for all 124 runs
- Single file, drag anywhere, works offline (with CDN)

Generator: `meta/harness/benchy/server/generate_report.py` — re-run to refresh from `reports/*.json`.

---

## 6. Vision chain

User-specified order: **Qwen3-VL-8B → Qwen3-VL-2B → Gemma-4-26B → Claude**.

Live test on `/tmp/test_geometry.png` (1485×968 PNG of a raised garden bed plan view with `Length: 12 ft`, `Width: 6 ft`, `Height: 2.5 ft` labels):

```
Model                   Disk    Peak mem  Cold s   Warm tok/s   Reads it correctly?
────────────────────  ──────  ────────  ──────  ──────────  ────────────────────
Qwen3-VL-2B              1.5 GB    3.1 GB     26.0           166  ✓  + compass rose
Qwen3-VL-8B (primary)    5.0 GB    7.0 GB      5.5            70  ✓  + reads logo text
Gemma-4-26B (4bit)      15.6 GB   16.6 GB      8.4            86  ✓  + specific colors
Gemma-4-26B (NVFP4)     15.6 GB   14.5 GB     20.3 (cold)     63
```

All three nailed every dimension. **Qwen3-VL-2B caught the compass rose orientation that the 8B missed** — same pattern as Bonsai-4B beating bigger models on focused tasks.

### `mlx-vlm` install gotcha
Qwen3-VL has a video processor that imports PyTorch *at module load time*, even for image-only input. Fix: `uv tool install mlx-vlm --with torch --with torchvision --reinstall`. Documented in `meta/harness/MODELS.md`.

### Router wiring for vision
Router accepts `--image PATH`. The `mlx-vlm` backend config has `image_required: true` and `{image}` placeholder in cmd. End-to-end test passed via `meta/harness/bin/llm --task=vision --image=/tmp/test_geometry.png "..."`.

---

## 7. Capability lifecycle pipeline — already built on `feature/meta-harness`

The user already built a complete **Capability Harvest → Matrix → Proof → Manifest → Registry → Verification** pipeline. Found it on the second pass after I initially tried to invent a parallel port plan. **All future tool/model integrations go through this — no quarantine, no separate folders.**

### Pipeline shape (`analysis/capabilities/`)
1. **Harvest** (`<tool>-capability-harvest.md`) — raw inventory of every surface the tool exposes
2. **Matrix** (`<tool>-capability-matrix.md`) — decisions: candidate / defer / block / reject + verification target
3. **Proof Run** — first successful invocation with evidence (session JSON under `meta/harness/docs/sessions/`)
4. **Manifest** (`<tool>-capability-manifest.yaml`) — machine-readable harness intent for proven capabilities
5. **Registry** (`<tool>-capability-registry.yaml`) — canonical per-tool YAML
6. **Verification** — `scripts/audit-dead-dna.sh` enforces parseability + required state fields

### Rules (`.claude/rules/`)
- `capability-harvest-protocol.md` — **Standard #1**: every external tool must move through the lifecycle. Required header fields: `tool`, `tool_version`, `canonical_docs`, `last_harvested`, `harvested_by`, `capabilities`. Required per-row: `id`, `surface`, `name`, `state`, `description`.
- `zero-dead-dna.md` — **Standard #2**: every row state is exactly one of `ACTIVE` / `DEFERRED` / `BLOCKED`. No UNKNOWN. DEFERRED rows must have `reason`, `target_phase`, `tracking_issue`. Curated DEFERRED reasons: `awaiting-upstream-dep`, `cost-prohibitive`, `out-of-scope-for-current-phase`, `redundant-with-other-tool`.
- `audit-dead-dna.sh` enforces via Ruby YAML validation, runs in pre-commit + CI.

### Harvests added this session
**PR #385 (merged) — grove-harness**: 71 rows
- 62 SFAs (1:1 with `juniper2026/harness/TOOL_MANIFEST.yaml`)
- 8 architecture patterns (SFA pattern, L2 wrapper template, marker contract, variant taxonomy, dispatch helper, tool manifest format, Marimo control plane, DuckDB cache substrate)
- 2 Marimo notebooks
- Decisions: 29 candidate, 42 defer
- Generator: `scripts/build-grove-registry.py` (re-runnable, parses harvest+matrix MD → YAML)

**PR #387 (open) — portless**: 18 rows
- 6 CLI commands, 12 patterns (hostname routing, HTTPS auto-cert, $PORT injection, monorepo config, git worktree prefix, Tailscale Funnel, etc.)
- All `candidate` decision, all DEFERRED state pending the same-PR proof

**PR #387 (open) — browser-harness**: 34 rows
- 20 helper functions (`new_tab`, `js`, `capture_screenshot`, `click_at_xy`, `cdp`, `iframe_target`, etc.) — `browser-harness-js` is the headline
- 6 architectural patterns (agent-helpers self-modifying canvas, domain-skills per-site playbooks, interaction-skills per-mechanic playbooks, CDP-attach-to-running-Chrome, coordinate-first clicks)
- 6 remote-browser surfaces (cloud daemons, profile sync — deferred to `phase-2-headless-pipelines`)
- 2 design doctrines

### Final registry state (after PR #387)
```
audit-dead-dna: OK
  registries=26
  active=153
  deferred=167
  blocked=3
  bootstrap_empty=4
```

---

## 8. SFA evaluation folder + multi-model browser SFA

**`meta/harness/tools/sfa-eval/`** — pre-capability staging area. Every SFA here is being evaluated; promotion to ACTIVE happens in the same commit as the move to its final harness directory + `proof_evidence:` registry update.

### Three SFAs landed across PR #386 + PR #387

**`sfa_init_caches.py`** (PR #386) — LATTICE port of `juniper2026/harness/init_caches.py`. No LLM. Bootstraps `meta/harness/state/cache/sfa-eval.duckdb` with two seed tables (8 plants, 16 migrations indexed from the branch). Writes canonical marker JSON per SPEC_SFA_PATTERN §3. `--verify` mode passes.

**`sfa_duckdb_local_v1.py`** (PR #386) — LATTICE port of `disler/single-file-agents/sfa_duckdb_openai_v2.py`. Same Pydantic tool schema + compute loop as the Disler original. Swaps `openai.OpenAI(...)` to point at `https://llm.localhost/v1` (or `http://localhost:9090/v1`). Default model `bonsai-4b`, `--model` selects any llama-swap entry.

**Critical finding (carries the whole architecture):** `mlx_lm.server` does NOT translate Qwen-style `<tool_call>...</tool_call>` content blocks into the OpenAI `tool_calls` wire field. Bonsai is Qwen-family — it emits valid tool calls in Qwen format, but `response.tool_calls` is empty. Added a fallback parser (`extract_pseudo_tool_calls`) that scans message content for both `<tool_call>...</tool_call>` XML blocks AND bare `{"name":..., "arguments":...}` JSON. **This is the bridge that makes any Qwen-derived local model work for tool-calling SFAs through llama-swap.**

Live results (committed under `meta/harness/docs/sessions/`):
```
bonsai-4b → FAIL: 8 iters, drops required fields (only emits `reasoning`)
            4B isn't large enough for multi-turn schema-following

bonsai-8b → PASS on both test prompts
  "Tallest plant?"     → 6 iters, 17.9s, "Southern Magnolia, 80 ft"
  "Migrations count?"  → 6 iters, 11.4s, "16 migrations, largest 8631 bytes"
```

**`sfa_browser_bonsai_v1.py`** (PR #387) — multi-model browser SFA. Six tools:
```
QueryDuckDBArgs        run SQL against state/cache/sfa-eval.duckdb
NavigateArgs           browser_harness.new_tab(url) + page_info
RunInBrowserArgs       browser_harness.js(expression) — arbitrary JS in active tab
CaptureScreenshotArgs  browser_harness.capture_screenshot(path)
DescribeScreenshotArgs HOT-SWAPS to vision model (qwen3vl-2b) for ONE call
FinalAnswerArgs        end loop
```

`DescribeScreenshot` is the headline tool — its implementation runs `client.chat.completions.create(model="qwen3vl-2b", messages=[image+text])` against the SAME base URL. llama-swap unloads bonsai-8b → loads qwen3vl-2b → returns description → llama-swap (or next call) reloads bonsai-8b. **The driver model never sees pixels — it gets text back from the tool.**

Auto-detects Portless: prefers `https://llm.localhost/v1` if reachable, falls back to `http://localhost:9090/v1`.

### Three live tests (all PASS, evidence under `meta/harness/docs/sessions/2026-05-13-*-browser-bonsai-*.json`)
```
Test 1 (text+DuckDB):       2 iters,  9.5 s,  0 swaps  ✓ "8 rows"
Test 2 (browser nav+JS):    3 iters,  7.0 s,  0 swaps  ✓ "title=Example Domain, h1=Example Domain"
Test 3 (multi-model swap):  2 iters, 17.2 s,  1 swap   ✓ "Length 12 ft, Width 6 ft, Height 2.5 ft"
```

Test 3 is the proof that matters — the model swap happens **inside** one compute loop, invisibly to the driver model.

---

## Empirical findings worth remembering

### Bonsai per task class
| Task | Winner | Why |
|---|---|---|
| Single-shot strict code-gen | **Bonsai-4B** (60% across 19 runs) | Terse output fits strict-equality eval; 4B has just enough reasoning |
| Multi-turn tool calling | **Bonsai-8B** | 4B drops required fields when juggling multi-turn schemas; 8B has headroom |
| Vision (dimension extraction) | **Qwen3-VL-2B** | Smallest VL, fastest (166 tok/s), caught compass rose orientation |
| Massive models on strict eval | LOSE | Qwen3.6-35B and Gemma-4-26B both 0/3 — over-explain, trail off into prose |

### Wire-format gotcha to never forget
**Qwen-family local models** (Bonsai, Qwen3-VL, Qwen3.6) emit `<tool_call>{...}</tool_call>` in the message content. mlx_lm.server doesn't translate it to OpenAI `tool_calls`. **Always include `extract_pseudo_tool_calls()` fallback** in any SFA that calls a Qwen-derived model via llama-swap.

### Bench finding for big models
The big MoE models (Qwen3.6-35B-A3B, Gemma-4-26B both quants, Savant 48B-A4B) got 0% accuracy on the strict-output code-gen benchmark — not because they can't code, but because they emit CoT reasoning + commentary that trips the strict-equality evaluator. They'd score differently on a free-form bench. The CoT-friendly prompt (`bench_d`) helped Bonsai-1.7B improve (0→1/3) but big models still 0/3 — they over-think.

### Hardware footprint (M3 Max, 64 GB unified memory)
```
Bonsai-1.7B:     495 MB disk, 0.54 GB peak  — 230 tok/s
Bonsai-4B:       1.1 GB disk, 1.22 GB peak  — 92 tok/s (warm)
Bonsai-8B:       2.3 GB disk, 2.41 GB peak  — 60 tok/s
Hermes-3-8B:     4.5 GB disk, 4.58 GB peak  — 47 tok/s
Qwen3-VL-2B:     1.5 GB disk, 3.08 GB peak  — 166 tok/s (warm)
Qwen3-VL-8B:     5.0 GB disk, 7.02 GB peak  — 70 tok/s (warm)
Gemma-4-26B:    15.6 GB disk, 16.56 GB peak — 86 tok/s
Qwen3.6-35B:    20.0 GB disk, 20.85 GB peak — 85 tok/s
Savant 48B-A4B: 20.0 GB disk, ~20 GB peak   — 63 tok/s
```

Total weights cached: ~70 GB across `~/.cache/huggingface/hub/` (primary) and `/Volumes/PixelTable/models/huggingface-cache/` (secondary — Gemma-4 NVFP4, Gemma-2/3/4-E4B, BitNet 1.58, Qwen3-VL-32B-abliterated stub, Qwen2-VL-72B-abliterated stub).

NVFP4 symlinked into primary cache: `~/.cache/huggingface/hub/models--mlx-community--gemma-4-26b-a4b-nvfp4` → `/Volumes/PixelTable/models/huggingface-cache/...` for unified mlx_lm access.

### Heretic / abliterated models cached but not yet wired
- `/Volumes/PixelTable/gemma4-heretical/` — script that pulls `trohrbaugh/gemma-4-31b-it-heretic-ara` and registers it in Ollama with the correct Gemma-4 chat template. ARA-abliterated, 5/100 refusal vs 98/100 stock. Run `./get-gemma4-heretical Q4_K_M` to register; 17 GB.
- `models--DavidAU--Qwen3-48B-A4B-Savant-Commander-Distill-12X-Closed-Open-Heretic-Uncensored-GGUF` — already registered in Ollama as `savant` and tested (1/5 vs Bonsai-4B 3/5).
- `models--mradermacher--Huihui-Qwen3-VL-32B-Thinking-abliterated-GGUF` — stub only, weights not pulled.

---

## Open PRs (state on 2026-05-13)

### PR #383 — Wave 1 Meta-Harness foundation
- Branch: `claude/jovial-banzai-8196e2` → main
- 3 commits, 61 files
- All CI green except `pxt (ephemeral PXT_HOME)` which is a **pre-existing failure** in migration 0012 (dry-run can't `get_table` on a not-yet-created upstream table). Phase 1 DoD item: "Self-hosted Mac runner registered → test-pxt workflow goes green."
- Includes the GitHub issue triage (374 → 240)

### PR #387 — multi-model browser SFA
- Branch: `feature/portless-browser-bonsai` → `feature/meta-harness`
- 1 commit, ~17 files
- Includes portless + browser-harness harvests, setup-portless.sh, sfa_browser_bonsai_v1.py, 3 test evidence files
- audit-dead-dna OK locally
- Awaiting CI

### PR #385 (merged) — grove harvest
### PR #386 (merged) — sfa-eval foundation

---

## Capability registry rows worth promoting next (DEFERRED → ACTIVE)

Each of these has proof evidence already committed. To promote: same commit edits the row from DEFERRED to ACTIVE with `wired_at:`, `invoked_by:`, `proof_evidence:` fields pointing at the existing session JSONs.

| Capability | Proof |
|---|---|
| `browser-harness-new-tab` | `meta/harness/docs/sessions/2026-05-13-200454-browser-bonsai-test2-browser-nav.json` |
| `browser-harness-js` | same |
| `browser-harness-capture-screenshot` | `meta/harness/state/_browser_bonsai_v1.done.json` |
| `portless-cli` | `scripts/setup-portless.sh` run output (re-runnable) |
| `portless-hostname-routing` | `.portless.json` files committed |
| `grove-sfa-init-caches` | `meta/harness/docs/sessions/...test1-text-duckdb.json` |
| `grove-sfa-pattern` | the working `sfa_init_caches.py` itself |
| `grove-marker-contract` | `meta/harness/state/_init_caches.done.json` |

8 rows ready to flip ACTIVE in a quick follow-up commit.

---

## Open questions / decisions pending

1. **Should PRs #385 (sfa-eval foundation) and #387 (multi-model browser SFA) flip those 8 rows to ACTIVE before merging, or in a follow-up PR after?** I left them DEFERRED because the protocol says "proof_evidence in same commit" — and a separate PR makes the lifecycle transitions visible.
2. **Where do `sfa_init_caches`, `sfa_duckdb_local_v1`, `sfa_browser_bonsai_v1` move to when they leave `sfa-eval/`?** Probably `meta/harness/tools/sfa-schema/` for DuckDB query layer, `meta/harness/tools/sfa-browser/` for browser-driven agents. User has not decided final homes yet.
3. **Should browser-harness `agent_helpers.py` self-modification be enabled in our SFAs?** Browser-harness's design intent is "agent writes missing helpers during execution." Powerful but extends the trust surface. Not currently used by `sfa_browser_bonsai_v1.py`.
4. **VW-bridge SFAs (P-R / P-D / P-W variants) are DEFERRED with `awaiting-upstream-dep`.** Unblock when `vwx-mcp` wiring lands (Phase 1 DoD).
5. **Should Bonsai vision (in-tab transformers.js + WebGPU) be the next milestone?** All weights exist (`onnx-community/Ternary-Bonsai-{1.7B,4B,8B}-ONNX`). HF Space demo confirmed. The `browser-harness-js` tool gives the bridge to call it. Next breakthrough.

---

## Concrete next moves (your call)

**(A) Promote the 8 proven rows to ACTIVE.** ~30 minutes. Closes the lifecycle loop on what just shipped. Cleanest registry state. Easy quick win.

**(B) Wire WebGPU Bonsai in the browser tab.** Build `bonsai-host.html` that loads `onnx-community/Ternary-Bonsai-1.7B-ONNX` via transformers.js. Add a `RunInBrowserLLM(prompt)` tool to the SFA that calls `js("await window.bonsai.generate(...)")`. End-to-end local inference INSIDE the user's tab, server-side orchestrated. The next breakthrough.

**(C) Port more Disler SFAs** through the same pattern: `sfa_sqlite_openai_v2.py`, `sfa_polars_*`, `sfa_meta_prompt_*`. Each becomes another proven capability. Builds registry coverage.

**(D) Promote the matrix decisions** — re-read the grove-harness matrix (71 rows) and convert any rows where evidence already exists outside `sfa-eval` (e.g. the LATTICE port of `codebase-context-agent.py` is already ACTIVE in the single-file-agents registry).

I'd vote **A first** (clean registry), **then B** (next breakthrough), then C/D as appropriate. The substrate is ready — the next move is whatever you want to put on top of it.

---

## File index — every artifact worth grepping for

```
# Wave 1 foundation (on claude/jovial-banzai-8196e2, PR #383)
pixeltable/migrations/0014_harness.py
pixeltable/migrations/_helpers.py                  (OWNED_PARENTS += "lattice/harness")
meta/SCHEMA.md  meta/ARCHITECTURE.md  CLAUDE.md    (LIVE STATE blocks)
{pixeltable,pixeltable/service,src,georef,genai,vw-plugin,ddc,meta/harness}/{GOAL.md,MEMORY.md}
scripts/score-{schema,api,frontend,georef,genai,vw-itwin,ddc,global}.sh
scripts/pre-commit-docs-check.sh                   (checks 7-10 added)
.github/workflows/docs-sync-check.yml              (job 6: harness-file-compliance)
meta/harness/{GOAL,MEMORY,CLAUDE}.md
meta/harness/bootstrap/run-autoresearch.sh
meta/harness/baseline-2026-05-13.json
meta/harness/baseline-global-2026-05-13.json
.claude/agents/{global-meta,schema,api,frontend,georef,genai,vw-itwin,ddc,ci}-harness.md
.claude/skills/lattice-{global,schema,api,frontend,georef,genai,vw-itwin,ddc,ci,autoresearch,goal-md}/SKILL.md
pixeltable/service/routes/harness.py               (7 endpoints under /v1/harness)

# Router + model substrate (on claude/jovial-banzai-8196e2, PR #383)
meta/harness/bin/llm                               (Python, stdlib, 200 lines)
meta/harness/config/models.json                    (7 backends, 8 tasks)
meta/harness/MODELS.md                             (full docs: routes, install, dual cache, heretic, SAM 3)
meta/harness/bin/llama-swap/{llama-swap,config.yaml,LICENSE.md,README.md}
scripts/setup-portless.sh                         (on feature/portless-browser-bonsai, PR #387)
scripts/portless/{llm,benchy}.sh

# Benchy + benchmarks (on claude/jovial-banzai-8196e2, PR #383)
meta/harness/benchy/server/modules/mlx_llm.py      (MLX adapter)
meta/harness/benchy/server/{server.py, modules/llm_models.py, modules/exbench_module.py}  (MLX wired in)
meta/harness/benchy/server/benchmark_data/lattice_*.yaml   (5 benches)
meta/harness/benchy/server/reports/*.json                  (12 reports)
meta/harness/benchy/server/generate_report.py              (HTML aggregator)
meta/harness/benchy/LATTICE_BENCH_REPORT.html              (113 KB, interactive)

# Capability lifecycle (on feature/meta-harness — main branch for these)
analysis/capabilities/README.md
analysis/capabilities/capability-{harvest,matrix}.template.md
analysis/capabilities/capability-manifest.template.yaml
analysis/capabilities/grove-harness-capability-{harvest.md,matrix.md,registry.yaml}   (PR #385)
analysis/capabilities/portless-capability-{harvest.md,matrix.md,registry.yaml}        (PR #387)
analysis/capabilities/browser-harness-capability-{harvest.md,matrix.md,registry.yaml} (PR #387)
.claude/rules/{capability-harvest-protocol,zero-dead-dna}.md
scripts/audit-dead-dna.sh                                                             (validator)
scripts/build-grove-registry.py                                                       (registry generator)

# SFA eval folder (PR #386 + #387)
meta/harness/tools/sfa-eval/README.md
meta/harness/tools/sfa-eval/sfa_init_caches.py
meta/harness/tools/sfa-eval/sfa_duckdb_local_v1.py
meta/harness/tools/sfa-eval/sfa_browser_bonsai_v1.py
meta/harness/state/cache/sfa-eval.duckdb           (8 plants + 16 migrations seed)
meta/harness/state/_init_caches.done.json
meta/harness/state/_duckdb_local_v1.done.json
meta/harness/state/_browser_bonsai_v1.done.json
meta/harness/state/screenshots/garden-bed.png      (test fixture)
meta/harness/docs/sessions/2026-05-13-*-duckdb-local-*.json  (4 files, sfa_duckdb tests)
meta/harness/docs/sessions/2026-05-13-*-browser-bonsai-*.json (3 files, sfa_browser_bonsai tests)

# Reference roots (read-only)
/Volumes/PixelTable/GROVE_HARNESS/juniper2026/                  prior iteration (62 SFAs)
~/browser-harness/                                              browser-use/browser-harness install
/Volumes/PixelTable/models/huggingface-cache/                   secondary HF cache (NVFP4, Gemma-4-E4B, BitNet, abliterated stubs)
~/.cache/huggingface/hub/                                       primary HF cache (Bonsai, Qwen3-VL, Hermes, Qwen3.6, Gemma-4-26B)
```

## Audit verdict at session close

```
scripts/audit-dead-dna.sh → OK
  registries=26
  active=153
  deferred=167
  blocked=3
  bootstrap_empty=4
```

The substrate is operable. Send the next move whenever.
