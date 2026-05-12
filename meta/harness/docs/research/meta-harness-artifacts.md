---
title: "Meta-Harness Artifacts and Integration Notes (DesireRecord / ImprovementGoal / AGORA / InfraNodus)"
type: "research"
status: "reference"
historical_only: true
source: "MARPA_DevStack_Research_20260508/meta-harness-artifacts.md"
---
# Meta-Harness Artifacts and Integration Notes

This document drafts three core artifacts for the bridge-analysis meta-harness and then extends them into an implementation-oriented supporting system that combines AGORA, GORE-style metrics, Meta-Harness search, golden paths, Autoresearch-style ratchets, and InfraNodus as the graph-intelligence layer.[cite:151]

## DesireRecord schema

The DesireRecord captures early needs, frustrations, opportunities, and “I wish I could…” statements before they are fully normalized into formal goals.[cite:151] It is the intake artifact for the meta-harness, and it should preserve ambiguity, source context, and early signal strength rather than forcing premature precision.[cite:151]

```yaml
DesireRecord:
  id: string
  title: string
  statement: string
  source:
    type: enum[user, stakeholder, benchmark, incident, observation, strategy]
    ref: string
  context:
    project: string
    repo: string
    subsystem: string
    phase: string
  category:
    primary: enum[capability, quality, workflow, risk, integration, knowledge]
    tags: [string]
  drivers:
    urgency: integer   # 1-5
    importance: integer # 1-5
    confidence: number # 0-1
    rationale: string
    signals: [string]
  desired_outcomes: [string]
  pain_points: [string]
  constraints: [string]
  links:
    dependencies: [string]
    affected_components: [string]
    related_desires: [string]
    related_goals: [string]
  status: enum[captured, triaged, refined, accepted, rejected, superseded]
  timestamps:
    created_at: datetime
    updated_at: datetime
```

### Notes

- Use this schema when the system knows there is a need but not yet the exact implementation path.[cite:151]
- Desires should remain human-readable and natural-language friendly, because they are often mined from transcripts, logs, docs, and issue narratives before formal decomposition.[cite:151]
- InfraNodus can analyze DesireRecords as a text graph to expose recurring concepts, hidden clusters, and neglected concerns before goal modeling begins.[cite:151]

## ImprovementGoal schema

The ImprovementGoal turns a desire into a measurable target with contribution logic, evaluation rules, and implementation options.[cite:151] This is the main AGORA/GORE-aligned artifact for structured reasoning about alternatives, trade-offs, and ratcheted improvement.[cite:151]

```yaml
ImprovementGoal:
  id: string
  title: string
  goal_type: enum[functional, quality, process, learning, risk_reduction]
  description: string
  parent_goal_id: string | null
  derived_from_desires: [string]

  fit_criterion:
    metric_name: string
    target_direction: enum[increase, decrease, satisfy]
    baseline_value: number | string
    target_value: number | string
    measurement_window: string

  evaluation:
    benchmark_tasks: [string]
    test_queries: [string]
    failure_conditions: [string]

  contribution_model:
    contribution_to_parent: number   # e.g. -100 to 100
    confidence: number               # 0-1
    preference_weight: number        # 0-1
    risk_penalty: number             # 0-1

  implementation:
    candidate_strategies: [string]
    selected_strategy: string | null
    affected_repos: [string]
    affected_dependencies: [string]

  governance:
    owner: string
    review_cycle: string
    acceptance_rule: string
    rollback_rule: string

  status: enum[proposed, modeled, approved, active, validated, retired]
  timestamps:
    created_at: datetime
    updated_at: datetime
```

### Notes

- AGORA-style goal modeling benefits from explicit contribution values, preference information, and parent-child links so analysts can reason about change impact and compare alternatives.[cite:151]
- The `contribution_model` section is what lets the harness score whether a change helps an upper-level objective or creates regressions elsewhere.[cite:151]
- Golden-path refinement should produce ImprovementGoals, not free-floating tasks, when the work affects system behavior or requirements quality.[cite:151]

## gold_goals.md template

This is the compact, durable file that states what “winning” currently means for a project or subsystem.[cite:151] It should stay short, measurable, and stable enough to act as the ratchet target for evaluation loops.[cite:151]

```md
# Gold Goals

## Context
- Project:
- Repo:
- Subsystem:
- Review date:
- Owner:

## Mission
- Core objective:
- Current phase:
- Non-negotiable constraints:

## Top goals
| Goal ID | Goal | Metric | Baseline | Target | Weight |
|---------|------|--------|----------|--------|--------|
|         |      |        |          |        |        |

## Benchmark set
- Task 1:
- Task 2:
- Task 3:

## Required guardrails
- Must not regress:
- Security / safety constraints:
- Performance ceilings:
- Dependency constraints:

## Open gaps
- Gap:
- Blocking dependency:
- Unknowns:

## Candidate harness improvements
- Improvement:
- Expected contribution:
- Evaluation plan:

## Ratchet rule
Accept a change only if benchmark results improve on weighted goals and no guardrail fails.
```

