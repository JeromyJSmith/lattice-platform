<!-- spec-verified: code.claude.com/docs 2026-05-11 -->
# Zero Dead DNA Rule

**Standard #2 of 3 introduced by Phase 0.6** (see `meta/harness/PLAN/06-CAPABILITY-HARVEST-AMENDMENT.md`).

## The rule

Every capability listed in any `analysis/capabilities/*-capability-registry.yaml` must, at all times, be in exactly one of three states: `ACTIVE`, `DEFERRED`, `BLOCKED`. No silent rows. No "we'll figure it out later" without a `target_phase` and `tracking_issue`.

The full lifecycle is harvest → matrix → manifest → registry → verification. Zero Dead DNA applies at the registry layer, and each registered row should remain traceable back to the harvest/matrix/manifest trail that justified it.

A capability stuck in `DEFERRED` past its `target_phase` is **dead DNA** and fails CI.

## Why

Tool ecosystems ship more capability than a first integration pass typically uses. The unused capability does not stay dormant — it accumulates as:

- Permissions you've granted but aren't auditing
- Surface area for prompt injection / misuse
- Future-you's confusion ("did we ever wire `infranodus.generate_seo_report`?")
- Drift between what the tool actually does and what the harness believes it does

Zero Dead DNA forces you to either USE a capability, EXPLAIN why you're not yet using it (with a deadline), or DOCUMENT what's blocking you.

## Enforcement

| Mechanism | Where | When |
|---|---|---|
| Registry must exist | `analysis/capabilities/<tool>-capability-registry.yaml` | Same commit as tool install |
| Required-fields check | `scripts/audit-dead-dna.sh` | Local pre-commit + CI |
| Past-target-phase check | same | CI fails if `DEFERRED` row's `target_phase` is in the past relative to current PR head's phase tag |
| BLOCKED requires resolution path | same | `blocker_resolution_path` must be a non-empty string |

## Allowed reasons for DEFERRED

Curated list — adding new reasons requires PR review:

- `out-of-scope-for-current-phase` — capability is real but doesn't serve the current section's goals
- `awaiting-upstream-dep` — needs another tool installed first (must reference that tool's row)
- `awaiting-api-key` — runtime credential not yet provisioned (must reference the .env key name)
- `experimental-upstream` — capability marked experimental by tool author; we'll wait for stability
- `cost-prohibitive` — running this capability costs more than the value at current scale
- `redundant-with-other-tool` — duplicated by another ACTIVE capability (must reference that row)

Anything outside this list goes through PR review as a new reason category.

## What dead DNA looks like in practice

```yaml
# BAD — fails Zero Dead DNA
- id: generate_seo_report
  surface: mcp_tool
  name: generate_seo_report
  state: DEFERRED
  description: SEO content gap report

# GOOD
- id: generate_seo_report
  surface: mcp_tool
  name: generate_seo_report
  state: DEFERRED
  description: SEO content gap report
  reason: out-of-scope-for-current-phase
  target_phase: post-Phase-8
  tracking_issue: 99   # opens with this amendment if a future phase needs it
```

## Relationship to Capability Harvest Protocol

Capability Harvest Protocol mandates the **harvest, matrix, manifest, and registry exist for integrated tools**. Zero Dead DNA mandates the **registry's contents stay honest over time**. Without the harvest you have no registry to audit; without zero-dead-DNA the registry rots into shelfware.
