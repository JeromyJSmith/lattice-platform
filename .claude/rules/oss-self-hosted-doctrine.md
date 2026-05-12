<!-- spec-verified: code.claude.com/docs 2026-05-11 -->
# OSS Self-Hosted Doctrine

**Standard introduced by Phase 1.5 §8** — see `meta/harness/PLAN/lattice-meta-harness-phase-1.5-gating-amendment` and `meta/harness/docs/research/_gated/README.md`. This rule operationalizes the cardinal rule `iTwin OSS self-hosted only` from `AGENTS.md` § cardinal rules and generalizes it to every commercial vendor.

## The rule

**LATTICE infrastructure is self-hosted open-source only.** Commercial-tier vendor content — pricing tiers, accelerator programs, partner programs, developer subscriptions, paid SaaS APIs, hosted asset endpoints — is **gated** under `meta/harness/docs/research/_gated/<vendor>/` and **dormant by default**. Architecting LATTICE against gated content is **forbidden** until a documented gate fires (see `_gated/README.md` for the five gates and activation procedure).

## Scope

This rule applies to every commercial vendor, present and future. As of Phase 1.5:

| Vendor | Gated content | OSS components (stay in regular architecture) |
|---|---|---|
| Bentley iTwin | iTwin Platform paid tiers, iTwin Activate (SAFE / cohorts), iTwin Partner Program commercial-terms layer, Bentley Developer Network (BDN) | `@itwin/core-geometry`, `@itwin/core-common`, `@itwin/core-quantity`, `@itwin/core-frontend` (all MIT); BIS schemas; iTwin.js library; public iTwin REST APIs as a protocol surface |
| Cesium (Bentley subsidiary) | Cesium ion paid SaaS; ion hosted asset serving; ion premium curated datasets; any feature requiring an ion API key against Cesium's hosted cloud | CesiumJS library; Cesium 3D Tiles OGC standard; **self-hosted** terrain serving, imagery serving, 3D Tiles serving; `@deck.gl/cesium` |

Adding a new vendor's commercial content triggers the same gating discipline: create `_gated/<vendor>/` with a vendor-specific README + the five-gate status table.

## Self-hosting expansion is mandatory

When the OSS alternative to a commercial SaaS path requires additional setup work (e.g., self-hosted terrain serving instead of Cesium ion), **the setup work is mandatory per doctrine**. The cost is paid in upfront engineering, not recurring SaaS spend. The trade matches the OSS-self-hosted doctrine exactly.

## Forbidden in dormant state

Until at least one gate fires for a given vendor:

- Architecting LATTICE features against any pricing tier of that vendor
- Including paid / commercial APIs from that vendor in any technical plan or PRD
- `propose-decomposition` outputs referencing gated content as a substrate dependency
- Any code path that assumes commercial-credit / paid-tier availability or a hosted-SaaS API key
- Citing pricing or commercial terms in any non-outreach document

## The single permitted use of gated content

**Drafting outreach to that vendor** (Partner Program inquiry, accelerator-cohort application, developer-network quote request, paid-tier inquiry). `meta/harness/docs/specs/outreach-templates.md` is the canonical and only doc allowed to point directly at specific files under `_gated/<vendor>/`. All other LATTICE docs cross-reference `_gated/README.md` (the policy), not specific gated files.

## The five gates

Defined fully in `meta/harness/docs/research/_gated/README.md`:

- **Gate A** — Accelerator Cohort Acceptance
- **Gate B** — Partner Program Acceptance
- **Gate C** — Developer Subscription
- **Gate D** — External Funding
- **Gate E** — Client-Funded Seat (doctrinally preferred over A–D)

When a gate fires, follow the activation procedure in `_gated/README.md` § "Activation procedure — when a gate fires". **Architectural changes do NOT happen automatically on activation** — each activation gets a PRD-tracked issue.

## Enforcement

| Mechanism | Where | When |
|---|---|---|
| Rule file present | `.claude/rules/oss-self-hosted-doctrine.md` | Always loads at session start |
| Cardinal rule | `AGENTS.md` § cardinal rules (the originating doctrine — never modify without team consensus) | Always loads |
| Vendor README + gate-status table | `_gated/<vendor>/README.md` | Inspect every time the agent touches gated content |
| `propose-decomposition` filter | `.claude/skills/propose-decomposition/SKILL.md` (Phase B) — must filter `_gated/<vendor>/**` when `status: dormant` AND `gate_status: not_triggered` for architectural queries | Phase B onward |
| Ingestion pipeline filter | `scripts/ingest-research.py` (Issue #235) — same filter | Phase 2 onward |

## Cross-references

- `AGENTS.md` § cardinal rules — originating doctrine (`iTwin OSS self-hosted only`, `Pixeltable is the only database`, etc.)
- `meta/harness/docs/research/_gated/README.md` — top-level five-gate policy
- `meta/harness/docs/research/_gated/<vendor>/README.md` — vendor-specific gate state + activation log
- `.claude/rules/capability-harvest-protocol.md` — sibling rule (every tool capability is enumerated)
- `.claude/rules/zero-dead-dna.md` — sibling rule (every capability has a state)
- `.claude/rules/dependency-allowlist.md` — every dependency is allowlisted; OSS-only stance is the binding default