This template mirrors the Autoresearch idea of explicit instructions plus keep-or-revert discipline, while adding AGORA-style weighted goals and guardrails.[cite:151]

## How to implement AGORA for meta goal modeling

AGORA should be implemented as a linked goal graph with at least three coordinated layers: product goals, workflow goals, and orchestration goals.[cite:151] Product goals cover user or system outcomes, workflow goals cover effort, traceability, and reuse, and orchestration goals cover routing, retrieval, dependency-aware context, and harness behavior.[cite:151]

Recommended implementation steps:

1. Capture raw desires as DesireRecords from docs, chats, incident logs, and benchmark notes.[cite:151]
2. Cluster and normalize them into candidate goal domains using InfraNodus or another graph-analysis pass so disconnected concerns and hidden bridges become visible.[cite:151]
3. Convert accepted domains into ImprovementGoals with parent-child structure, contribution values, confidence, and preference weights.[cite:151]
4. Link each goal to affected repos, schemas, prompts, services, dependencies, or pipelines so the dependency map becomes the grounding layer for impact analysis.[cite:151]
5. Store accepted top-level goals in `gold_goals.md`, and use that file as the stable contract for evaluation and ratcheting.[cite:151]

AGORA is most useful here because it provides a formal way to reason about alternatives, preferences, and contribution relationships instead of flattening everything into a backlog.[cite:151]

## Examples of self-improving meta harnesses

Useful software-engineering examples include a coding harness that learns which files to inspect first based on repository topology and historical bug-fix success, a PR-review harness that rewrites its own review checklist and failure triage prompts, and a test-generation harness that changes how it mines dependency edges and stack traces to propose higher-yield regression tests.[cite:151] Karpathy’s Autoresearch is a narrower example: it improves a constrained task artifact under a fixed metric and keeps only beneficial revisions through a ratchet loop.[cite:151]

The Stanford IRIS Lab Meta-Harness is broader: it searches over the harness code around a base model or agent, including retrieval logic, memory use, prompt construction, and tool wiring, rather than changing model weights.[cite:151] Related open implementations and artifacts noted in the source material include the Stanford Meta-Harness repo, the TBench2 harness artifact, and the Superagentic metaharness library inspired by the same outer-loop optimization pattern.[cite:151]

## Steps to build a gap analysis tool integrated with the dependency map

A gap analysis tool should ingest goals, desires, components, and dependencies into one stable-ID graph so each ImprovementGoal can point to repos, modules, data assets, prompts, tools, and pipelines.[cite:151] That makes it possible to ask operational questions such as which goals have no benchmark, which dependencies have no owning goal, and which critical paths lack a validation plan.[cite:151]

Suggested build sequence:

1. Ingest DesireRecords, ImprovementGoals, dependency nodes, ownership data, ADRs, benchmark specs, and incidents into one graph store.[cite:151]
2. Link each ImprovementGoal to affected components and dependency nodes.[cite:151]
3. Compute structural gaps, such as uncovered dependencies, unbenchmarked goals, and high-centrality components with no quality checks.[cite:151]
4. Rank gaps by a composite score using preference weight, dependency centrality, uncertainty, and risk penalty.[cite:151]
5. Feed the highest-ranked gaps into the proposer loop as candidate improvement opportunities.[cite:151]

InfraNodus can strengthen this tool by converting requirement text, dependency descriptions, failure corpora, and implementation docs into concept networks that reveal clusters, structural gaps, and conceptual gateways.[cite:151] That lets the system perform graph-driven delta analysis between desired-state and current-state corpora instead of relying only on manual checklists.[cite:151]

## Measuring improvement with GORE-style contribution values

A practical GORE-style score can combine contribution to parent goals, preference weight, confidence, and validation pass rate into a single weighted measure.[cite:151] One workable heuristic proposed in the source material is:

\[
weighted\_contribution = contribution\_to\_parent \times preference\_weight \times confidence \times validation\_pass\_rate
\]

This score should not replace benchmark evidence, but it is useful for ranking candidate harness changes and judging whether a local improvement supports or harms higher-level goals.[cite:151] At the portfolio level, useful metrics include goal coverage, benchmark coverage, guardrail pass rate, regression frequency, mean improvement per accepted change, and dependency-risk-adjusted contribution value.[cite:151]

Recommended additional metrics:

