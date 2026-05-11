<!-- spec-verified: code.claude.com/docs 2026-05-11 -->
# Phase 0.6 — Capability Harvest Amendment

**Status:** binding. Phase 1 BLOCKED until Amendment 06 + 07 + 08 are all committed.

## Why this exists

Tool ecosystems ship more capability than we initially wire up. Of InfraNodus's 22+ MCP tools, the first integration pass typically uses 4-5. The other 17 are *dead DNA* — installed but un-invoked, un-documented, un-scored. Same problem at scale across Graphify (parisgroup + safishamsi), GitNexus, and any future tool. The harness becomes a thin wrapper around a fraction of what's actually available.

**Capability Harvest** is the explicit prophylactic: before any tool is "integrated," every capability surface (MCP tools, CLI commands, skills, agents, hooks, prompts) is **inventoried, reasoned about, and bound to either ACTIVE or DEFERRED with a reason**. No capability is silently ignored.

## Three permanent standards introduced by this amendment

1. **Capability Harvest Protocol** — see `.claude/rules/capability-harvest-protocol.md`. Every tool integration must produce a capability registry under `analysis/capabilities/` before the tool's first end-to-end use.
2. **Zero Dead DNA Rule** — see `.claude/rules/zero-dead-dna.md`. Every capability in a registry must be ACTIVE (wired), DEFERRED (reason recorded, target phase), or BLOCKED (external blocker recorded). No silent unused capability.
3. **Always-Running CI/CD Health Loop** — `scripts/audit-dead-dna.sh` runs on every commit (Phase 7 will wire it into docs-sync-check.yml Job 12); fails CI if any capability sits in DEFERRED past its target phase without justification.

## Dependency allowlist (user-approved)

Per user directive *"All Dependencies can be added to an allowlist: {dependency}"*:

| Dependency | Install path | Justification | Phase added |
|---|---|---|---|
| `graphify` (parisgroup-ai, Rust) | `curl install.sh → /tmp → review → exec` | Structural AST + dependency graph, MCP integration | 1 |
| `gitnexus` (npm) | `npm install gitnexus` (LOCAL devDependency — NOT `-g`) | Execution graph + pre/post tool hooks; user-preferred local scope | 1 |
| `infranodus-mcp-server` | `npx -y` via `.mcp.json` (no global install) | Semantic gap analysis; API-key gated via `.env` | 1 |
| `graphifyy` (safishamsi, PyPI — double-y) | `uv tool install graphifyy` | Multi-format + YouTube URL ingestion; complements Rust graphify | 0.7 (substrate) |
| `infranodus/skills` (zip) | unzip to `~/.claude/skills/` | InfraNodus's bundled Claude skills | 1 |

See `.claude/rules/dependency-allowlist.md` for the machine-readable form.

## File inventory added by this amendment

### Plan / docs

- `meta/harness/PLAN/06-CAPABILITY-HARVEST-AMENDMENT.md` — this file
- Updates to `00-OVERVIEW.md` (add Phase 0.6 row), `02-PLAN.md` (Phase 1 + Phase 6 exit conditions), `04-EXECUTION-HANDOFF.md` (Issues #17-19), `.claude/rules/infranodus-corpus.md` (full MCP tool catalog + preferred tool map)

### Rules (Phase 6 → land now as ambient project rules; replicated/referenced from .claude/rules/ in Phase 6 of the main plan)

- `.claude/rules/capability-harvest-protocol.md`
- `.claude/rules/zero-dead-dna.md`
- `.claude/rules/dependency-allowlist.md`

### Capability registries

- `analysis/capabilities/README.md`
- `analysis/capabilities/infranodus-capability-registry.yaml` — 20 MCP tools + 14 skills, every DEFERRED has a reason
- `analysis/capabilities/graphify-parisgroup-capability-registry.yaml` — 18 CLI + 9 MCP + 5 slash + 3 skills + 2 agents
- `analysis/capabilities/gitnexus-capability-registry.yaml` — 16 MCP + 5 group tools + 2 prompts + 4 skills + hooks
- `analysis/capabilities/graphify-safishamsi-capability-registry.yaml` — Python multi-format + YouTube ingestion

### Scripts

- `scripts/audit-dead-dna.sh` — stub, exits 0, references Issue #17

## Pixeltable docs note (cross-link to Amendment 07)

The capability registries reference Pixeltable as a knowledge substrate (see Amendment 07). Capability rows that DEFER to "later phase" must point to the substrate row that will operationalize them.

**Amendment 07 (Knowledge Substrate) extends this:** the `analysis/capabilities/*-capability-registry.yaml` files for each tool will have a companion entry in `lattice/knowledge/skills_registry` (when Issue #22 runs the first harvest). Once both layers are populated, anti-amnesia pre-flight on a tool resolves to: registry tells you *what exists*, substrate tells you *how to use it correctly*.

## Issues created in Phase 8

- **#17** — Implement `scripts/audit-dead-dna.sh` full check (parse all registries, scan codebase for ACTIVE-tool invocations, fail on DEFERRED-past-target)
- **#18** — Wire `audit-dead-dna.sh` into `docs-sync-check.yml` as Job 12
- **#19** — Capability harvest pass on Graphify (parisgroup) — first real ACTIVE/DEFERRED assignments after tool install

## Exit conditions (Phase 1 amended)

Phase 1 (KG Triad install) is not complete until:

1. Original Phase 1 exits met (graphify run produces analysis.json; .mcp.json contains infranodus; gitnexus indexes repo)
2. **NEW:** Every tool in dependency allowlist has its capability registry populated to ACTIVE/DEFERRED/BLOCKED (no UNKNOWN rows)
3. **NEW:** `bash scripts/audit-dead-dna.sh` exits 0 (against the registries committed in this amendment — the script's stub form is sufficient here)

## Exit conditions (Phase 6 amended)

Phase 6 (.claude/ system files) is not complete until:

1. Original Phase 6 exits met
2. **NEW:** `.claude/rules/capability-harvest-protocol.md`, `zero-dead-dna.md`, `dependency-allowlist.md` all exist and are referenced from `.claude/rules/infranodus-corpus.md`
