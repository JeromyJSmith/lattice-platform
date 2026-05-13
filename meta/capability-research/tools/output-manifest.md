# Graph Tool Output Manifest

Date: 2026-05-13
Status: draft

This manifest defines where graph and gap-analysis tools are allowed to write
outputs for LATTICE capability research.

## Allowed Output Roots

| Tool | Output root | Purpose |
|---|---|---|
| InfraNodus | `meta/capability-research/tools/` | Human-readable gap reports and planning notes |
| InfraNodus | `meta/capability-research/inventory/` | JSON or structured gap-analysis output |
| Graphify | `meta/capability-research/inventory/graphify/` | Docs-first graph output after scoped proof |
| GitNexus | `meta/capability-research/inventory/gitnexus/` | Exported summaries or current-state notes after scoped proof |
| Harness proof | `meta/harness/docs/sessions/` | Verifier-backed session evidence |

## Disallowed Output Roots

| Path | Reason |
|---|---|
| Repo root `graphify-out/` | Easy to accidentally commit generated graph output or self-index |
| `meta/harness/` root | Harness docs should stay proof/execution focused |
| `analysis/capabilities/` | Registry YAML only; generated reports do not belong here |
| `pixeltable/` | Runtime code/schema only; no exploratory graph output |
| `src/` | UI/runtime only; no exploratory graph output |
| `3d_assets/`, `assets/`, `public/` | Asset/runtime payload areas, not research output |

## Naming

Use date-stamped files:

```text
meta/capability-research/tools/infranodus-gap-analysis-YYYY-MM-DD.md
meta/capability-research/inventory/infranodus-gap-analysis-YYYY-MM-DD.json
meta/capability-research/inventory/graphify/YYYY-MM-DD-docs-first/
meta/capability-research/inventory/gitnexus/YYYY-MM-DD-harness-subset/
meta/harness/docs/sessions/YYYY-MM-DD-<tool>-proof.md
```

## Evidence Rule

Generated tool output is not proof by itself. For a capability row to become
proven, a harness evidence artifact must cite:

1. The command or MCP call used.
2. The input corpus or manifest.
3. The output path.
4. The verifier result.
5. The promotion decision.

Until that exists, tool outputs are research material only.

## First Allowed Runs

| Order | Tool | Scope | Output |
|---:|---|---|---|
| 1 | InfraNodus | Curated docs in `corpus-manifest.yaml` | `tools/infranodus-gap-analysis-YYYY-MM-DD.md` |
| 2 | Graphify | Curated docs only | `inventory/graphify/YYYY-MM-DD-docs-first/` |
| 3 | GitNexus | `first_code_subset` only | `inventory/gitnexus/YYYY-MM-DD-harness-subset/` |

Repo-wide Graphify or GitNexus runs are explicitly out of scope until those
three runs have evidence-backed results.