- Goal coverage: percentage of accepted goals with at least one benchmark and one owner.[cite:151]
- Gap closure rate: percentage of high-priority gaps that moved from open to mitigated in a review cycle.[cite:151]
- Requirement drift delta: graph difference between desires, accepted goals, and implementation docs over time using InfraNodus comparison outputs.[cite:151]
- Harness quality score: task success plus QA gates minus penalties for regressions, complexity spikes, or repeated failure motifs.[cite:151]

## Merged supporting system

The strongest merged system uses different layers for different jobs rather than collapsing everything into one tool.[cite:151] Golden paths define the preferred refinement route for recurring work, `gold_goals.md` defines what winning means now, the meta-harness adapts and improves orchestration behavior from evidence, InfraNodus acts as the structural sensing and graph-intelligence layer, and an Autoresearch-style ratchet accepts only measured improvements.[cite:151]

A clean layered model is:

1. **Desire layer** — captures what stakeholders want, including vague or conflicting pressures, as DesireRecords.[cite:151]
2. **Goal layer** — refines desires into ImprovementGoals using AGORA/GORE decomposition, alternatives, conflicts, and contribution values.[cite:151]
3. **Golden layer** — stores a compact `gold_goals.md` file that defines accepted success criteria, benchmarks, and guardrails.[cite:151]
4. **Graph-intelligence layer** — InfraNodus turns messy text from logs, traces, docs, requirements, and dependency descriptions into graphs that expose clusters, content gaps, gateway concepts, and discourse drift.[cite:151]
5. **Meta-harness layer** — the proposer changes retrieval behavior, planning, decomposition, tool flow, and benchmark use based on files, traces, graph artifacts, and scores.[cite:151]
6. **Ratchet QA layer** — candidate changes are kept only if weighted outcomes improve and no guardrail fails, following the Autoresearch discipline of measurable keep-or-revert loops.[cite:151]

In this model, Meta-Harness and golden paths are complementary, not competing.[cite:151] Golden paths encode the canonical workflow skeleton, while the meta-harness decides when to follow that skeleton strictly, when to branch, and how to improve it over time using evidence.[cite:151]

## InfraNodus as graph-intelligence layer

InfraNodus should not be treated as a side visualization tool; it should be used as a reusable analysis service inside the meta-improvement layer.[cite:151] Its role is to turn raw text into a concept network that exposes clusters, structural gaps, conceptual gateways, and diversity signals that can improve retrieval, prompt design, benchmark design, governance drift detection, and proposer briefs.[cite:151]

High-value insertion points include:

- Desire capture: graph stakeholder notes, roadmap fragments, issues, and transcripts to detect blind spots early.[cite:151]
- Goal modeling: compare raw desires to accepted goals and find underrepresented concerns.[cite:151]
- Retrieval / GraphRAG: use `contentGaps` and `conceptualGateways` as retrieval hints, not as facts, to widen or rebalance context selection.[cite:151]
- Failure clustering: graph traces and evaluator comments to find repeated failure brokers and choke points.[cite:151]
- Dependency-map analysis: graph interfaces, ADRs, and module docs to identify weakly connected or semantically isolated subsystems.[cite:151]
- Continuous QA: compare graphs over time to detect narrowing, drift, or harmful overfocus in the optimization loop.[cite:151]

A practical operating policy is to use `optimize=gaps` on goals, failures, and retrieval corpora when reducing blind spots, `optimize=develop` for balanced expansion, `optimize=reinforce` only for deliberately narrow tasks, and `optimize=latent` when the harness appears stuck in a narrow local optimum.[cite:151] Graph advice should inform retrieval and proposer context, but it should not override benchmark-driven acceptance decisions.[cite:151]

## Recommended repo additions

To make this system easier to operationalize, the following files should be added to the project:

- `schemas/desire-record.schema.yaml` — normalized DesireRecord schema.[cite:151]
- `schemas/improvement-goal.schema.yaml` — normalized ImprovementGoal schema.[cite:151]
- `gold_goals.md` — the active ratchet target for goals, benchmarks, and guardrails.[cite:151]
- `analysis/infranodus/` — graph artifacts such as `desires.graph.json`, `goals.graph.json`, `failures.graph.json`, and `goal-vs-implementation.diff.json`.[cite:151]
- `analysis/gaps/` — ranked gap reports linked to dependency nodes and goals.[cite:151]
- `meta-harness/` — proposer briefs, candidate harness variants, evaluation summaries, and acceptance results.[cite:151]

## Operating principle

The most useful guiding principle for the supporting system is this: stable workflow structure, adaptive orchestration, graph-informed sensing, and ratcheted acceptance should all coexist.[cite:151] That keeps the system reusable enough to become a platform, but evidence-driven enough to keep improving without guessing.[cite:151]
