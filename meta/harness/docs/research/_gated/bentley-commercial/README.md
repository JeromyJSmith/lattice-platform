---
title: "Bentley Commercial — Gate State + Activation Log"
type: gating-policy
status: dormant
gate_required: ["Gate A: Accelerator", "Gate B: Partner Program", "Gate C: Developer Subscription", "Gate D: External Funding", "Gate E: Client-Funded Seat"]
gate_status: not_triggered
activation_log: []
doctrine_default: "iTwin OSS self-hosted only — Bentley commercial content here is dormant"
vendor: "Bentley Systems"
source: "Phase 1.5 amendment (this folder created 2026-05-12)"
---
# Bentley Commercial — Gate State

> **Read `_gated/README.md` first.** This folder is dormant by default per the five-gate policy.

## Vendor

**Bentley Systems** — covers all commercial-tier Bentley content: iTwin Activate accelerator, iTwin Partner Program (commercial-terms layer), Bentley Developer Network (BDN), iTwin Platform paid tiers, OpenSite+ early access, MicroStation / OpenRoads / other non-iTwin paid SDK products.

## Doctrine default

**iTwin OSS self-hosted only.** Per cardinal rule in `AGENTS.md` § cardinal rules. Translated:

- `@itwin/core-geometry`, `@itwin/core-common`, `@itwin/core-quantity`, `@itwin/core-frontend` — MIT-licensed, used freely. **Not gated.**
- BIS schema vocabulary — open, used freely. **Not gated.**
- iTwin.js library, public iTwin REST APIs viewed as protocol surface — used freely. **Not gated.**
- iTwin Synchronization API IFC connectors as a protocol concept — used freely. **Not gated.**
- iTwin Platform paid tiers (Community/Standard/Premium/Enterprise commercial billing) — **gated** (this folder).
- iTwin Activate accelerator (SAFE, cohort terms, funding pipeline) — **gated** (this folder).
- iTwin Partner Program commercial-terms layer — **gated** (this folder). The Partner Program *application path* is mentioned in `meta/harness/docs/specs/outreach-templates.md` as outreach; the commercial implications of accepted-partner status live here.
- Bentley Developer Network (BDN) — **gated** (this folder). Not required for iTwin REST API development; relevant only for non-iTwin Bentley SDK products, which the cardinal rule forbids.

## Gate status table

| Gate | Status | Last evaluated | Notes |
|---|---|---|---|
| Gate A: Accelerator Cohort Acceptance | `not_triggered` | 2026-05-12 | 2026 iTwin Activate cohort theme + window not yet announced. Application requires LATTICE / MARPA principal authorization first. |
| Gate B: Partner Program Acceptance | `not_triggered` | 2026-05-12 | Application form is open year-round; we have not yet submitted. |
| Gate C: Developer Subscription | `not_triggered` | 2026-05-12 | BDN annual fees not publicly disclosed; no LATTICE need until non-iTwin product scope opens (forbidden by cardinal rule). |
| Gate D: External Funding | `not_triggered` | 2026-05-12 | LATTICE has no external funding round. |
| Gate E: Client-Funded Seat | `not_triggered` | 2026-05-12 | No client engagement currently operates on client-funded Bentley commercial access. |

## Activation log

```yaml
# Each activation entry uses this YAML shape:
# - date: "YYYY-MM-DD"
#   gate: "Gate A" | "Gate B" | "Gate C" | "Gate D" | "Gate E"
#   trigger_evidence: "<email ref, signed SAFE, partner-agreement countersigned, client PO, etc.>"
#   capabilities_now_active: ["<specific capability 1>", "<specific capability 2>"]
#   activated_files: ["<path/to/activated/file-1.md>", ...]
#   prd_issue: "<GH issue # opened for architectural review>"

# No activations yet.
activation_log: []
```

## Contents inventory

| File | What it contains | Provenance |
|---|---|---|
| `itwin-pricing.md` | Verified iTwin Platform pricing tier table (Community / Standard $199 / Premium $499 / Enterprise), credit cost structure, worked example | Moved from `meta/harness/docs/research/itwin-pricing.md` in Phase 1.5 §5.1 |
| `activate-program.md` | iTwin Activate accelerator details (SAFE $250K, iTwin Ventures $100M fund, $250K–$5M check range, cohort history, James Kress / Clive Hackforth references) | Extracted from `bentley-ecosystem-deep-dive-20260508.md` § Pillar 3 in Phase 1.5 §5.2 |
| `partner-program.md` | Partner Program tier specifics (Standard / Premier), three engagement phases (Envision / Design / Sprint), co-marketing terms, application process | Extracted from `bentley-ecosystem-deep-dive-20260508.md` § Pillar 1 in Phase 1.5 §5.2 |
| `bdn-developer-access.md` | Bentley Developer Network — Commercial Subscription and SELECT Subscription tiers, scope (non-iTwin SDK products like MicroStation / OpenRoads), pricing unknowns | Extracted from `bentley-ecosystem-deep-dive-20260508.md` § Pillar 2 in Phase 1.5 §5.2 |

## Cross-references

- `_gated/README.md` — top-level five-gate policy + activation procedure
- `meta/harness/docs/research/bentley-ecosystem-deep-dive-20260508.md` — OSS-layer Bentley facts retained outside `_gated/` after extraction; contains stub paragraphs pointing back here
- `meta/harness/docs/specs/outreach-templates.md` — active outreach drafts; the only LATTICE doc permitted to point directly at files in this folder
- `meta/harness/docs/research/marpa-business-intelligence.md` — strategic frame that references this folder via `_gated/README.md` (the gating policy), never directly
- `.claude/rules/oss-self-hosted-doctrine.md` (or canonical OSS-self-hosted rule) — the binding rule this gate operationalizes
- `AGENTS.md` § cardinal rules — `iTwin OSS self-hosted only` is the originating doctrine

## Open work (to be issue-tracked during Phase B / Phase 2 sequencing)

- File a GH issue once Phase B sequencing begins: "Ingestion pipeline + propose-decomposition must filter `_gated/<vendor>/**` when `status: dormant` AND `gate_status: not_triggered` for architectural queries." (Currently a TODO inside `_gated/README.md`; promote to a tracked issue when Phase B starts.)
