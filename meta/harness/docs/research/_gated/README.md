---
title: "Gated Commercial Content — Dormancy Policy"
type: gating-policy
status: dormant
gate_required: ["Gate A: Accelerator", "Gate B: Partner Program", "Gate C: Developer Subscription", "Gate D: External Funding", "Gate E: Client-Funded Seat"]
gate_status: not_triggered
activation_log: []
doctrine_default: "Self-hosted open-source only — this subtree is dormant"
vendor: "multi-vendor (top-level policy)"
source: "meta/harness/PLAN/lattice-meta-harness-phase-1.5-gating-amendment (this amendment authored 2026-05-12)"
---
# Gated Commercial Content — Dormancy Policy

> The leading underscore on `_gated/` is intentional: it sorts first in directory listings and signals "special — read this README before using anything inside."

## Purpose

This subdirectory contains commercial-tier content from external vendors. **All content here is dormant by default.** The default LATTICE doctrine is: **self-hosted, open-source-only infrastructure**. Commercial-tier content here is reference material for **outreach and negotiation only**, never architectural input.

If you are reading this because you arrived here via a cross-reference from another LATTICE document: that cross-reference is intentionally routing you through this policy before you reach any commercial-tier file. Read this README before reading anything else under `_gated/`.

## The five gates

Content under `_gated/<vendor>/` is **dormant** until at least one of the following gates fires:

| Gate | Trigger condition | What activates |
|---|---|---|
| **Gate A: Accelerator Cohort Acceptance** | LATTICE is accepted into an official vendor accelerator (e.g., Bentley iTwin Activate) | Production-scale platform access for the cohort window; term-sheet conversation; vendor pipeline relationship |
| **Gate B: Partner Program Acceptance** | LATTICE is accepted into the vendor's partner program at an operational tier | Year-round partner channel access; co-marketing eligibility; developer relations contact |
| **Gate C: Developer Subscription** | LATTICE purchases a commercial developer subscription (e.g., Bentley BDN, Cesium ion paid tier) | SDK-level or paid-API access |
| **Gate D: External Funding** | LATTICE secures external funding sufficient to absorb recurring vendor spend without affecting margin | Operational affordability of commercial tier |
| **Gate E: Client-Funded Seat** | A specific client purchases their own commercial-tier seat; LATTICE operates on top of *that client's* paid access | Commercial knowledge becomes active **for that client engagement only**, never as a LATTICE recurring cost |

**Gate E is doctrinally preferred over A–D.** It preserves the "clients pay vendor, never LATTICE" stance and decouples LATTICE's recurring revenue from any external pricing changes.

## Forbidden in dormant state

Until at least one gate fires for a given vendor, the following are **forbidden**:

- Architecting LATTICE features against any pricing tier of that vendor
- Including paid / commercial APIs from that vendor in any technical plan or PRD
- `propose-decomposition` outputs referencing gated content as a substrate dependency
- Any code path that assumes commercial-credit / paid-tier availability
- Citing pricing or commercial terms in any non-outreach document

## Permitted in dormant state

Exactly one use is permitted: **drafting outreach to that vendor** — Partner Program inquiry, accelerator-cohort application, developer-network quote request, paid-tier inquiry. In that narrow context, citing correct tier names, cohort terms, and program structure is necessary to sound informed.

`meta/harness/docs/specs/outreach-templates.md` is the canonical home for active outreach drafts. It is the only LATTICE doc allowed to point directly into specific files under `_gated/<vendor>/` rather than at this README.

## Activation procedure — when a gate fires

When a gate fires for a vendor:

1. **Append an entry to `_gated/<vendor>/README.md` § Activation Log** with:
   - Date
   - Gate fired (A | B | C | D | E)
   - Trigger evidence (cohort acceptance email reference, SAFE signed, partner agreement countersigned, client purchase order, etc.)
   - Specific commercial capabilities now available
2. **Update YAML frontmatter on each activated file:**
   - `gate_status: not_triggered` → `gate_status: triggered`
   - Populate `activation_log:` with the entry summary
3. **Open a PRD-tracked issue** for any architectural changes that depend on the newly-activated capability. **Architectural changes do NOT happen automatically on activation.**

## How `propose-decomposition` and the ingestion pipeline handle this folder

Both must filter on `status: dormant` and `gate_status: not_triggered` and **exclude dormant gated content from architecture proposals and from `search_research` results returned to architectural queries**. Outreach queries (explicitly tagged as such) may include dormant content.

When Phase B + Phase 2 bring the ingestion pipeline online (`scripts/ingest-research.py`, Issue #235) and `propose-decomposition` activates, both must respect this filter. TODOs to that effect live in:

- `scripts/ingest-research.py` — TODO: filter out `meta/harness/docs/research/_gated/**/*` when `status: dormant` AND `gate_status: not_triggered` for architectural queries; include only for `query_type: outreach`.
- `.claude/skills/propose-decomposition/SKILL.md` — TODO: same filter, applied to `search_research` calls in the introspection pass.

These TODOs are flagged now so the filter is not forgotten when those implementations land.

## Vendor subdirectories

| Subdir | Vendor | Doctrine default |
|---|---|---|
| `bentley-commercial/` | Bentley Systems (iTwin Activate, Partner Program, BDN, iTwin Platform paid tiers) | iTwin OSS self-hosted only |
| `cesium-commercial/` | Cesium / Bentley (Cesium ion paid SaaS only — OSS Cesium components are NOT gated) | Self-host CesiumJS + 3D Tiles + terrain / imagery via open formats |

Add a new `_gated/<vendor>/` directory only when a real new vendor's commercial content needs gating. Do not stub vendors speculatively.

## Cross-references

- Each vendor subdir has its own `README.md` with that vendor's gate status table and contents inventory
- `meta/harness/docs/specs/outreach-templates.md` — the only doc allowed to point directly into specific files inside `_gated/`
- `.claude/rules/oss-self-hosted-doctrine.md` (or wherever the canonical doctrine rule lives) — the rule this README operationalizes
