<!-- spec-verified: code.claude.com/docs 2026-05-11 -->
# Capability Lifecycle

Capability Harvest is mandatory setup for any tool or harness surface that LATTICE depends on. The goal is to use the full tool surface deliberately instead of wiring a small subset and forgetting the rest.

## Pipeline

| Stage | Artifact | Purpose | Gate |
|---|---|---|---|
| Harvest | `analysis/capabilities/<tool>-capability-harvest.md` | Raw inventory of all tool surfaces | No omitted surfaces; all metrics start at zero |
| Matrix | `analysis/capabilities/<tool>-capability-matrix.md` | Decide candidate use/defer/block/reject per harness | Every useful row has a proposed harness, invocation, and verification target |
| Proof Run | CI, score scripts, reports, filesystem evidence | Run the capability once and prove it produced the desired outcome | Evidence artifact exists and verification passes |
| Manifest | `analysis/capabilities/<tool>-capability-manifest.yaml` | Machine-readable harness intent for proven rows | Capability has at least one successful proof run |
| Registry | `analysis/capabilities/<tool>-capability-registry.yaml` | Canonical state: ACTIVE, DEFERRED, BLOCKED | `scripts/audit-dead-dna.sh` passes and ACTIVE rows cite proof evidence |
| Tracking | Pixeltable evidence, score history, trend reports | Track quality, cost, latency, and regressions over time | Global Meta-Harness consumes the signal |

## Zero-to-Registered Rule

A harvested capability is not active just because it appears in a table. New rows
start at zero: no score, no trust, no dispatch weight, and no registry authority.
The first successful run is the gateway into the manifest and registry.

Promotion requires:

- a runnable invocation
- an expected output or outcome
- a verifier or scoring command
- an evidence artifact
- one passing proof run

After promotion, the Meta-Harness starts tracking capability metrics such as pass
rate, runtime, cost, model/provider used, input shape, output shape, and failure
patterns. Before promotion, the row is only possibility space.

## Contract-Only Rows

An active-looking capability row without proof is contract-only. It can describe
intent, ownership, expected invocation, expected output, and verification shape,
but it is not trusted and must not receive dispatch weight.

Use these meanings during pre-flight:

| State | Meaning | Operator action |
|---|---|---|
| Contract-only | Row has enough detail to run later, but no passing proof artifact | Treat as untrusted; schedule or run pre-flight |
| Proven | Row cites passing proof evidence and deterministic verifier output | Eligible for manifest/registry promotion and tracking |
| Deferred | Row is useful, but blocked, incomplete, or intentionally later | Keep visible with blocker and next action |
| Failed | Row was exercised and the verifier or evidence contract failed | Do not promote; fix contract, execution, or verifier first |

`ACTIVE` must mean proven. If a registry currently contains an `ACTIVE` row with
no proof evidence, the pre-flight interpretation is contract-only until the row
cites proof.

## Pre-Flight Loop

The MetaHarness pre-flight loop converts a row into an evidence-backed result:

```text
capability row
  -> run contract
  -> browser execution
  -> sidecar/verifier
  -> evidence artifact
  -> row result
  -> promotion/tracking
```

The run contract names the goal, inputs, allowed paths, denied paths, timeout,
working directory, expected output, verifier, evidence destination, and promotion
rule. The browser surface makes the row and result visible to the operator. The
FastAPI sidecar and verifier make the pass/defer/fail decision. The evidence
artifact is the proof record until Pixeltable evidence tables are live.

Promotion happens only after the row result cites proof. Tracking begins after
promotion and records pass rate, runtime, cost when known, model/provider, input
shape, output shape, and failure mode.

## Harness rule

Each section harness writes its own docs and diagrams. Those docs must include a capability harvest table or link to the tool-level harvest, plus the harness-specific matrix rows it relies on. The Global Meta-Harness does not own the individual harvests; it verifies that the harvests, matrices, manifests, registries, and evidence agree.

## Docs-harness role

The Documentation Meta-Harness cross-checks ACTIVE capability rows against the docs mirror substrate. Once docs ingestion is live, an ACTIVE capability with no matching doc coverage becomes a docs gap and is reported through `analysis/gaps/docs-gap-report.md` and `lattice/harness/section_events`.

Until that substrate is live, the hard gate is `scripts/audit-dead-dna.sh`: every registry must parse, every row must have the required state fields, and bootstrap-empty registries must be marked `spec-verified: false`.
