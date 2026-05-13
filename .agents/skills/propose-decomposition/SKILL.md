---
name: propose-decomposition
description: "Introspective function. The organism inspects its own codebase via search_tutorials, search_research, search_docs, search_api_reference, get_coverage_gaps, Graphify dependency graphs, and InfraNodus topic analysis, then proposes a polymorphic decomposition plan. NEVER executes cell-divide. Human gate is mandatory. Depth-guarded: max 3 new levels of nesting per cycle. INERT until Phase B."
disable-model-invocation: true
user-invocable: true
source: "lattice-internal (Phase 1 Amendment §2.2)"
vendored_at: null
vendor_strategy: lattice-authored
local_adaptations: []
lineage: []
---
# propose-decomposition — Organism Self-Inspection

> **HARD CONSTRAINT — Phase 1:** This skill is *inert*. Its sensory tools (`search_tutorials`, `search_research`, `search_docs`, `search_api_reference`, `get_coverage_gaps`, Graphify, InfraNodus) come online during Phase B per Amendments 06/07/08 and Phase 0.6/0.7/0.8 substrate landing. Do NOT invoke this skill in Phase 1.

## Purpose

Let the organism examine its own structure and propose where the skill genome should divide next. Output is a *proposal*, never an execution. The human reads the proposal and decides whether to run `cell-divide` for the suggested target(s).

## Inputs

| Argument | Required | Meaning |
|---|---|---|
| `focus_section` | optional | If set, restrict introspection to one section (`schema`, `api`, `frontend`, `georef-reality`, `genai`, `vw-itwin`, `ddc`, `ci`, `docs`). If omitted, scans the entire organism. |
| `max_depth_delta` | optional | Max new levels of nesting this proposal may suggest. Hard cap is 3 per the depth guard. |

## Behavior (Phase B+)

1. **Substrate query pass** (anti-amnesia pre-flight):
   - `search_tutorials("decomposition patterns", tool_name=focus_section)`
   - `search_research("polymorphic harness decomposition")`
   - `search_docs("section ownership rules", tool_name="lattice")`
   - `get_coverage_gaps(tool_name=focus_section, severity="high")`
2. **Structural pass** (Graphify):
   - Run `graphify analyze --root . --format json`.
   - Identify hotspots (high coupling), hubs, bridges, cycles per `.Codex/skills/improve-codebase-architecture/SKILL.md`.
3. **Semantic pass** (InfraNodus):
   - Read the latest snapshot of `analysis/infranodus/desires.graph.json` + `analysis/infranodus/goals.graph.json` (from the substrate).
   - Identify gap and gateway topics that suggest where the harness needs more dedicated cells.
4. **Synthesis** — produce a markdown proposal containing:
   - One paragraph framing of the organism's current health (composite score from all section harnesses).
   - Per candidate division: target path, parent commit SHA, expected lineage depth after division, rationale (which signals from passes 1–3 motivate this), risk callouts, and the exact `cell-divide` command the human would invoke to execute it.
   - Depth guard check: refuse to emit proposals that would introduce more than `max_depth_delta` (default 3) new nesting levels in a single cycle. If more nesting is warranted, recommend the human run a follow-up cycle after the previous level is verified healthy.
   - Explicit "NEXT ACTIONS" list with the exact human-review checkpoint.
5. **Emit** to `meta/harness/PLAN/proposals/<UTC-timestamp>-decomposition.md`. Do not commit; the human commits after review.

## What this skill does NOT do

- It does NOT execute `cell-divide`. It only describes what `cell-divide` *would* do.
- It does NOT mutate the genome, the substrate, the knowledge tables, or the docs.
- It does NOT propose deletions. Only divisions and promotions.
- It does NOT exceed the depth guard (3 new levels per cycle).

## Hard constraint reminder

Per Phase 1 Amendment §2.2 + §5:
- **Do not run this skill in Phase 1.**
- The sensory layer (the six `@pxt.query` tools + Graphify + InfraNodus) is itself in plan-state until Phase B applies migrations 0014–0016 and the bootstrap pipelines run on the M3 Max. Invoking this skill before Phase B completes will return zero results from every sensory call and produce a vacuous proposal.
