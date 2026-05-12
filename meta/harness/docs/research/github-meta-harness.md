---
title: "GitHub Meta-Harness Research — Stanford IRIS Lab + InfraNodus deep-dive"
type: "research"
status: "reference"
historical_only: true
source: "MARPA_DevStack_Research_20260508/github meta-harness (1).md"
---
<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# github meta-harness

The main GitHub repo you’re looking for is the Stanford IRIS Lab implementation at `stanford-iris-lab/meta-harness` on GitHub.[^1_1]

## Primary Meta-Harness repo

- Repo: [stanford-iris-lab/meta-harness](https://github.com/stanford-iris-lab/meta-harness)[^1_1]
- What it is: A framework for automated search over task‑specific model harnesses – i.e., the code around a fixed base model that decides what to store, retrieve, and how to call tools.[^1_2][^1_1]
- Purpose: Lets a coding agent iteratively propose, evaluate, and refine harness code (prompting, memory, tool wiring) using filesystem access to prior code, scores, and traces.[^1_2]

For Terminal-Bench 2 specifically, they also release the discovered harness as a separate artifact:

- Repo: [stanford-iris-lab/meta-harness-tbench2-artifact](https://github.com/stanford-iris-lab/meta-harness-tbench2-artifact)[^1_3][^1_2]
- Role: Concrete agent scaffold that implements the optimized harness Meta‑Harness found for Terminal‑Bench 2.0, built on top of Terminus‑KIRA / Terminus‑2.[^1_3][^1_2]


## Related/open reimplementations

If you’re exploring implementations or adaptations:


| Project | Link | Notes |
| :-- | :-- | :-- |
| Stanford Meta-Harness | [stanford-iris-lab/meta-harness](https://github.com/stanford-iris-lab/meta-harness) | Official framework for harness search.[^1_1][^1_2] |
| TBench2 harness artifact | [stanford-iris-lab/meta-harness-tbench2-artifact](https://github.com/stanford-iris-lab/meta-harness-tbench2-artifact) | Ready-made harness for Terminal‑Bench 2.[^1_3][^1_2] |
| Superagentic metaharness | [SuperagenticAI/metaharness](https://github.com/SuperagenticAI/metaharness) | Open-source Python library inspired by Meta‑Harness for optimizing harnesses around agentic coding systems.[^1_4] |

If you tell me your intended use (e.g., tuning your LATTICE OS agents, building a harness search loop around Claude Code, etc.), I can sketch how to plug this repo into your stack and which parts of their design matter most for you.
<span style="display:none">[^1_5][^1_6][^1_7][^1_8]</span>

<div align="center">⁂</div>

[^1_1]: https://github.com/stanford-iris-lab/meta-harness

[^1_2]: https://arxiv.org/html/2603.28052v1

[^1_3]: https://github.com/stanford-iris-lab/meta-harness-tbench2-artifact

[^1_4]: https://github.com/SuperagenticAI/metaharness

[^1_5]: https://github.com/revfactory/harness

[^1_6]: https://www.reddit.com/r/LocalLLaMA/comments/1shyczh/stanford_self_improving_metaharness/

[^1_7]: https://github.com/howdymary/hermes-agent-metaharness

[^1_8]: https://github.com/SaehwanPark/meta-harness


---

# I want a quick conceptual overview of how it works and how it relates to Karpathy's "autoresearch" and how we can use the following QA techniques to build an evolved system we can reuse for the way we operate and adapt to our projects:

Yes, draft these artifacts:
DesireRecord schema.
ImprovementGoal schema.
A short gold_goals.md template that the analysis system can populate.
Then Follow-up with:
→ How to implement AGORA for meta goal modeling in our project
→ What are examples of self-improving meta harnesses in software engineering
→ Steps to build a gap analysis tool integrated with our dependency map
→ How can we measure improvement using GORE metrics like contribution values
→ Merge these ideas into a supporting improved system: meta harness vs golden paths for requirements refinement

Meta-Harness is best thought of as an outer-loop system that improves the **agent wrapper**, while Karpathy’s autoresearch is an outer-loop system that improves the **task program itself**. If you combine them for your workflow, you get a reusable improvement stack: AGORA models what matters, golden goals define success, a meta-harness changes orchestration behavior, and autoresearch-style ratchets keep only changes that measurably help.[^2_1][^2_2][^2_3]

## Core idea

Meta-Harness searches over the harness code around a model or agent, including retrieval logic, memory use, prompt construction, and tool wiring, instead of changing model weights. Its proposer is itself a coding agent with filesystem access to prior code, logs, traces, and scores, so it can inspect regressions and make larger structural edits than a fixed mutation template would allow.[^2_4][^2_1]

Karpathy’s autoresearch uses a similar outer loop, but with a narrower and cleaner optimization target: one editable research file, a fixed time budget, a single metric, and a git-based keep-or-revert ratchet after each experiment. In practice, Meta-Harness is “optimize the operating system around the agent,” while autoresearch is “optimize the executable artifact under a strict evaluation loop.”[^2_5][^2_3][^2_1]

## Relationship to autoresearch

The strongest overlap is the **ratchet loop**: propose a change, run an evaluation, keep the new baseline only if the metric improves, otherwise revert. The key difference is search space: autoresearch edits a constrained task file like `train.py`, while Meta-Harness edits orchestration code and can rewrite how the agent stores experience, retrieves context, and sequences tools.[^2_3][^2_1]

For your environment, the useful synthesis is: use autoresearch discipline for evaluation hygiene and use Meta-Harness breadth for orchestration evolution. That means fixed benchmark tasks, clean rollback, explicit baselines, and reusable harness modules that can adapt to project type, repository state, dependency topology, and requirements maturity.[^2_2][^2_1][^2_3]

## Evolved system

A reusable system for your projects can have five layers:

1. **Desire layer**: captures what stakeholders want, even when vague or conflicting, as candidate desires and pressures rather than finalized requirements.[^2_6][^2_2]
2. **Goal layer**: refines desires into measurable ImprovementGoals using AGORA-style goal decomposition, alternatives, conflicts, and contribution values.[^2_7][^2_2]
3. **Golden layer**: stores a compact `gold_goals.md` file that defines the current accepted success criteria, benchmark tasks, and guardrails for a repo or initiative.[^2_2][^2_3]
4. **Harness layer**: the meta-harness decides how agents retrieve docs, inspect code, traverse the dependency map, ask clarification questions, and choose golden paths for refinement.[^2_1]
5. **Ratchet layer**: every harness revision is evaluated on benchmark suites and accepted only if contribution-weighted outcomes improve without breaking core goals.[^2_3][^2_2]

That architecture makes “how we operate” a first-class artifact, not tribal knowledge.[^2_1][^2_3]

## Artifacts

Below are concise starter artifacts you can drop into your project docs or convert into JSON Schema.

### `DesireRecord` schema

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
    confidence: number  # 0-1
  rationale: string
  signals:
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

This corresponds to the early AGORA/GORE need to establish initial goals from customer needs before decomposition and selection among alternatives.[^2_2]

### `ImprovementGoal` schema

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
    contribution_to_parent: number   # e.g. -100 to +100
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

AGORA explicitly adds contribution values and preference information to goal graphs so analysts can compare alternatives, reason about change impact, and improve requirements quality.[^2_7][^2_2]

### `gold_goals.md` template

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
|---|---|---|---|---|---|

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

This template mirrors the autoresearch philosophy of explicit program instructions plus a keep-or-revert baseline, while adding AGORA-style weighted goal reasoning.[^2_3][^2_2]

## AGORA in your project

To implement AGORA for meta goal modeling in LATTICE OS, model goals across three linked graphs: product goals, workflow goals, and orchestration goals. Product goals cover outcomes like ingest point clouds faster or improve segmentation quality; workflow goals cover developer effort, traceability, and reuse; orchestration goals cover agent routing, dependency-aware retrieval, and benchmark stability.[^2_1][^2_2]

Then attach attributes to nodes and edges: preference weight, contribution value, confidence, dependency criticality, and volatility. Your dependency map becomes the grounding layer, so each goal can reference impacted packages, services, schemas, prompts, notebooks, or pipelines, which makes gap analysis and change-impact reasoning operational instead of aspirational.[^2_7][^2_2]

## Self-improving harness examples

Examples in software engineering include:

- A coding harness that learns which files to inspect first based on historical bug-fix success and repository topology, then updates retrieval ordering and summarization policy over time.[^2_1]
- A PR-review harness that rewrites its own review checklist, static-analysis sequence, and failure triage prompts based on which comments led to accepted fixes versus noise.[^2_1]
- A test-generation harness that changes how it mines dependency edges, stack traces, and failing snapshots to propose higher-yield regression tests.[^2_1]
- Autoresearch itself is a narrow example: the agent improves a training script under a fixed metric and keeps only metric-improving revisions.[^2_5][^2_3]

The reusable lesson is to separate the task artifact from the operational harness so you can improve both independently.[^2_3][^2_1]

## Gap analysis and metrics

To build a gap analysis tool integrated with your dependency map:

1. Ingest goals, desires, components, and dependencies into one graph keyed by stable IDs.[^2_2]
2. Link each ImprovementGoal to affected nodes: repos, modules, data assets, prompts, tools, pipelines.[^2_2]
3. Compute coverage gaps, such as goals with no benchmark, dependencies with no owning goal, or critical paths touched by no validation plan.[^2_2]
4. Rank gaps by a composite score: preference weight, dependency centrality, risk penalty, and uncertainty.[^2_2]
5. Feed those ranked gaps into the meta-harness as candidate improvement opportunities.[^2_1]

A simple GORE-inspired contribution score can be defined as: weighted contribution $=$ contribution_to_parent $\times$ preference_weight $\times$ confidence $\times$ validation_pass_rate, which gives you a practical acceptance heuristic for harness changes. At the portfolio level, track metrics like goal coverage, benchmark coverage, guardrail pass rate, regression frequency, mean improvement per accepted change, and dependency-risk-adjusted contribution value.[^2_7][^2_3][^2_2]

## Meta harness vs golden paths

Golden paths and meta-harnesses solve different problems, so the best system uses both. Golden paths encode the preferred refinement route for recurring work, such as “turn stakeholder desire into benchmarked ImprovementGoal into dependency-linked implementation ticket,” while the meta-harness decides when to follow that path strictly, when to branch, and how to improve the path itself from evidence.[^2_3][^2_2][^2_1]

A useful merged pattern is:

- Golden paths define canonical refinement workflows and artifact shapes.[^2_2]
- `gold_goals.md` defines what winning currently means for a project.[^2_3][^2_2]
- The meta-harness adapts retrieval, planning, and decomposition behavior to fit the project context.[^2_1]
- The autoresearch ratchet accepts only changes that improve weighted goal outcomes on the benchmark set.[^2_3]

That gives you a durable operating model: stable enough to reuse, adaptive enough to evolve.[^2_3][^2_1]

Would you like me to turn this into a concrete repo starter pack with `desire-record.schema.json`, `improvement-goal.schema.json`, and `gold_goals.md` files?
<span style="display:none">[^2_10][^2_11][^2_12][^2_13][^2_14][^2_15][^2_8][^2_9]</span>

<div align="center">⁂</div>

[^2_1]: https://arxiv.org/html/2603.28052v1

[^2_2]: https://www-di.inf.puc-rio.br/~julio/agora-re02.pdf

[^2_3]: https://github.com/stanford-iris-lab/meta-harness

[^2_4]: https://arxiv.org/abs/2603.28052

[^2_5]: https://github.com/karpathy/autoresearch

[^2_6]: https://faculty.sites.iastate.edu/sbasu/gore-pref

[^2_7]: https://dl.acm.org/doi/10.5555/647648.760603

[^2_8]: https://arxiv.org/pdf/2603.28052.pdf

[^2_9]: https://arxiviq.substack.com/p/meta-harness-end-to-end-optimization

[^2_10]: https://www.linkedin.com/posts/baraktur_meta-harness-end-to-end-optimization-of-activity-7444744842603143168-KJtv

[^2_11]: https://www.verdent.ai/guides/what-is-autoresearch-karpathy

[^2_12]: https://yoonholee.com/meta-harness/

[^2_13]: https://www.reddit.com/r/singularity/comments/1roo6v0/andrew_karpathys_autoresearch_an_autonomous_loop/

[^2_14]: https://huggingface.co/papers/2603.28052

[^2_15]: https://hackernoon.com/i-let-karpathys-autoresearch-agent-run-overnight


---

# What QA techniques can integrate with Meta-Harness for better optimization

The most effective QA techniques to pair with Meta-Harness are ones that (1) give rich, structured feedback per run, and (2) are cheap and deterministic enough to drive many outer-loop iterations. In practice, that means moving beyond a single scalar score into layered checks: correctness, safety, robustness, trace quality, and cost/latency — all logged in the filesystem Meta-Harness already uses as its memory.[^3_1][^3_2][^3_3]

Below I’ll group concrete QA techniques you can plug into a Meta-Harness-style loop.

***

## 1. Strong task-level evaluation

Meta-Harness already optimizes against task scores (e.g., accuracy on text classification, pass rate on TerminalBench), but you can enrich this layer with more nuanced QA.[^3_2][^3_1]

Key techniques:

- **Deterministic benchmark suites**
Use frozen task suites with deterministic scoring: unit-test style checks for coding harnesses, exact-match / F1 for QA, and strict numerical thresholds for math. This gives a stable primary objective and makes regressions obvious from run to run.[^3_1][^3_2]
- **Multi-metric objectives (accuracy + cost + latency)**
One advantage of Meta-Harness is the ability to optimize for multi-dimensional objectives like accuracy vs. context tokens vs. wall-clock time. Extending QA here means logging at least:[^3_2]
    - success/failure per task
    - context tokens used and number of tool calls
    - total runtime and peak memory
You can then either scalarize (e.g., weighted sum) or trace a Pareto frontier of harness variants and choose a point with acceptable trade-offs.[^3_2]
- **Model-agnostic evaluation**
Meta-Harness shows that a discovered harness can transfer to multiple models and still improve average accuracy. A QA extension is:[^3_1]
    - evaluate each candidate harness across a small panel of models (e.g., strong + cheap variants)
    - penalize candidates that only shine on one model but regress on others
This mitigates overfitting the harness to quirks of a specific backend.[^3_1]

***

## 2. Rich execution-trace QA

The core Meta-Harness idea is search **with selective access to diagnostic experience**, not just scores. QA should therefore add structure to traces.[^3_2][^3_1]

Useful techniques:

- **Structured trace logging**
For every run, capture:
    - tool call sequence (with inputs/outputs)
    - errors and exceptions
    - timeouts, retries, and branch choices
    - prompt/context snapshots at key checkpoints
Meta-Harness already uses a filesystem-backed store of code, scores, and traces so the proposer can “grep” failures and see which harness decision caused them. QA here is about schema and coverage: making sure traces are complete, consistent across iterations, and cheap enough to keep.[^3_3][^3_1][^3_2]
- **Failure-mode classification**
Add an automated pass that labels each failure with a cause category like:
    - retrieval-miss
    - tool misuse
    - hallucinated assumption
    - timeout/looping
    - formatting/parsing error
You can implement this as a secondary LLM classifier over the trace, or as heuristic matchers on logs. Meta-Harness benefits because the coding agent can search “where do retrieval misses cluster?” instead of staring at a flat list of failed tasks.[^3_1][^3_2]
- **Invariant checks and contracts**
For coding harnesses, add QA that verifies invariants regardless of task outcome:
    - no unbounded loops or recursive tool calls
    - maximum context/token budget per step
    - no writes outside designated workspace
    - consistent environment bootstrap (no hidden state leakage across candidates)
The Superagentic metaharness implementation, for example, explicitly captures a compact environment bootstrap snapshot before optimization and validates candidate workspaces with deterministic checks. Those validations are QA gates in the optimization loop.[^3_4][^3_3]

***

## 3. Harness-structure QA

Since Meta-Harness edits code, harness quality itself becomes a QA target.[^3_3][^3_2]

Techniques you can plug in:

- **Static analysis \& linting of harness code**
Run style and safety checks on the harness:
    - linters and type checkers
    - forbidden patterns (hard-coded secrets, wildcards, brittle if-chains)
    - overly complex branching or deeply nested control flow
The paper notes that code-space overfitting is more inspectable: “brittle if-chains or hard-coded mappings” are visible in code in a way weight-space overfitting is not. QA can automatically flag such patterns and reduce their score or block them.[^3_2]
- **Diff-aware QA between baseline and candidate harnesses**
Instead of just testing final behavior, run a static diff between baseline and candidate:
    - identify changed files and functions
    - compute basic complexity metrics (function length, cyclomatic complexity)
    - ensure critical guardrails (safety checks, constraints) were not removed
You can then:
    - down-weight candidates with large complexity increases unless they buy significant accuracy
    - reject candidates that weaken guardrails, even if scores improve
- **Configuration \& prompt schema validation**
If your harness defines tools, prompts, or configurations declaratively (e.g., YAML/json), add schema validation and semantic checks:
    - all tool references resolved
    - required tool arguments present
    - prompt templates remain well-formed with required slots
This prevents “partially broken” harnesses from entering runtime evaluation.

***

## 4. Robustness and adversarial QA

Beyond “average-case” performance, QA can probe robustness, which is especially relevant if you’re optimizing harnesses for production workflows.

Ideas:

- **Input fuzzing**
For harnesses that parse instructions or operate on semi-structured inputs, add fuzz tests:
    - inject noise into inputs
    - randomize order or presence of hints
    - test extreme edge lengths
Evaluate how often the harness still routes correctly, formats outputs properly, and avoids crashes.
- **Adversarial / red-team prompts**
Maintain a curated set of prompts that test:
    - prompt injection and jailbreaking
    - attempts to bypass constraints and guardrails
    - ambiguous or conflicting tasks
Reject or penalize harness variants that become more fragile under these sets, even if they improve main-task accuracy.
- **Cross-distribution generalization tests**
The Meta-Harness work shows transfer to held-out corpora and models. QA can extend this by:[^3_1]
    - training/optimizing on one data distribution
    - validating on distinct distributions (other datasets, out-of-domain samples)
This reduces overfitting to the training distribution’s quirks.

***

## 5. Human-in-the-loop and meta-QA

Even though Meta-Harness is designed to reduce human dependence, you can use human feedback more efficiently by integrating it at the right layer.[^3_5]

Techniques:

- **Curated review of harness-change trajectories**
Periodically, a human reviews:
    - sequences of harness edits
    - associated metric history
    - major structural shifts (e.g., new retrieval policy, new tool-flow)
They can label trajectories as “promising,” “degenerate complexity,” or “brittle hack,” and your QA can feed those labels into selection or pruning heuristics.
- **Golden regression tests from real incidents**
When a harness failure causes a real-world incident, convert it into:
    - a new benchmark case
    - a guardrail test that must pass before any candidate is accepted
This gradually tunes QA objectives toward what matters operationally instead of just academic benchmarks.
- **Meta-QA on the optimization loop**
Evaluate the outer-loop itself:
    - success rate: fraction of runs where best candidate beats baseline
    - optimization efficiency: improvement per evaluation (Meta-Harness is reported to match other text optimizers in 0.1× the evaluations and surpass them by >10 points).[^3_2][^3_1]
    - stability: variance in final performance across seeds and search budgets
This lets you debug your optimization process and adjust budgets, proposal strategies, or acceptance criteria.

***

## 6. How to wire these into Meta-Harness

Given the architecture described in the paper and implementations like Superagentic’s `metaharness`, the integration pattern looks like:

1. **Extend the evaluation step**
Instead of producing just a “score.json”, evaluate each candidate harness with a QA pipeline that outputs:
    - `task_metrics.json` (accuracy-like metrics)
    - `cost_metrics.json` (tokens, tools, time)
    - `qa_flags.json` (violations, regression flags, robustness results)
    - `trace/` directory with structured logs and failure classification
Meta-Harness’s proposer can read all of this via filesystem access.[^3_3][^3_1][^3_2]
2. **Define acceptance rules that incorporate QA**
Upgrade the ratchet logic from “score_new > score_best” to something like:
    - `score_new >= score_best - eps`
    - no critical QA flags
    - complexity increase below a threshold, or offset by larger improvement
This mirrors how some metaharness implementations “validate and then evaluate” candidates before accepting them.[^3_4][^3_3]
3. **Expose QA summaries to the proposer**
Ensure the coding agent sees not just raw numbers but compact human-readable summaries and pointers into traces, e.g.:
    - “Most failures labeled retrieval-miss in `module X`”
    - “Adversarial prompts 12–15 failed due to missing guardrail Y”
The paper emphasizes selective access to prior diagnostic experience as a key advantage; your QA summaries are the curated part of that experience.[^3_1][^3_2]
4. **Evolve QA over time**
Treat the QA configuration itself (which tests, which adversarial inputs, thresholds) as another artifact under version control and periodic review. As systems mature, you can tighten thresholds or add new robustness suites.

***

If you describe your current harness (e.g., for coding, retrieval, or multi-agent orchestration in LATTICE), I can propose a concrete QA pipeline and file layout tailored to that setup, including specific JSON schemas and where they plug into the Meta-Harness loop.
<span style="display:none">[^3_6][^3_7][^3_8][^3_9]</span>

<div align="center">⁂</div>

[^3_1]: https://yoonholee.com/meta-harness/

[^3_2]: https://arxiv.org/html/2603.28052v1

[^3_3]: https://shashikantjagtap.net/meta-harness-a-self-optimizing-harness-around-coding-agents/

[^3_4]: https://github.com/SuperagenticAI/metaharness

[^3_5]: https://www.linkedin.com/pulse/meta-harness-automating-benchmaxing-loop-vivek-haldar-hm4qc

[^3_6]: https://x.com/hwchase17/status/2040471961206214864

[^3_7]: https://www.reddit.com/r/singularity/comments/1s81vhz/stanford_researchers_autonomously_improved_a/

[^3_8]: https://testcollab.com/blog/harness-engineering

[^3_9]: https://engineering.fb.com/2026/04/02/developer-tools/kernelevolve-how-metas-ranking-engineer-agent-optimizes-ai-infrastructure/


---

# Lets include this tool Throughout the entire process of this meta-improvement layer, insert it wherever it can be helpful and useful. You're going to need to do quite a bit of research before you assume you understand exactly where it will fit. I want you to research first and then literally take each part of this whole process and then look at how this tool could apply and does apply how this tool can add hardening and even more complete functionality, etc...

INFRANODUS:
[https://infranodus.com/](https://infranodus.com/)
[https://www.youtube.com/@infranodus/videos](https://www.youtube.com/@infranodus/videos)
[https://www.youtube.com/watch?v=mgKQNC7Fqlo](https://www.youtube.com/watch?v=mgKQNC7Fqlo)
[https://www.youtube.com/watch?v=PSJHz8Nwk3M\&list=PLg_R9_eJ-LLNHoMU93VzJRAU3jpdrM_bn](https://www.youtube.com/watch?v=PSJHz8Nwk3M&list=PLg_R9_eJ-LLNHoMU93VzJRAU3jpdrM_bn)
[https://www.youtube.com/watch?v=mgKQNC7Fqlo\&list=PLg_R9_eJ-LLPnH9z2WTW8O4rc0tJGh36h](https://www.youtube.com/watch?v=mgKQNC7Fqlo&list=PLg_R9_eJ-LLPnH9z2WTW8O4rc0tJGh36h)
[https://www.youtube.com/watch?v=qP4KTLBzoWQ\&list=PLg_R9_eJ-LLM0JKhCQFCrkwlMhAVuPnsw](https://www.youtube.com/watch?v=qP4KTLBzoWQ&list=PLg_R9_eJ-LLM0JKhCQFCrkwlMhAVuPnsw)
[https://www.youtube.com/playlist?list=PLg_R9_eJ-LLOjfsUcplu-P8SyZ4bxgoyc](https://www.youtube.com/playlist?list=PLg_R9_eJ-LLOjfsUcplu-P8SyZ4bxgoyc)

Yes — InfraNodus fits **throughout** the meta-improvement layer, not as a side visualization tool but as a structural analysis component for discourse, traces, requirements, gaps, and retrieval contexts. The reason it fits so well is that Meta-Harness improves an agent by inspecting prior code and execution traces, while InfraNodus turns messy text corpora into graph structure with clusters, gateways, gaps, and diversity signals that can be fed back into prompt design, RAG, benchmark design, and goal modeling.[^4_1][^4_2][^4_3]

## What InfraNodus adds

InfraNodus represents text as a network of concepts connected by co-occurrence, ranks influential concepts with betweenness centrality, detects topical communities, and highlights structural gaps between clusters that could be bridged with new questions or ideas. Its API can return graph JSON, statements, graph summaries, content gaps, conceptual gateways, diversity statistics, and AI advice modes such as `develop`, `reinforce`, `gaps`, and `imagine`, which makes it usable as a machine-facing analysis primitive rather than only a human dashboard.[^4_4][^4_5][^4_2][^4_3]

That is important for your system because your meta-improvement layer is not just optimizing code; it is optimizing understanding, decomposition, retrieval, and requirements refinement across changing projects. InfraNodus gives you a way to quantify when discourse is too biased, too focused, diversified, or dispersed, and to ask the next bridging question from graph structure instead of intuition alone.[^4_6][^4_3][^4_1]

## Where it fits

Below is the full process with InfraNodus inserted at every meaningful stage.


| Process stage | How InfraNodus applies | Hardening / functionality gained |
| :-- | :-- | :-- |
| Desire capture | Build graphs from stakeholder notes, issue threads, meetings, docs, Slack/Obsidian exports.[^4_3] | Detect recurring concepts, hidden clusters, neglected concerns, and early requirement blind spots.[^4_2][^4_3] |
| Goal modeling | Analyze DesireRecords and draft ImprovementGoals as a graph of concepts and tensions.[^4_2][^4_3] | Exposes disconnected goal areas, over-dominant narratives, and candidate bridges for AGORA refinement.[^4_2][^4_3] |
| `gold_goals.md` creation | Generate a graph summary of accepted goals and compare it to raw desires.[^4_3] | Shows which accepted goals underrepresent original intent, which is excellent for governance drift detection.[^4_3] |
| Retrieval / GraphRAG | Use API graph summaries, DOT graphs, cluster keywords, and conceptual gateways to augment prompts and retrieval.[^4_3][^4_7] | Better context packing, more diverse retrieval, less overfocus on dominant nodes, stronger bridging between repositories and doc sets.[^4_3] |
| Meta-Harness proposal loop | Feed prior traces, failures, benchmark reports, and repo notes into InfraNodus before proposing edits.[^4_1][^4_3] | Lets the proposer see structural failure themes and missing bridges, not just flat logs.[^4_1][^4_2] |
| QA / regression analysis | Graph failed runs, incident reports, and evaluator comments.[^4_3] | Surfaces repeated failure motifs, brittle concepts, and latent regression clusters faster than manual review.[^4_3] |
| Gap analysis | Compare desired-state graph vs current implementation graph using `compareGraphs` and difference modes.[^4_3] | Converts gap analysis from checklist work into structural delta analysis.[^4_3] |
| Dependency-map integration | Project statements from dependency nodes, ownership docs, interfaces, ADRs, and runbooks into graphs.[^4_3] | Identifies central components, weakly connected modules, and concept bridges across subsystems.[^4_3] |
| Benchmark design | Use structural gaps to generate benchmark questions and edge-case tasks.[^4_2][^4_3] | Better coverage of blind spots, not just happy-path tests.[^4_2] |
| Continuous improvement | Compare graphs over time for repo, project, or program evolution.[^4_3] | Lets you measure whether discourse is becoming broader, more coherent, or more biased during optimization.[^4_3] |

## Best uses in your stack

For LATTICE-style work, the highest-value insertion points are these:

- **Requirements refinement**: ingest project briefs, agent plans, PRDs, ADRs, benchmark notes, and meeting transcripts into InfraNodus; use structural gaps to draft clarifying questions before implementation starts.[^4_2][^4_3]
- **Harness memory shaping**: before the harness retrieves context, run InfraNodus summaries over candidate corpora and use top clusters, gaps, and gateways as retrieval hints or query expansion features.[^4_7][^4_3]
- **Failure clustering**: treat failed agent traces as statements; cluster by concept and bridge nodes; rank failure brokers by betweenness centrality to find the small set of recurring chokepoints.[^4_3][^4_2]
- **Golden-path auditing**: compare the graph of your canonical workflow docs against the graph of actual issues, incidents, or experiments to find where the golden path is missing reality.[^4_3]

In other words, InfraNodus is especially strong whenever the problem is “we have too much text and not enough structural understanding.”[^4_2][^4_3]

## A concrete architecture

A strong reusable architecture would look like this:

1. **Ingestion layer**
Collect stakeholder notes, repo docs, benchmark specs, traces, incident reports, dependency descriptions, and goals as timestamped statements.[^4_3]
2. **InfraNodus analysis layer**
Use `graphAndStatements` for graph JSON and summaries, `graphAndAdvice` for bridge questions and improvement ideas, and `compareGraphs` for desired-vs-current or baseline-vs-candidate structural comparison.[^4_3]
3. **Meta-goal layer**
Convert clusters into candidate domains, gaps into ImprovementGoal prompts, conceptual gateways into cross-cutting architecture themes, and diversity stats into QA signals on whether your process is too narrow or too scattered.[^4_3]
4. **Meta-Harness layer**
The proposer agent reads InfraNodus outputs alongside code, scores, and traces, then edits retrieval policies, decomposition prompts, workflow rules, and benchmark sets.[^4_1][^4_3]
5. **Ratchet / QA layer**
Accept candidate harness changes only when benchmark metrics improve and the associated discourse graph does not become more biased in a harmful way unless that narrowing is explicitly desired for the task.[^4_8][^4_3]

This is very aligned with Karpathy’s autoresearch discipline, where a fixed loop proposes, tests, and keeps improvements, except here the optimization target is broader and the evidence includes graph-structured discourse intelligence.[^4_8][^4_1]

## Hardening patterns

InfraNodus can harden the system in several specific ways:

- **Blind-spot hardening**: structural gaps become first-class QA targets, so the system must explain how a change addresses or deliberately ignores them.[^4_2][^4_3]
- **Bias hardening**: diversity statistics can flag when the process is overly dominated by a few top nodes or clusters, which is useful when one subsystem or narrative hijacks planning.[^4_3]
- **Drift hardening**: compare the graph of raw desires to approved goals and later to implementation docs to detect semantic drift across the lifecycle.[^4_3]
- **Retrieval hardening**: use gateway nodes and gap topics to diversify retrieval instead of always pulling from the densest cluster.[^4_7][^4_3]
- **Trace hardening**: graph execution failures so the harness can recognize recurring failure brokers and modify its operating policy accordingly.[^4_1][^4_3]

These are not cosmetic benefits; they make the outer loop more causally informed and less likely to optimize a narrow proxy.[^4_1][^4_3]

## How to apply it step by step

Here is the process I would recommend for your evolved system:

1. **Desire intake**
Send captured statements from stakeholders, docs, and roadmap notes to InfraNodus `graphAndStatements` with `extendedGraphSummary=true`.[^4_3]
2. **Question generation**
Use `graphAndAdvice` with `optimize=gaps` and `requestMode=question` to generate clarifying questions that bridge underconnected requirement areas.[^4_3]
3. **ImprovementGoal drafting**
Convert top clusters into goal areas, content gaps into unresolved tensions, and conceptual gateways into likely leverage points or architectural connectors.[^4_3]
4. **Golden goal validation**
Compare the graph of accepted goals to the graph of original desires using `compareGraphs` in `difference` mode to see what was lost or overemphasized.[^4_3]
5. **Dependency-aware gap analysis**
Build parallel graphs from dependency descriptions, ADRs, module docs, and incident records; compare these with the goal graph to identify structurally uncovered modules or concepts.[^4_3]
6. **Harness optimization**
Provide InfraNodus summaries as structured context for Meta-Harness proposal iterations so the coding agent edits not only from logs, but from discourse-level patterns.[^4_1][^4_3]
7. **Continuous QA**
Graph benchmark failures, human review notes, and regression reports every cycle; track whether failure structure is shrinking or merely moving.[^4_3]

## Specific API patterns

The most useful InfraNodus endpoints for your use case are:

- `POST /api/v1/graphAndStatements` for converting text or statement arrays into graph JSON, statements, and extended summaries.[^4_3]
- `POST /api/v1/graphAndAdvice` for generating graph-informed questions, ideas, summaries, or reprompts with modes like `develop`, `reinforce`, `gaps`, and `latent`.[^4_3]
- `POST /api/v1/compareGraphs` for merging, overlapping, or differencing desired-state and current-state corpora.[^4_3]
- `POST /api/v1/graphsAndAiAdvice` for graph-aware advice across several corpora or their difference graph.[^4_3]
- `POST /api/v1/dotGraph` or `/dotGraphFromText` for compact graph context you can inject into prompts and agent memory.[^4_3]

A very practical pattern is to keep a `statements/` directory in your meta-improvement repo and continuously derive InfraNodus graph artifacts per stage: `desires.graph.json`, `goals.graph.json`, `traces.graph.json`, `dependencies.graph.json`, and `delta.goal-vs-implementation.graph.json`.[^4_3]

## Meta harness vs golden paths with InfraNodus

InfraNodus makes the distinction cleaner. Golden paths define the canonical steps for requirements refinement and delivery, while the meta-harness adapts and improves those steps; InfraNodus sits between them as the structural sensing layer that tells you where the golden path is incomplete, overfocused, or disconnected.[^4_2][^4_1][^4_3]

So the merged system becomes:

- Golden paths = the preferred workflow skeleton.[^4_8]
- InfraNodus = the discourse graph sensor and gap detector.[^4_2][^4_3]
- Meta-Harness = the self-improving orchestration layer that rewrites behavior from evidence.[^4_1]
- Autoresearch ratchet = the acceptance discipline that keeps only measured improvements.[^4_8]

That combination is unusually strong because it joins structural reasoning, operational adaptation, and controlled optimization into one loop.[^4_8][^4_1][^4_3]

## Recommendation

For your workflow, I would not treat InfraNodus as a UI-only research aid. I would treat it as a reusable analysis service inside the meta-improvement layer: one part requirements intelligence, one part GraphRAG augmentation, one part failure-cluster detector, and one part governance drift monitor.[^4_7][^4_2][^4_3]

The next best move is to turn this into an implementation blueprint with:

- an InfraNodus insertion matrix by lifecycle stage,
- a proposed folder layout for graph artifacts,
- schemas for DesireRecord and ImprovementGoal enriched with graph fields,
- and a concrete Claude Code / Meta-Harness loop showing exactly when each InfraNodus endpoint is called.
<span style="display:none">[^4_10][^4_11][^4_12][^4_13][^4_14][^4_15][^4_16][^4_17][^4_18][^4_9]</span>

<div align="center">⁂</div>

[^4_1]: https://arxiv.org/html/2603.28052v1

[^4_2]: https://github.com/stanford-iris-lab/meta-harness

[^4_3]: https://github.com/stanford-iris-lab/meta-harness-tbench2-artifact

[^4_4]: https://infranodus.com/use-case/text-network-analysis

[^4_5]: https://infranodus.com/api/docs

[^4_6]: https://infranodus.com/use-case/text-mining

[^4_7]: https://infranodus.com/use-case/ai-knowledge-graphs

[^4_8]: https://github.com/SuperagenticAI/metaharness

[^4_9]: https://infranodus.com

[^4_10]: https://infranodus.com/docs/text-network-analysis

[^4_11]: https://infranodus.com/graphs

[^4_12]: https://infranodus.com/about/how-it-works

[^4_13]: https://infranodus.com/api

[^4_14]: https://arxiv.org/abs/2603.28052

[^4_15]: https://infranodus.com/docs

[^4_16]: https://infranodus.com/use-case/network-analysis-visualization

[^4_17]: https://arxiviq.substack.com/p/meta-harness-end-to-end-optimization

[^4_18]: https://noduslabs.com/infranodus/


---

# Example code for InfraNodus graph analysis in harness evaluation

Benefits of structural gap detection for QA techniques in Meta-Harness

Here’s a concrete way to use InfraNodus inside harness evaluation: treat run traces, benchmark explanations, failure notes, and requirement text as analyzable discourse, then convert the resulting graph summaries, gap reports, and graph differences into evaluation features and acceptance gates for Meta-Harness candidates. The main benefit is that structural gap detection adds a second layer of QA beyond scalar pass rates, helping the harness optimize not just for “did it pass” but also for “what parts of the problem space remain disconnected, underexplored, or repeatedly bridged badly.”[^5_1][^5_2][^5_3][^5_4][^5_5]

## Example code

Below is a Python example that shows three useful patterns: analyze a single candidate’s failure corpus, compare baseline vs candidate traces, and ask InfraNodus for graph-informed questions to improve the next harness iteration.[^5_6][^5_1]

```python
import os
import json
import requests
from pathlib import Path

API_TOKEN = os.environ["INFRANODUS_API_TOKEN"]
BASE_URL = "https://infranodus.com/api/v1"
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json",
}

def infranodus_post(endpoint, params=None, payload=None):
    url = f"{BASE_URL}/{endpoint}"
    r = requests.post(url, params=params or {}, headers=HEADERS, json=payload or {})
    r.raise_for_status()
    return r.json()

def load_texts(folder):
    texts = []
    for path in sorted(Path(folder).glob("*.md")) + sorted(Path(folder).glob("*.txt")) + sorted(Path(folder).glob("*.json")):
        text = path.read_text(encoding="utf-8")
        if path.suffix == ".json":
            try:
                obj = json.loads(text)
                text = json.dumps(obj, indent=2)
            except Exception:
                pass
        texts.append({"text": text, "title": path.name})
    return texts

def concat_contexts(contexts, max_docs=30):
    merged = []
    for c in contexts[:max_docs]:
        title = c.get("title", "untitled")
        text = c.get("text", "")
        merged.append(f"# {title}\n{text}")
    return "\n\n".join(merged)

def analyze_failure_graph(candidate_dir):
    corpus = concat_contexts(load_texts(candidate_dir))
    return infranodus_post(
        "graphAndStatements",
        params={
            "doNotSave": "true",
            "addStats": "true",
            "extendedGraphSummary": "true"
        },
        payload={
            "text": corpus
        }
    )

def compare_baseline_candidate(baseline_dir, candidate_dir):
    baseline = concat_contexts(load_texts(baseline_dir))
    candidate = concat_contexts(load_texts(candidate_dir))
    return infranodus_post(
        "compareGraphs",
        params={
            "doNotSave": "true",
            "addStats": "true"
        },
        payload={
            "contexts": [
                {"text": baseline, "title": "baseline"},
                {"text": candidate, "title": "candidate"}
            ],
            "compareMode": "difference"
        }
    )

def generate_gap_questions(candidate_dir):
    corpus = concat_contexts(load_texts(candidate_dir))
    return infranodus_post(
        "graphAndAdvice",
        params={
            "doNotSave": "true",
            "addStats": "true",
            "optimize": "gaps"
        },
        payload={
            "text": corpus,
            "requestMode": "question"
        }
    )

def score_candidate_with_graph_signals(eval_json_path, candidate_dir, baseline_dir=None):
    eval_data = json.loads(Path(eval_json_path).read_text())
    task_score = eval_data["task_score"]
    failure_rate = eval_data.get("failure_rate", 0.0)

    graph = analyze_failure_graph(candidate_dir)
    summary = graph.get("graphSummary", {})
    stats = graph.get("stats", {})

    # Adjust these field names to actual InfraNodus response keys in your setup
    diversity = stats.get("diversity", 0.0)
    influence_concentration = stats.get("betweennessCentralization", 0.0)

    penalty = 0.0
    if failure_rate > 0.2:
        penalty += 0.15
    if influence_concentration > 0.8:
        penalty += 0.10   # failures too concentrated around a few chokepoints
    if diversity < 0.15:
        penalty += 0.05   # candidate may be overfitting a narrow discourse band

    diff = None
    if baseline_dir:
        diff = compare_baseline_candidate(baseline_dir, candidate_dir)

    advice = generate_gap_questions(candidate_dir)

    final_score = task_score - penalty

    return {
        "task_score": task_score,
        "penalty": penalty,
        "final_score": final_score,
        "graph_summary": summary,
        "graph_stats": stats,
        "baseline_diff": diff,
        "gap_questions": advice.get("aiAdvice"),
    }

if __name__ == "__main__":
    result = score_candidate_with_graph_signals(
        eval_json_path="runs/candidate_017/eval.json",
        candidate_dir="runs/candidate_017/traces",
        baseline_dir="runs/baseline/traces",
    )
    Path("runs/candidate_017/infranodus_eval.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    print("Saved graph-aware evaluation to runs/candidate_017/infranodus_eval.json")
```

This works because InfraNodus exposes endpoints for graph generation from text, graph-informed advice, and graph comparison, while Meta-Harness explicitly benefits from access to full trace history and diagnostic context rather than compressed summaries alone.[^5_4][^5_1][^5_6]

## Where to plug it in

The best insertion points in a Meta-Harness loop are:

- **After each candidate evaluation**: send failure traces, tool logs, and benchmark rationales to `graphAndStatements` to extract graph structure and stats.[^5_1][^5_4]
- **Before the next proposal**: send the same corpus to `graphAndAdvice` with `optimize=gaps` so the proposer gets bridge questions and missing-topic prompts instead of only a raw score.[^5_3][^5_1]
- **When comparing candidates**: use `compareGraphs` or `graphsAndAiAdvice` on baseline vs candidate traces to detect whether a “better” candidate only shifted failures around or actually reduced structural blind spots.[^5_1]

That gives you a graph-aware outer loop: candidate, evaluate, graph, compare, advise, revise.[^5_4][^5_1]

## Structural gap benefits

Structural gap detection is especially valuable for QA because InfraNodus defines gaps as distant topical clusters that are insufficiently connected, which exposes blind spots in the discourse and suggests bridge questions or ideas. In Meta-Harness terms, those blind spots often correspond to untested assumptions, weak retrieval joins, missing workflow transitions, or failure modes that standard success metrics do not reveal.[^5_5][^5_3][^5_4]

The practical benefits are:

- **Blind-spot discovery**: it shows what the harness is not connecting, such as “dependency migration” and “rollback policy” appearing as separate clusters in incident traces.[^5_3][^5_5]
- **Failure clustering**: repeated regressions often gather around a few broker concepts, making it easier to find chokepoints in planning or tool routing.[^5_5][^5_4]
- **Benchmark expansion**: gaps can be turned into new benchmark tasks or adversarial cases, improving coverage over time.[^5_3][^5_1]
- **Retrieval hardening**: bridge nodes and cluster summaries can guide more diverse context selection instead of repeatedly retrieving from the densest topic only.[^5_7][^5_1]
- **Governance drift detection**: compare desired-goal corpora with implementation or incident corpora to spot where the system has semantically drifted from intended outcomes.[^5_1][^5_3]


## QA techniques improved

Structural gap detection strengthens several QA techniques you asked about earlier:


| QA technique | How gap detection improves it |
| :-- | :-- |
| Regression testing | Reveals whether regressions cluster in previously disconnected concepts, not just whether pass rate changed.[^5_3][^5_4] |
| Failure analysis | Converts logs into concept clusters and bridge failures, making root-cause analysis faster.[^5_5][^5_4] |
| Benchmark design | Generates new tests from missing bridges between clusters.[^5_3][^5_1] |
| Prompt / policy QA | Shows whether a new harness narrows discourse too aggressively or misses required conceptual transitions.[^5_5][^5_3] |
| RAG QA | Highlights over-dominant retrieval areas and underrepresented topics, improving context diversity.[^5_7][^5_1] |
| Requirements QA | Compares raw desires and accepted goals to detect omissions and semantic drift.[^5_1][^5_3] |

This matters because Meta-Harness works best when the proposer can form causal hypotheses from rich evidence, and graph gaps are a compact causal hint about what is systematically missing rather than merely failing.[^5_4]

## A useful scoring pattern

A practical graph-aware QA score for harness selection is:

- Base score = task metric from your benchmark.[^5_4]
- Subtract penalties for repeated high-centrality failure brokers, low discourse diversity when breadth is required, or newly introduced gaps in critical clusters.[^5_5][^5_3]
- Add credit when a candidate reduces baseline-vs-candidate difference in critical failure themes or meaningfully bridges previously disconnected requirement areas.[^5_3][^5_1]

That keeps the acceptance rule closer to operational quality than a single pass/fail metric.[^5_1][^5_4]

## Minimal file layout

A simple harness-evaluation layout could be:

- `runs/<candidate>/eval.json` — scalar metrics.
- `runs/<candidate>/traces/` — tool logs, error reports, rationales, benchmark notes.
- `runs/<candidate>/infranodus_eval.json` — graph stats, summaries, gap questions, comparison diffs.
- `runs/<candidate>/acceptance.json` — final keep/reject decision with graph-aware reasoning.

This mirrors the Meta-Harness principle that the optimizer should have direct access to prior source, scores, and traces, while InfraNodus adds graph-derived structure on top of those raw artifacts.[^5_4][^5_1]

## Example acceptance rule

A good first acceptance policy is:

- Accept only if benchmark score improves or stays within epsilon.[^5_4]
- Reject if critical QA guardrails fail.[^5_1]
- Reject if structural gap analysis shows new unbridged gaps in required domains like safety, rollback, or dependency integrity.[^5_3]
- Prefer candidates whose graph advice shifts from “ask missing bridge questions” toward “reinforce and develop” on the target domain, because that suggests the discourse has become more connected and actionable.[^5_1]

That gives you a stronger optimization loop without replacing your existing benchmark suite.[^5_3][^5_4]

Would you like me to turn this into a reusable evaluator module with a typed Python wrapper around the InfraNodus endpoints and a sample `candidate_acceptance.py` policy?
<span style="display:none">[^5_10][^5_11][^5_12][^5_13][^5_14][^5_15][^5_8][^5_9]</span>

<div align="center">⁂</div>

[^5_1]: https://infranodus.com/api/docs

[^5_2]: https://yoonholee.com/meta-harness/

[^5_3]: https://infranodus.com/about/how-it-works

[^5_4]: https://arxiv.org/html/2603.28052v1

[^5_5]: https://infranodus.com/use-case/text-network-analysis

[^5_6]: https://support.noduslabs.com/hc/en-us/articles/13605983537692-InfraNodus-API-Access-Points

[^5_7]: https://infranodus.com/docs/graph-rag-knowledge-graph

[^5_8]: https://infranodus.com/api

[^5_9]: https://github.com/noduslabs/infranodus

[^5_10]: https://infranodus.com/docs/knowledge-graphs-llm-reasoning

[^5_11]: https://infranodus.com/docs

[^5_12]: https://www.linkedin.com/posts/baraktur_meta-harness-end-to-end-optimization-of-activity-7444744842603143168-KJtv

[^5_13]: https://ryuchen.github.io/essay/0x00000C.files/1-WWW- InfraNodus- Generating Insight Using Text Network Analysis.pdf

[^5_14]: https://www.obsidianstats.com/plugins/infranodus-graph-view

[^5_15]: https://arxiv.org/abs/2603.28052


---

# Step-by-step InfraNodus integration into Meta-Harness proposer

Here is the cleanest way to integrate InfraNodus into the Meta-Harness proposer: add a graph-analysis substep between “inspect prior traces” and “draft the next harness edit,” so the proposer sees not only raw logs and scores but also graph summaries, structural gaps, and baseline-vs-candidate discourse differences derived from those logs.[^6_1][^6_2][^6_3]

## Integration loop

The Meta-Harness proposer already works by reading prior candidate source, scores, and execution traces from the filesystem and then proposing the next harness revision. InfraNodus fits as a derived-analysis layer on top of that history: it turns traces, benchmark notes, failure explanations, and goal docs into graph artifacts that reveal clusters, gaps, and bridge questions for the proposer to act on.[^6_4][^6_2][^6_3][^6_1]

The revised loop becomes:

1. Read prior candidates and traces from the filesystem.[^6_3]
2. Build stage-specific text corpora from failures, successes, requirements, and benchmark rationales.[^6_1]
3. Send those corpora to InfraNodus for graph summaries and gap-oriented advice.[^6_4][^6_1]
4. Save the returned graph artifacts back into the Meta-Harness workspace.[^6_3][^6_1]
5. Let the proposer read both raw traces and InfraNodus outputs before editing the harness.[^6_2][^6_3]
6. Evaluate the new candidate and repeat.[^6_3]

## Step by step

### 1. Normalize proposer inputs

Create a preprocessing step that converts each prior run into a compact text bundle: `score.md`, `failure_summary.md`, `tool_trace.md`, `benchmark_rationale.md`, and optionally `requirements_context.md`. This matters because InfraNodus works best on coherent textual statements or corpora, while Meta-Harness works best when the proposer can still drill back into raw files for specifics.[^6_2][^6_1][^6_3]

### 2. Create analysis corpora

Build separate corpora for different questions instead of one giant dump. A good split is:[^6_1]

- `corpus_failures.txt` for failed traces and incident notes.[^6_1]
- `corpus_successes.txt` for successful runs and strong rationales.[^6_1]
- `corpus_goals.txt` for `gold_goals.md`, requirements, and evaluation criteria.[^6_1]
- `corpus_diff_inputs.json` for baseline-vs-candidate comparison.[^6_1]

This separation gives the proposer more targeted graph signals, such as “why failures cluster” versus “what goals are underrepresented.”[^6_5][^6_6]

### 3. Run InfraNodus graph extraction

Call `graphAndStatements` first on each corpus to obtain graph structure, summaries, topical communities, and stats. Use `doNotSave=true`, `addStats=true`, and `extendedGraphSummary=true` so the output is analysis-ready without persisting anything externally.[^6_4][^6_1]

The output should be saved into files such as:

- `analysis/infranodus/failures.graph.json`[^6_1]
- `analysis/infranodus/successes.graph.json`[^6_1]
- `analysis/infranodus/goals.graph.json`[^6_1]

These files become first-class proposer inputs just like scores and traces.[^6_3]

### 4. Ask for gap-oriented advice

Call `graphAndAdvice` on the failure and goal corpora with `optimize=gaps` and usually `requestMode=question`. InfraNodus documents that this mode identifies structural gaps in the discourse graph and directs the prompt to bridge them, with `gapDepth` available to probe deeper or less obvious gaps.[^6_4][^6_1]

Save these outputs as:

- `analysis/infranodus/failures.gap_questions.md`[^6_1]
- `analysis/infranodus/goals.gap_questions.md`[^6_1]

These are especially useful as proposer prompts like: “What concept bridge is repeatedly missing between dependency integrity and rollback policy?” rather than “improve the harness somehow.”[^6_7][^6_5]

### 5. Compare baseline vs candidate histories

Use `compareGraphs` or `graphsAndAiAdvice` with `compareMode=difference` on baseline and current-best candidate corpora. This identifies what changed structurally in the discourse between two harness versions, which is important because a candidate may improve pass rate while introducing new blind spots or simply shifting failures into a different cluster.[^6_5][^6_1]

Store the result as:

- `analysis/infranodus/baseline_vs_best.diff.json`[^6_1]
- `analysis/infranodus/baseline_vs_best.advice.md`[^6_1]

This gives the proposer a structural delta view, not just metric delta.[^6_1]

### 6. Add a proposer briefing file

Before each proposal, synthesize a short machine-readable briefing file such as `proposal_brief.md` that contains:

- top failure clusters from InfraNodus.[^6_1]
- major structural gaps and bridge questions.[^6_4]
- dominant goal clusters from goal analysis.[^6_1]
- graph differences between baseline and best current candidate.[^6_1]
- the current benchmark and guardrail status from Meta-Harness evaluation.[^6_3]

This is the key handoff object. Meta-Harness is strong because the proposer can inspect raw history selectively; the briefing should accelerate that inspection, not replace it.[^6_2][^6_3]

### 7. Update the proposer prompt

Modify the proposer instructions so the coding agent explicitly checks InfraNodus artifacts during diagnosis. For example:[^6_3][^6_1]

- Read `analysis/infranodus/failures.graph.json` before scanning raw traces.[^6_1]
- Read `analysis/infranodus/*.gap_questions.md` to identify missing conceptual bridges.[^6_4]
- Use graph deltas to avoid edits that merely move failure concentration from one topic cluster to another.[^6_1]

This makes InfraNodus part of the proposer’s reasoning discipline rather than an optional report.[^6_3]

### 8. Turn graph findings into edit hypotheses

Require the proposer to translate graph findings into explicit hypotheses before editing harness code. Examples:[^6_3][^6_1]

- “Failures cluster around retrieval-policy and environment-bootstrap; modify retrieval ordering and startup checks.”[^6_1]
- “Goal graph shows implementation ignores evaluation reproducibility; add deterministic seed and trace schema enforcement.”[^6_1]
- “Difference graph shows new candidate improved coding accuracy but introduced drift around rollback semantics; strengthen rollback guardrails.”[^6_1]

This step is important because graph analysis is only useful if it becomes an operational hypothesis.[^6_6]

### 9. Evaluate with graph-aware acceptance

After the new harness is evaluated, score it normally on task metrics, then run InfraNodus again on its traces and compare against the previous best. Reject or down-rank candidates that improve scalar metrics but create new critical structural gaps in safety, dependency integrity, or requirements coverage.[^6_6][^6_5][^6_3][^6_1]

This gives you a two-part ratchet:

- metric improvement from Meta-Harness evaluation.[^6_3]
- structural coherence improvement from InfraNodus graph analysis.[^6_1]


### 10. Accumulate longitudinal memory

Keep InfraNodus outputs over time instead of overwriting them. A proposer can then inspect whether the system’s failure discourse is converging, fragmenting, or repeatedly revisiting the same gaps across many iterations, which is exactly the kind of long-horizon diagnostic context Meta-Harness is designed to exploit.[^6_2][^6_3][^6_1]

## Recommended file layout

A practical directory layout would be:

```text
meta_harness_workspace/
  candidates/
    candidate_001/
    candidate_002/
  evaluations/
    candidate_001/
      scores.json
      traces/
      summaries/
    candidate_002/
      scores.json
      traces/
      summaries/
  analysis/
    infranodus/
      failures.graph.json
      successes.graph.json
      goals.graph.json
      failures.gap_questions.md
      goals.gap_questions.md
      baseline_vs_best.diff.json
      baseline_vs_best.advice.md
      history/
        iter_001/
        iter_002/
  proposer/
    proposal_brief.md
    proposer_instructions.md
```

This layout preserves the Meta-Harness principle that all useful history lives in the filesystem and can be selectively inspected with ordinary tools.[^6_3]

## Endpoint mapping

Here is the simplest mapping from proposer need to InfraNodus endpoint:


| Proposer need | InfraNodus endpoint | Why |
| :-- | :-- | :-- |
| Summarize failures as structure | `graphAndStatements` [^6_1] | Produces graph, stats, and summaries from trace corpora.[^6_1] |
| Generate missing-bridge questions | `graphAndAdvice` with `optimize=gaps` and `requestMode=question` [^6_1][^6_4] | Produces bridge questions from structural gaps.[^6_4] |
| Compare baseline and current-best | `compareGraphs` [^6_1] | Shows structural difference between corpora.[^6_1] |
| Compare and ask what changed | `graphsAndAiAdvice` with `compareMode=difference` [^6_1] | Produces advice over the difference graph.[^6_1] |
| Improve RAG context for proposer | `graphAndAdvice` or GraphRAG flow [^6_8][^6_9] | Uses graph summaries and key clusters to improve prompt context.[^6_8] |

## Proposer policy changes

To make this effective, change proposer policy in three ways:

- **Graph-first triage**: start with InfraNodus summaries before drilling into raw traces, so the proposer forms better hypotheses faster.[^6_2][^6_1]
- **Gap-to-edit discipline**: every proposed edit should cite at least one graph-derived gap, cluster, or difference finding.[^6_1]
- **Structural guardrails**: never accept an edit that introduces new unresolved gaps in critical domains even if benchmark score rises.[^6_5][^6_6]

That prevents local optimization against a narrow metric and helps the proposer operate at the level of discourse structure, not just line-by-line debugging.[^6_6][^6_3]

## Why this improves Meta-Harness

Meta-Harness gains power from selective access to raw prior code and execution traces through the filesystem, enabling counterfactual diagnosis and targeted edits. InfraNodus improves that diagnosis stage by compressing sprawling text into graph structure, highlighting the concepts that dominate, the clusters that remain disconnected, and the questions that would bridge them.[^6_2][^6_4][^6_3][^6_1]

So the proposer becomes stronger in three ways:

- It identifies failure themes faster.[^6_1]
- It proposes edits based on missing conceptual bridges, not just surface symptoms.[^6_5][^6_4]
- It can reason about requirements, traces, and benchmark narratives in one unified structural language.[^6_8][^6_1]


## Practical first version

For a first implementation, I would keep it simple:

- Analyze only failures, goals, and baseline-vs-best diff.[^6_1]
- Generate only one `proposal_brief.md` per iteration.[^6_3][^6_1]
- Use only two gating signals from InfraNodus: critical gap emergence and failure-cluster concentration.[^6_5][^6_4]
- Let the proposer reference graph outputs, but keep final acceptance still mostly benchmark-driven until you have enough history to calibrate graph-aware thresholds.[^6_3]

That gives you a low-friction integration that is still faithful to both systems.[^6_3][^6_1]

Would you like the next step to be a concrete proposer pseudocode file or a real Python module skeleton for this integration?
<span style="display:none">[^6_10][^6_11][^6_12][^6_13][^6_14][^6_15][^6_16]</span>

<div align="center">⁂</div>

[^6_1]: https://infranodus.com/api/docs

[^6_2]: https://yoonholee.com/meta-harness/

[^6_3]: https://arxiv.org/html/2603.28052v1

[^6_4]: https://support.noduslabs.com/hc/en-us/articles/13605983537692-InfraNodus-API-Access-Points

[^6_5]: https://infranodus.com/docs/content-gap-analysis

[^6_6]: https://infranodus.com/about/how-it-works

[^6_7]: https://support.noduslabs.com/hc/en-us/articles/18819595426460-Using-InfraNodus-API-to-Generate-Questions-for-Any-Text

[^6_8]: https://infranodus.com/use-case/ai-knowledge-graphs

[^6_9]: https://infranodus.com/docs/graph-rag-knowledge-graph

[^6_10]: https://dify.ai/blog/level-up-your-dify-chatbot-integrating-infranodus-for-advanced-q-a-and-idea-generation

[^6_11]: https://www.facebook.com/groups/techtitansgroup/posts/1628541431806502/

[^6_12]: https://infranodus.com/docs

[^6_13]: https://infranodus.com/docs/network-analysis

[^6_14]: https://infranodus.com/api

[^6_15]: https://infranodus.com

[^6_16]: https://scienovice.com/articles/meta-harness-automated-code-optimization


---

# Common pitfalls in InfraNodus graph integration

The main pitfalls are over-trusting the graph, feeding it low-quality corpora, and turning gap signals into automatic edits without enough benchmark discipline. InfraNodus is powerful because it surfaces structural gaps, topic clusters, and bias in discourse graphs, but Meta-Harness can still overfit in code space, so graph outputs should guide diagnosis and test creation rather than act as unquestioned truth.[^7_1][^7_2][^7_3][^7_4]

## Input pitfalls

A common mistake is sending InfraNodus a noisy, mixed corpus where failures, successes, requirements, and random logs are all blended together. Because InfraNodus builds graphs from statements and co-occurring lemmas or concepts, poor corpus segmentation can create misleading clusters and fake bridges that reflect formatting or logging style more than actual system behavior.[^7_3][^7_5][^7_6]

Another pitfall is using text that is too raw, too repetitive, or too thin. If traces are dominated by boilerplate stack traces, duplicated prompt headers, or repeated tool wrappers, the graph can overemphasize procedural tokens instead of the meaningful semantic issues you want the proposer to learn from.[^7_7][^7_2][^7_1]

## Interpretation pitfalls

The biggest interpretation error is to treat a structural gap as automatically meaning “this is missing and should be connected.” InfraNodus defines gaps as distant topical clusters that could be connected, but in a harness workflow some separations are healthy, such as isolating security controls from speculative ideation or keeping rollback logic separate from exploratory planning.[^7_7][^7_3]

A related mistake is confusing centrality with importance. A concept can become central because it appears in many repetitive failure notes, not because it is the best leverage point for the next harness edit, so graph metrics should be combined with benchmark results, error severity, and domain judgment.[^7_2][^7_4][^7_1]

## Optimization pitfalls

One dangerous pattern is making the proposer optimize directly for better-looking graphs rather than better task outcomes. Since Meta-Harness works by iteratively editing harness code and evaluating candidates, the graph should be an auxiliary diagnostic layer; otherwise you risk producing discourse that appears more connected while actual benchmark performance stagnates or regresses.[^7_8][^7_4][^7_9]

Another pitfall is building brittle policies from graph findings, such as hard-coded prompt branches for the current dominant clusters. The Meta-Harness paper explicitly warns that code-space overfitting can show up as brittle if-chains or hard-coded mappings, and graph-derived heuristics can accidentally encourage exactly that if they are not kept general and re-tested on held-out tasks.[^7_4]

## QA pitfalls

A frequent QA mistake is using gap detection only after failures instead of also on goals, benchmarks, and retrieval corpora. InfraNodus is also useful for evaluating knowledge-base completeness and identifying blind spots before failure happens, so limiting it to postmortems leaves value on the table.[^7_10][^7_3][^7_8]

Another pitfall is not calibrating thresholds. Metrics like diversity, cluster separation, or concentration can be informative, but without project-specific baselines they can produce noisy or misleading accept/reject signals, especially across very different repositories or tasks.[^7_2][^7_10]

## Workflow pitfalls

Teams often make InfraNodus an optional side dashboard instead of integrating it into the actual proposer and evaluator workflow. If the graph outputs are not persisted on disk alongside candidate scores, traces, and validation artifacts, then the Meta-Harness proposer cannot reliably use them as part of its diagnostic memory.[^7_9][^7_11]

Another workflow issue is overwriting graph history instead of keeping longitudinal snapshots. Since the harness outer loop depends on comparing prior candidates and understanding whether improvements are durable, you want graph artifacts versioned by iteration so you can see whether failure structure is genuinely shrinking or just moving around.[^7_6][^7_9]

## Retrieval pitfalls

If you use InfraNodus for GraphRAG, a common mistake is assuming graph-derived context is always better than simpler retrieval. The docs position it as a way to improve prompt relevance and capture complex relations, but it still depends on the quality and coverage of the underlying corpus, so poor source material can yield confident but incomplete retrieval guidance.[^7_8][^7_10]

Another mistake is over-diversifying retrieval because the graph says a corpus is biased. Some tasks need narrow, high-precision context, so forcing broader coverage can dilute the prompt and reduce execution quality rather than improve it.[^7_2][^7_8]

## Good guardrails

The safest way to avoid these pitfalls is:

- Separate corpora by purpose: failures, successes, goals, dependencies, and benchmarks.[^7_5][^7_6]
- Treat graph outputs as hypotheses, not facts.[^7_1][^7_3]
- Use graph findings to generate new questions, tests, and retrieval hints, not direct unchecked edits.[^7_12][^7_13]
- Keep benchmark-driven acceptance as the primary ratchet.[^7_4]
- Persist graph artifacts per iteration so structural change can be compared over time.[^7_9][^7_6]

That approach lets InfraNodus strengthen Meta-Harness without turning the graph layer into a new source of overfitting.[^7_4][^7_2]
<span style="display:none">[^7_14][^7_15][^7_16][^7_17][^7_18]</span>

<div align="center">⁂</div>

[^7_1]: https://infranodus.com/docs/text-network-analysis

[^7_2]: https://infranodus.com/use-case/text-mining

[^7_3]: https://infranodus.com/about/how-it-works

[^7_4]: https://arxiv.org/html/2603.28052v1

[^7_5]: https://support.noduslabs.com/hc/en-us/articles/8825622679580-Tutorial-Qualitative-Research-using-Text-Network-Thematic-Analysis

[^7_6]: https://infranodus.com/api/docs

[^7_7]: https://infranodus.com/use-case/text-network-analysis

[^7_8]: https://infranodus.com/use-case/ai-knowledge-graphs

[^7_9]: https://shashikantjagtap.net/meta-harness-a-self-optimizing-harness-around-coding-agents/

[^7_10]: https://infranodus.com/docs/graph-rag-knowledge-graph

[^7_11]: https://infranodus.com/api

[^7_12]: https://support.noduslabs.com/hc/en-us/articles/13605983537692-InfraNodus-API-Access-Points

[^7_13]: https://infranodus.com/docs/content-gap-analysis

[^7_14]: https://infranodus.com

[^7_15]: https://www.linkedin.com/pulse/code-around-model-matters-more-than-you-think-automating-binod-kumar-w5wlc

[^7_16]: https://infranodus.com/use-case/marketing-research

[^7_17]: https://infranodus.com/docs/knowledge-graphs-for-llms

[^7_18]: https://ryuchen.github.io/essay/0x00000C.files/1-WWW- InfraNodus- Generating Insight Using Text Network Analysis.pdf


---

# please help me create a structured task list that can help me avoid errors and assure that the content given to infranodus is of the highest quality and necessary:

Best practices to avoid InfraNodus integration failures
How to debug structural gaps in InfraNodus graphs
InfraNodus API error handling in GraphRAG
Compare InfraNodus with other GraphRAG tools
Example Meta-Harness config optimized for InfraNodus

Yes — the safest way to avoid InfraNodus failures is to turn it into a **gated content-prep workflow** before anything reaches the API or the Meta-Harness proposer. Below is a structured task list that covers content quality, debugging, API handling, GraphRAG tool comparison, and a starter Meta-Harness config pattern tuned for InfraNodus.[^8_1][^8_2][^8_3][^8_4][^8_5]

## Task list

Use this as an operational checklist for every corpus you send to InfraNodus.

### 1. Corpus intake

- Identify the corpus purpose first: failures, successes, goals, dependencies, benchmarks, or retrieval knowledge base.[^8_2][^8_3]
- Reject mixed-purpose corpora; never blend incident logs, requirements text, and successful run notes into one default graph.[^8_6][^8_7]
- Record provenance for each document: source, timestamp, repo, subsystem, run ID, and whether it is raw or human-curated.[^8_4][^8_2]


### 2. Content cleaning

- Remove duplicate blocks, repeated prompt boilerplate, stack-trace spam, and long low-signal headers before graphing.[^8_8][^8_9]
- Normalize terminology, such as choosing one canonical term for the same subsystem or agent role, so graphs are not split by naming drift.[^8_6][^8_8]
- Keep semantically meaningful text, but strip secrets, irrelevant environment noise, and machine-generated repetition.[^8_2][^8_4]


### 3. Corpus shaping

- Split corpora into coherent text bundles, such as `corpus_failures.txt`, `corpus_goals.txt`, and `corpus_dependencies.txt`.[^8_2]
- Keep each corpus small enough to stay topically coherent; use multiple targeted runs rather than one giant graph dump.[^8_1][^8_6]
- Add short human summaries to very raw logs so the graph has meaningful semantic anchors, not only procedural noise.[^8_7][^8_8]


### 4. Preflight QA

- Check that each corpus answers one clear question, for example: “Why did candidates fail?” or “What goals are underrepresented?”[^8_10][^8_6]
- Verify that each corpus has enough semantic variety to form a graph, but not so much unrelated content that clusters become meaningless.[^8_11][^8_8]
- Run a simple lint pass: non-empty, no massive duplicates, no unresolved binary junk, no broken encoding, no secrets.[^8_2]


### 5. InfraNodus graphing

- First call `graphAndStatements` with `doNotSave=true`, `addStats=true`, and `extendedGraphSummary=true` for every new corpus.[^8_2]
- Save outputs as versioned artifacts rather than overwriting them, so you can compare iteration-to-iteration graph changes.[^8_4][^8_2]
- Review graph summaries before using them downstream in proposer prompts or retrieval logic.[^8_6][^8_2]


### 6. Gap debugging

- Use `graphAndAdvice` with `optimize=gaps` and `requestMode=question` to inspect missing conceptual bridges.[^8_2]
- Confirm that detected gaps are meaningful for the workflow and not simply desirable separations, such as security isolation or unrelated subsystems.[^8_11][^8_6]
- Compare suspicious graphs against a more curated corpus slice to see whether the “gap” was caused by noise, over-broad input, or poor segmentation.[^8_7][^8_8]


### 7. Candidate comparison

- Use `compareGraphs` or `graphsAndAiAdvice` with `compareMode=difference` to compare baseline vs best candidate or goals vs implementation.[^8_2]
- Reject the interpretation that “difference” automatically means “improvement”; use benchmark and QA evidence to validate it.[^8_5][^8_2]
- Track graph deltas over time to see whether failure structure is shrinking or merely moving.[^8_4][^8_2]


### 8. Harness integration

- Expose graph summaries, gap questions, and graph diffs to the proposer as files in the same workspace as traces and scores.[^8_4][^8_2]
- Require each proposed harness change to reference a graph-derived hypothesis plus a benchmark-oriented rationale.[^8_5][^8_2]
- Keep benchmark-driven acceptance as the primary ratchet, with graph findings as diagnostic and guardrail signals.[^8_1][^8_5]


### 9. Retrieval integration

- Use InfraNodus GraphRAG only where relational context and missing-topic detection matter more than pure similarity retrieval.[^8_3][^8_1]
- For narrow precision tasks, test InfraNodus against plain RAG because broader relational retrieval can dilute useful context.[^8_3][^8_1]
- Keep a fallback retrieval path when graph-based context is low-confidence or graph generation fails.[^8_1][^8_2]


### 10. Operational review

- Audit graphs periodically for terminology drift, over-dominant nodes, and low-signal clusters.[^8_9][^8_8]
- Create regression tests from meaningful gaps that led to real incidents or bad harness decisions.[^8_10][^8_5]
- Maintain a living playbook of “known bad corpus patterns” so your team stops repeating ingestion mistakes.[^8_8][^8_7]


## Best practices

These are the highest-value practices to prevent InfraNodus integration failures:

- Keep one corpus, one question, one graph objective.[^8_6]
- Prefer curated semantic summaries plus raw evidence, not raw evidence alone.[^8_7][^8_8]
- Treat graph outputs as hypotheses to test, not truths to automate blindly.[^8_5][^8_6]
- Version every graph artifact by run, candidate, and corpus type.[^8_4][^8_2]
- Pair graph QA with standard task QA, not instead of it.[^8_5][^8_1]


## Debugging structural gaps

When a gap looks wrong or confusing, debug it in this order:

1. **Check corpus purity**: was unrelated content mixed together?[^8_7][^8_6]
2. **Check terminology drift**: are two concepts really the same thing with different names?[^8_8]
3. **Check repetition bias**: did boilerplate or repeated error text dominate the graph?[^8_9]
4. **Check segmentation**: should the corpus have been split by subsystem, run phase, or goal area?[^8_10][^8_6]
5. **Check whether the gap is actually desirable**: some conceptual separation is intentional and healthy.[^8_11][^8_6]
6. **Compare against a curated subset**: if the gap disappears, the original graph was probably noisy.[^8_8][^8_7]

A good rule is: never let one surprising gap directly change the harness until it survives a second pass on a cleaner corpus.[^8_5][^8_6]

## API handling

InfraNodus exposes REST endpoints for graph generation, advice, graph comparison, and GraphRAG use cases, so your integration should wrap those endpoints with defensive handling. For GraphRAG workflows especially, add retries, timeout control, payload-size checks, auth validation, and safe fallback behavior when graph requests fail or return incomplete output.[^8_12][^8_1][^8_2]

Practical error-handling tasks:

- Validate the API token and endpoint reachability before batch processing.[^8_2]
- Fail fast on malformed payloads and log the exact corpus ID and endpoint used.[^8_2]
- Store raw request and response metadata for debugging, but redact secrets.[^8_2]
- Use fallback modes: plain RAG, cached graph artifacts, or proposer-without-graph mode when InfraNodus is unavailable.[^8_1][^8_4]
- Add per-endpoint health checks in CI for `graphAndStatements`, `graphAndAdvice`, and `compareGraphs`.[^8_2]


## Tool comparison

InfraNodus is strongest when you want a plug-and-play GraphRAG API, interactive graph observability, gap detection, and easy integration without standing up your own graph database. Its own documentation highlights ease of use, interactive graphs, and built-in content gap detection, while also noting constraints such as subscription requirements, knowledge-base size limitations, and lack of local Ollama GraphRAG support at the time described.[^8_13][^8_3][^8_1]

A practical comparison is:


| Tool style | Strengths | Weaknesses | Best fit |
| :-- | :-- | :-- | :-- |
| InfraNodus | Fast setup, interactive graph, gap detection, API-driven GraphRAG.[^8_3][^8_1] | Subscription, possible KB size limits, less local/self-hosted flexibility.[^8_1] | Research, requirements, diagnostics, human-in-the-loop graph QA.[^8_13] |
| Plain vector RAG | Simple, cheap, mature, strong for local passage similarity.[^8_3] | Weak relational/contextual reasoning across concepts.[^8_3][^8_13] | Narrow retrieval and factual lookup.[^8_3] |
| Self-built graph RAG stack | Flexible, local, customizable ontology and storage model.[^8_14] | More engineering overhead, harder observability, more pipeline maintenance.[^8_14][^8_13] | Large custom platforms with strong internal graph expertise.[^8_14] |

For your use case, InfraNodus looks strongest as a **structural analysis layer** on top of Meta-Harness rather than as the only retrieval system.[^8_1][^8_4]

## Starter config

Below is a compact example Meta-Harness-style config pattern optimized for InfraNodus-assisted proposing and evaluation.[^8_4][^8_2]

```yaml
meta_harness:
  workspace_root: ./meta_harness_workspace
  baseline_candidate: terminus_kira
  proposer:
    read_paths:
      - evaluations/current_best/scores.json
      - evaluations/current_best/traces/
      - analysis/infranodus/failures.graph.json
      - analysis/infranodus/goals.graph.json
      - analysis/infranodus/failures.gap_questions.md
      - analysis/infranodus/baseline_vs_best.diff.json
      - proposer/proposal_brief.md
    policy:
      require_graph_hypothesis: true
      require_benchmark_rationale: true
      forbid_direct_graph_only_edits: true

  infranodus:
    enabled: true
    base_url: https://infranodus.com/api/v1
    endpoints:
      graph: graphAndStatements
      advice: graphAndAdvice
      compare: compareGraphs
    params:
      doNotSave: true
      addStats: true
      extendedGraphSummary: true
    corpora:
      failures: evaluations/current_best/traces/failures/
      goals: goals/
      dependencies: architecture/dependencies/
    advice:
      optimize: gaps
      requestMode: question
    fallbacks:
      on_api_failure: proposer_without_graph
      on_low_confidence_graph: plain_rag_only

  evaluator:
    primary_metric: benchmark_score
    guardrails:
      - no_critical_regressions
      - no_security_gap_emergence
      - no_dependency_integrity_gap_emergence
    graph_signals:
      use_for_diagnostics: true
      use_for_acceptance: true
      acceptance_mode: guardrail_only

  artifacts:
    save_versioned_graphs: true
    proposal_brief: proposer/proposal_brief.md
    graph_dir: analysis/infranodus/history/
```

This matches the Meta-Harness pattern of filesystem-readable diagnostics while inserting InfraNodus outputs as structured artifacts the proposer can inspect before editing the harness.[^8_4][^8_2]

## Recommended sequence

Start with this rollout order:

1. Corpus linting and segmentation.[^8_7][^8_8]
2. Versioned `graphAndStatements` runs on failures and goals.[^8_2]
3. Gap debugging workflow with `graphAndAdvice`.[^8_10][^8_2]
4. Baseline-vs-best comparison with `compareGraphs`.[^8_2]
5. Proposer briefing integration.[^8_4][^8_2]
6. Acceptance guardrails using only critical graph regressions at first.[^8_5][^8_1]

That sequence keeps the integration safe, observable, and less likely to create graph-induced overfitting.[^8_6][^8_5]

Would you like me to convert this into a reusable checklist document and a machine-readable YAML task plan?
<span style="display:none">[^8_15][^8_16][^8_17][^8_18][^8_19][^8_20][^8_21]</span>

<div align="center">⁂</div>

[^8_1]: https://infranodus.com/docs/graph-rag-knowledge-graph

[^8_2]: https://infranodus.com/api/docs

[^8_3]: https://infranodus.com/use-case/ai-knowledge-graphs

[^8_4]: https://yoonholee.com/meta-harness/

[^8_5]: https://arxiv.org/html/2603.28052v1

[^8_6]: https://infranodus.com/about/how-it-works

[^8_7]: https://support.noduslabs.com/hc/en-us/articles/8825622679580-Tutorial-Qualitative-Research-using-Text-Network-Thematic-Analysis

[^8_8]: https://infranodus.com/docs/text-network-analysis

[^8_9]: https://infranodus.com/use-case/text-mining

[^8_10]: https://infranodus.com/docs/content-gap-analysis

[^8_11]: https://infranodus.com/use-case/text-network-analysis

[^8_12]: https://infranodus.com/api

[^8_13]: https://support.noduslabs.com/hc/en-us/articles/19226701201436-Portable-GraphRAG-Supercharge-Your-AI-Thinking-with-Knowledge-Graphs

[^8_14]: https://infranodus.com/docs/knowledge-graphs-for-llms

[^8_15]: https://arxiviq.substack.com/p/meta-harness-end-to-end-optimization

[^8_16]: https://github.com/infiniflow/ragflow/issues/9108

[^8_17]: https://www.reddit.com/r/n8n/comments/1ks4y1d/a_panel_of_ai_experts_that_use_knowledge_graphs/

[^8_18]: https://dify.ai/blog/connecting-infranodus-graphrag-as-an-external-knowledge-base-in-dify

[^8_19]: https://www.reddit.com/r/Rag/comments/1ftgvv4/would_you_always_recommend_knowledge_graph_rag/

[^8_20]: https://infranodus.com/use-case/mcp-server

[^8_21]: https://www.youtube.com/playlist?list=PLZhDuTZwzpWcgWKn2ZKQPPvuFU4hepQc9


---

# The InfraNodus input checklist that catches 90% of graph failures before they

happen

Template for content preprocessing checklist before InfraNodus API call

How to validate InfraNodus graph quality using network stats

Integrating content quality checks into Meta-Harness workflow

Examples of bad vs good text inputs for InfraNodus graphs

Yes — the right move is to use a **pre-API input gate** so bad corpora never reach InfraNodus or your Meta-Harness proposer in the first place. Below is a practical checklist, a preprocessing template, graph-quality validation rules based on InfraNodus network stats, workflow integration guidance, and concrete bad-vs-good input examples.[^9_1][^9_2][^9_3][^9_4][^9_5]

## Input checklist

This checklist should catch most graph failures before they happen.[^9_2][^9_1]

### 1. Define purpose

- State the corpus purpose in one sentence, such as “analyze failure modes in candidate_017 traces.”[^9_2]
- Choose exactly one analysis target: failures, successes, goals, dependencies, benchmarks, or retrieval corpus.[^9_4][^9_5]
- Reject the corpus if it mixes unrelated purposes.[^9_5][^9_6]


### 2. Validate source quality

- Confirm every file has provenance: source, date, subsystem, run ID, and owner.[^9_3][^9_2]
- Remove empty files, near-duplicates, binary junk, and unresolved encoding issues.[^9_2]
- Reject corpora dominated by boilerplate, repeated prompts, or stack-trace spam.[^9_7][^9_1]


### 3. Normalize language

- Canonicalize names for the same component, agent, subsystem, and benchmark.[^9_1][^9_5]
- Expand ambiguous abbreviations where possible so graph nodes reflect meaning, not shorthand noise.[^9_1]
- Strip low-signal headers, repetitive system text, and machine scaffolding that does not describe the underlying issue.[^9_7]


### 4. Shape the corpus

- Keep one corpus focused on one question.[^9_5]
- Prefer multiple targeted corpora over one massive mixed corpus.[^9_8][^9_2]
- Add short human summaries to raw logs so meaningful concepts co-occur in text, not just procedural tokens.[^9_6][^9_1]


### 5. Preflight pass

- Ask: “Would a human reading this corpus understand the main concepts without the original system?”[^9_1]
- Ask: “Will the dominant words represent real topics rather than repeated runtime syntax?”[^9_7]
- Reject the corpus if the answer to either question is no.[^9_7][^9_1]


### 6. InfraNodus-ready packaging

- Use `graphAndStatements` first with `doNotSave=true`, `addStats=true`, and `extendedGraphSummary=true`.[^9_4][^9_2]
- Save versioned artifacts per run and corpus type.[^9_2]
- Review `mainTopics`, `mainConcepts`, `contentGaps`, `conceptualGateways`, and `diversityStatistics` before using outputs in prompts.[^9_2]


## Preprocessing template

Use this as a content preprocessing checklist before every InfraNodus API call.

```md
# InfraNodus Preprocessing Checklist

## Corpus identity
- Corpus ID:
- Purpose:
- Owner:
- Date:
- Source files:
- Run / candidate ID:
- Subsystem:

## Scope check
- [ ] One primary question only
- [ ] One corpus type only: failures / successes / goals / dependencies / benchmarks / retrieval
- [ ] No unrelated documents mixed in

## Quality check
- [ ] No empty files
- [ ] No duplicate or near-duplicate files
- [ ] No binary junk / encoding issues
- [ ] No secrets or credentials
- [ ] No excessive boilerplate or copied prompt wrappers
- [ ] No long stack traces without summarization

## Semantic check
- [ ] Canonical names normalized
- [ ] Ambiguous abbreviations expanded
- [ ] Raw logs accompanied by short summaries where needed
- [ ] Repeated low-signal tokens removed
- [ ] Text still preserves the original issue meaning

## Packaging check
- [ ] Corpus split correctly by purpose
- [ ] File names include source + date + subsystem
- [ ] Corpus size is reasonable for one coherent graph
- [ ] Version tag assigned

## API settings
- Endpoint: graphAndStatements / graphAndAdvice / compareGraphs
- [ ] doNotSave=true
- [ ] addStats=true
- [ ] extendedGraphSummary=true
- [ ] includeStatements set appropriately
- [ ] compareMode set appropriately if comparing corpora

## Approval
- Reviewed by:
- Ready for API call: Yes / No
- Notes:
```

This template matches InfraNodus’s API model, where graph summaries and structured analytics are first-class outputs, and also fits the Meta-Harness style of versioned filesystem artifacts used by the proposer.[^9_3][^9_2]

## Graph quality validation

You can validate InfraNodus graph quality using the network and summary signals it exposes, especially modular topical clusters, betweenness-centrality-based importance, content gaps, conceptual gateways, and diversity statistics.[^9_1][^9_2]

Use these validation rules:

- **Topic coherence**: `mainTopics` should reflect real concepts in the corpus, not repeated runtime scaffolding or template headers.[^9_1][^9_2]
- **Concept usefulness**: top concepts should point to meaningful failure themes, goals, or dependencies, not generic words created by noisy preprocessing.[^9_7][^9_2]
- **Gap plausibility**: `contentGaps` should suggest meaningful missing bridges; if they seem absurd, the corpus is probably mixed or noisy.[^9_5][^9_2]
- **Gateway relevance**: `conceptualGateways` should look like legitimate cross-cutting connectors between clusters, not artifacts of logging syntax.[^9_2]
- **Diversity sanity**: diversity statistics should align with the corpus type, where a focused failure corpus can be narrower than a goals corpus, but neither should collapse into one repetitive procedural cluster unless that is truly the content.[^9_7][^9_2]
- **Centrality sanity**: high-centrality nodes should be interpretable as bridge concepts rather than repeated boilerplate or system wrappers.[^9_9][^9_1]

A simple validation rubric:


| Check | Healthy signal | Warning sign |
| :-- | :-- | :-- |
| Topics | Real domain clusters.[^9_2] | Dominated by prompt scaffolding or log syntax.[^9_7] |
| Central nodes | Meaningful bridge concepts.[^9_1] | Repeated headers, wrapper names, or generic runtime words.[^9_7] |
| Gaps | Useful bridge questions.[^9_5] | Random or obviously irrelevant connections.[^9_5][^9_6] |
| Diversity | Matches intended corpus breadth.[^9_7] | Extreme narrowness from repetition or chaos from mixed corpora.[^9_7][^9_6] |
| Gateways | Connect actual subsystems or themes.[^9_2] | Connect artifacts of formatting rather than semantics.[^9_1] |

## Workflow integration

The cleanest Meta-Harness integration is to insert content-quality checks **before** every InfraNodus analysis artifact is created, then store both the cleaned corpus and validation result in the same filesystem workspace the proposer already reads.[^9_10][^9_3][^9_2]

A strong workflow is:

1. Gather raw traces, summaries, goals, or dependency docs into a candidate corpus.[^9_3]
2. Run the preprocessing checklist and reject bad corpora before any API call.[^9_2]
3. Save a `corpus_manifest.json` describing provenance, normalization, and lint status.[^9_3][^9_2]
4. Run `graphAndStatements` to generate graph artifacts only for approved corpora.[^9_2]
5. Save graph-quality validation results next to the graph artifact.[^9_2]
6. Expose only approved graph artifacts to the proposer in `analysis/infranodus/`.[^9_3]
7. Use `graphAndAdvice` and `compareGraphs` only after the base graph passes quality checks.[^9_2]

That way the proposer sees graph artifacts that are already filtered for quality, which reduces the chance of optimizing around noisy or misleading graph structure.[^9_10][^9_1]

## Bad vs good inputs

Here are practical examples.

### Bad input: mixed noisy log dump

```text
INFO starting run
INFO starting run
SYSTEM PROMPT LOADED
tool_call bash
tool_call bash
ERROR file not found
Traceback line 1...
Traceback line 2...
Traceback line 3...
candidate score 0.42
retrying...
retrying...
retrying...
```

This is bad because it is dominated by repeated runtime scaffolding, procedural noise, and unsummarized traces, so central nodes and clusters are likely to reflect logging artifacts rather than meaningful concepts.[^9_1][^9_7]

### Good input: failure summary corpus

```text
Candidate 017 failed to update the dependency map after schema changes.
The harness retrieved migration notes but ignored rollback constraints.
Two failures involved missing links between dependency integrity checks and release gating.
The evaluator reported regressions in reproducibility because seed handling changed during bootstrap.
Suggested focus: retrieval ordering, rollback policy enforcement, deterministic environment setup.
```

This is good because it preserves the semantic content of the failure, creates meaningful co-occurrences between real concepts, and gives InfraNodus a structure that can reveal clusters, gaps, and bridge concepts.[^9_5][^9_1]

### Bad input: mixed goals and incidents

```text
We want better onboarding for agents.
Yesterday the Docker daemon crashed.
The roadmap includes graph QA.
Customer wants less latency.
A branch merge failed because of permissions.
```

This is bad because it mixes strategic goals, infrastructure incidents, and product requirements into one shallow graph, which can create misleading gaps and incoherent clusters.[^9_6][^9_5]

### Good input: normalized goal corpus

```text
Goal: improve agent onboarding by reducing setup ambiguity.
Goal: reduce evaluation latency in harness runs.
Goal: strengthen graph QA before proposer iterations.
Constraint: maintain deterministic bootstrap and permission-safe workflows.
Dependency risk: permission handling affects branch merge reliability and evaluator automation.
```

This is better because the corpus has one planning purpose, normalized language, and clearly stated relationships between goals and constraints.[^9_5][^9_2]

## Practical acceptance rule

A corpus should be blocked from InfraNodus if any of these are true:

- mixed purpose,[^9_5]
- dominated by repetitive low-signal text,[^9_7]
- terminology drift not normalized,[^9_1]
- no provenance,[^9_3]
- graph-quality preview shows nonsensical topics or gaps.[^9_5][^9_2]

That simple gate will prevent most downstream graph problems before they affect Meta-Harness optimization.[^9_3][^9_2]

If you want, I can turn this into two concrete artifacts next: a reusable `infranodus_input_checklist.md` and a `corpus_quality_gate.yaml` for your workflow.
<span style="display:none">[^9_11][^9_12][^9_13][^9_14][^9_15][^9_16][^9_17]</span>

<div align="center">⁂</div>

[^9_1]: https://infranodus.com/docs/text-network-analysis

[^9_2]: https://infranodus.com/api/docs

[^9_3]: https://yoonholee.com/meta-harness/

[^9_4]: https://support.noduslabs.com/hc/en-us/articles/13605983537692-InfraNodus-API-Access-Points

[^9_5]: https://infranodus.com/about/how-it-works

[^9_6]: https://support.noduslabs.com/hc/en-us/articles/8825622679580-Tutorial-Qualitative-Research-using-Text-Network-Thematic-Analysis

[^9_7]: https://infranodus.com/use-case/text-mining

[^9_8]: https://infranodus.com/docs/graph-rag-knowledge-graph

[^9_9]: https://infranodus.com/use-case/text-network-analysis

[^9_10]: https://arxiv.org/html/2603.28052v1

[^9_11]: https://infranodus.com/docs/network-analysis

[^9_12]: https://dl.acm.org/doi/10.1145/3308558.3314123

[^9_13]: https://ryuchen.github.io/essay/0x00000C.files/1-WWW- InfraNodus- Generating Insight Using Text Network Analysis.pdf

[^9_14]: https://infranodus.com/api

[^9_15]: https://github.com/ai-boost/awesome-harness-engineering

[^9_16]: https://infranodus.com/docs/voyant-visualization-tools

[^9_17]: https://infranodus.com/docs/faq


---

# • Example InfraNodus preprocessing script for Meta-Harness

• How to interpret extendedGraphSummary metrics

• Automating graph quality checks in Meta-Harness pipeline

• Fixing low modularity or betweenness issues

• Thresholds for good InfraNodus graph diversity

A good implementation is to treat InfraNodus as a **preprocessed, scored analysis stage** inside Meta-Harness: clean and normalize the corpus, call `graphAndStatements` with stats and extended summary, validate the graph, then expose only approved graph artifacts to the proposer. The important caution is that InfraNodus gives useful structural signals like topical communities, betweenness-ranked bridge concepts, content gaps, conceptual gateways, and diversity statistics, but its docs do not publish universal numeric thresholds for “good” graphs, so any thresholds you use should be treated as project heuristics calibrated against your own corpora.[^10_1][^10_2][^10_3][^10_4]

## Preprocessing script

Here is a practical Python example for Meta-Harness that cleans text inputs, builds a corpus, calls InfraNodus, and runs simple graph-quality checks before the proposer reads the result.[^10_3][^10_1]

```python
import os
import re
import json
import hashlib
from pathlib import Path
import requests

API_TOKEN = os.environ["INFRANODUS_API_TOKEN"]
BASE_URL = "https://infranodus.com/api/v1"
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json",
}

WORKSPACE = Path("meta_harness_workspace")
RAW_DIR = WORKSPACE / "evaluations" / "current_best" / "traces"
OUT_DIR = WORKSPACE / "analysis" / "infranodus"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CANONICAL_TERMS = {
    r"\bmh\b": "meta harness",
    r"\bgraphrag\b": "graph rag",
    r"\bdep map\b": "dependency map",
    r"\bbootstrapping\b": "bootstrap",
}

NOISE_PATTERNS = [
    r"^INFO\b.*$",
    r"^DEBUG\b.*$",
    r"^TRACE\b.*$",
    r"^SYSTEM PROMPT LOADED.*$",
    r"^tool_call\s+\w+.*$",
    r"^retrying\.*$",
    r"^Traceback \(most recent call last\):.*$",
    r"^\s*File \".*\", line \d+.*$",
]

def sha1(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()

def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n")
    lines = text.splitlines()

    cleaned = []
    for line in lines:
        if any(re.match(p, line) for p in NOISE_PATTERNS):
            continue
        line = re.sub(r"\s+", " ", line).strip()
        if not line:
            continue
        cleaned.append(line)

    text = "\n".join(cleaned).lower()

    for pattern, replacement in CANONICAL_TERMS.items():
        text = re.sub(pattern, replacement, text)

    return text.strip()

def summarize_raw_log(text: str, file_name: str) -> str:
    text = normalize_text(text)
    snippets = text.split("\n")[:12]
    summary = "\n".join(snippets)
    return f"# source: {file_name}\n{summary}"

def build_corpus(raw_dir: Path):
    docs = []
    seen = set()

    for path in sorted(raw_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".txt", ".md", ".log", ".json"}:
            continue

        raw = path.read_text(encoding="utf-8", errors="ignore")
        if path.suffix.lower() == ".json":
            try:
                raw = json.dumps(json.loads(raw), indent=2)
            except Exception:
                pass

        doc = summarize_raw_log(raw, path.name)
        h = sha1(doc)
        if h in seen:
            continue
        seen.add(h)

        if len(doc.split()) < 20:
            continue

        docs.append({
            "source": str(path),
            "title": path.name,
            "text": doc,
        })

    return docs

def call_infranodus_graph(text: str):
    url = f"{BASE_URL}/graphAndStatements"
    params = {
        "doNotSave": "true",
        "addStats": "true",
        "extendedGraphSummary": "true",
    }
    payload = {"text": text}
    r = requests.post(url, params=params, headers=HEADERS, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()

def validate_graph(result: dict):
    summary = result.get("extendedGraphSummary", {}) or result.get("graphSummary", {})
    stats = result.get("stats", {}) or {}

    main_topics = summary.get("mainTopics", [])
    main_concepts = summary.get("mainConcepts", [])
    content_gaps = summary.get("contentGaps", [])
    gateways = summary.get("conceptualGateways", [])
    diversity = summary.get("diversityStatistics", stats.get("diversityStatistics", {}))

    issues = []
    warnings = []

    if len(main_topics) < 2:
        warnings.append("Low topical variety: fewer than 2 main topics.")
    if len(main_concepts) < 5:
        warnings.append("Very few main concepts: corpus may be too thin or over-cleaned.")
    if len(content_gaps) == 0:
        warnings.append("No content gaps detected: corpus may be overly uniform or densely repetitive.")
    if len(gateways) == 0:
        warnings.append("No conceptual gateways detected: graph may be fragmented or too flat.")

    diversity_score = None
    if isinstance(diversity, dict):
        diversity_score = diversity.get("score") or diversity.get("diversity")
    elif isinstance(diversity, (int, float)):
        diversity_score = diversity

    if diversity_score is not None:
        if diversity_score < 0.10:
            issues.append("Extremely low diversity: graph likely dominated by repetitive language.")
        elif diversity_score < 0.20:
            warnings.append("Low diversity: check for duplicated patterns or overly narrow corpus.")
        elif diversity_score > 0.85:
            warnings.append("Very high diversity: corpus may be too mixed or incoherent.")

    return {
        "passed": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
    }

def write_outputs(docs, graph_result, validation):
    corpus_path = OUT_DIR / "failures.corpus.md"
    graph_path = OUT_DIR / "failures.graph.json"
    validation_path = OUT_DIR / "failures.validation.json"

    corpus_text = "\n\n".join(f"## {d['title']}\n{d['text']}" for d in docs)
    corpus_path.write_text(corpus_text, encoding="utf-8")
    graph_path.write_text(json.dumps(graph_result, indent=2), encoding="utf-8")
    validation_path.write_text(json.dumps(validation, indent=2), encoding="utf-8")

def main():
    docs = build_corpus(RAW_DIR)
    corpus_text = "\n\n".join(d["text"] for d in docs)

    if len(corpus_text.split()) < 100:
        raise RuntimeError("Corpus too small after preprocessing.")

    graph_result = call_infranodus_graph(corpus_text)
    validation = validate_graph(graph_result)
    write_outputs(docs, graph_result, validation)

    if not validation["passed"]:
        raise RuntimeError(f"InfraNodus graph validation failed: {validation['issues']}")

if __name__ == "__main__":
    main()
```

This script is aligned with InfraNodus’s documented API outputs, including `extendedGraphSummary` fields such as `mainTopics`, `mainConcepts`, `contentGaps`, `conceptualGateways`, and `diversityStatistics`, and with Meta-Harness’s filesystem-centric optimization loop where traces, scores, and derived artifacts are persisted for the proposer to inspect.[^10_1][^10_3]

## Extended summary meaning

A useful way to interpret `extendedGraphSummary` is:

- `mainTopics`: the main topical communities inferred from co-occurring concepts, which are based on graph clustering over the text network.[^10_2][^10_1]
- `mainConcepts`: the most structurally important or salient concepts in the discourse, often closely related to highly connected or bridge-like nodes.[^10_4][^10_1]
- `contentGaps`: structural blind spots or underconnected areas where InfraNodus suggests useful bridges or missing questions.[^10_5][^10_1]
- `conceptualGateways`: concepts that connect distinct topical clusters and often act as high-leverage bridge terms.[^10_6][^10_1]
- `topRelations`: strong co-occurrence relations that summarize how concepts appear together in local context windows.[^10_2][^10_1]
- `diversityStatistics`: indicators of how concentrated, dispersed, or varied the discourse is across its conceptual structure.[^10_5][^10_1]

The underlying method matters here: InfraNodus turns text into lemmas, connects them within a 4-gram window, ranks nodes by betweenness centrality, and detects topical groups using community detection based on modularity. So these metrics are not embedding similarity metrics; they are graph-structural signals about discourse organization.[^10_7][^10_2]

## Automated checks

In Meta-Harness, the cleanest automation pattern is:

1. preprocess corpus from traces or goals,[^10_3]
2. call InfraNodus with stats and extended summary,[^10_1]
3. validate graph quality,[^10_1]
4. store artifacts in the proposer workspace,[^10_3]
5. block proposer use if the graph fails quality gates.[^10_3][^10_1]

The main checks I would automate are:

- corpus size floor, to catch over-filtered inputs.[^10_1]
- duplicate ratio, to catch repeated logs or wrappers.[^10_8]
- topical count sanity, to catch thin or collapsed graphs.[^10_1]
- diversity sanity, to catch graphs that are too repetitive or too mixed.[^10_9][^10_5]
- gateway presence, to catch graphs with no meaningful cross-cluster structure.[^10_1]
- dominant-node review, to catch centrality dominated by logging artifacts instead of domain concepts.[^10_8][^10_9]

These should write a validation artifact such as `analysis/infranodus/failures.validation.json`, and the proposer should read only graphs whose validation passed.[^10_3][^10_1]

## Low modularity

Low modularity usually means the discourse is not separating into meaningful topical communities, because the text is either too uniform, too short, or too noisy for cluster structure to emerge clearly. In practice, fix it by splitting mixed corpora into more coherent subsets, adding semantically meaningful summaries to raw logs, removing repeated scaffolding, and separating failures, goals, dependencies, and successes into distinct corpora.[^10_4][^10_2][^10_8]

A second cause is over-normalization, where you stripped too much and flattened the semantic variation out of the corpus. If your graph has almost no community structure, restore some domain-specific wording and keep concise human-authored failure summaries so the graph has real topic boundaries to work with.[^10_10][^10_4][^10_8]

## Betweenness issues

Betweenness problems usually show up in two ways: either a few meaningless wrapper terms dominate as bridge nodes, or there are no useful bridge nodes at all. If meaningless terms dominate, remove repeated system scaffolding, unify synonyms, and demote procedural phrases by preprocessing so high-centrality nodes represent true bridge concepts like rollback, retrieval policy, or dependency integrity instead of `tool_call` or `retrying`.[^10_6][^10_9][^10_2][^10_8]

If there are no useful bridge nodes, your corpus may be too fragmented or too shallow. In that case, add short interpretive summaries that state the relationships among concepts explicitly, because co-occurrence-based graphs need meaningful conceptual overlap in the text in order to expose pathways for meaning circulation.[^10_10][^10_2][^10_4]

## Diversity heuristics

InfraNodus documents diversity-oriented behavior and exposes diversity statistics, but it does not publish universal numeric pass/fail thresholds for all use cases, so the safest approach is to treat thresholds as **local heuristics** and calibrate them by corpus type. A practical starting rule set is:[^10_5][^10_1]

- `< 0.10`: likely too repetitive or over-cleaned; probably poor graph quality for most Meta-Harness uses.[^10_9][^10_5]
- `0.10–0.20`: narrow corpus; acceptable for tightly scoped incident analysis, but review manually.[^10_5]
- `0.20–0.60`: often a healthy operational band for focused but informative corpora, subject to validation against your real data.[^10_5][^10_1]
- `0.60–0.85`: broad and varied; useful for goals or research corpora if topics still remain coherent.[^10_5]
- `> 0.85`: likely too mixed for one graph unless intentionally aggregating many distinct themes.[^10_10][^10_5]

Those are not official InfraNodus thresholds; they are reasonable operational heuristics inferred from how InfraNodus describes diverse versus highly connected discourse and from the way text-network graphs behave under noisy or mixed corpora.[^10_2][^10_5]

## Practical policy

A strong first policy in Meta-Harness is:

- block graphs with extreme low diversity and no meaningful gateways,[^10_5][^10_1]
- warn on very high diversity and force manual review,[^10_5]
- warn on fewer than two main topics unless the corpus is intentionally narrow,[^10_1]
- reject graphs whose dominant concepts are boilerplate or runtime scaffolding.[^10_8][^10_9]

That keeps the graph layer useful without pretending the metrics are more standardized than the documentation supports.[^10_1][^10_5]

Would you like me to turn this into a reusable `infranodus_preprocess.py` and `graph_quality_gate.py` pair with a sample Meta-Harness folder layout?
<span style="display:none">[^10_11][^10_12][^10_13][^10_14][^10_15][^10_16][^10_17][^10_18]</span>

<div align="center">⁂</div>

[^10_1]: https://infranodus.com/api/docs

[^10_2]: https://infranodus.com/about/how-it-works

[^10_3]: https://yoonholee.com/meta-harness/

[^10_4]: https://infranodus.com/use-case/text-network-analysis

[^10_5]: https://support.noduslabs.com/hc/en-us/articles/13605983537692-InfraNodus-API-Access-Points

[^10_6]: https://noduslabs.com/research/visualization-text-polysingularity-network-analysis/

[^10_7]: https://www.youtube.com/watch?v=XkVtGS-v_7k

[^10_8]: https://infranodus.com/docs/text-network-analysis

[^10_9]: https://infranodus.com/use-case/text-mining

[^10_10]: https://support.noduslabs.com/hc/en-us/articles/8825622679580-Tutorial-Qualitative-Research-using-Text-Network-Thematic-Analysis

[^10_11]: https://www.youtube.com/watch?v=YFTF-dhNqg8

[^10_12]: https://pricepertoken.com/mcp-servers/infranodus-knowledge-graphs-text-analysis

[^10_13]: https://support.noduslabs.com/hc/en-us/articles/13605191136924-InfraNodus-API-Data-Structure

[^10_14]: https://ryuchen.github.io/essay/0x00000C.files/1-WWW- InfraNodus- Generating Insight Using Text Network Analysis.pdf

[^10_15]: https://arxiviq.substack.com/p/meta-harness-end-to-end-optimization

[^10_16]: https://www.youtube.com/watch?v=vOG9XBStUr8

[^10_17]: https://arxiv.org/pdf/2603.28052.pdf

[^10_18]: https://infranodus.com


---

# How to use contentGaps and conceptualGateways for RAG prompts

Full workflow automating InfraNodus in Meta-Harness loop

Advanced parameters like optimize=gaps for graph quality

Use `contentGaps` as prompts for what the system is **missing**, and use `conceptualGateways` as prompts for **what can connect** the missing pieces to what you already know. In a Meta-Harness loop, that means InfraNodus should sit between trace collection and proposer drafting, turning raw run history into gap-driven retrieval hints, bridge questions, and graph-quality diagnostics before the next harness edit is proposed.[^11_1][^11_2][^11_3][^11_4][^11_5]

## RAG prompt use

InfraNodus’s GraphRAG framing is to convert prompts and knowledge bases into graphs, follow graph edges for relational context, and use content gaps to improve the quality of the context supplied to the LLM. The docs explicitly describe `contentGaps` as structural blind spots and `conceptualGateways` as bridge concepts, which makes them ideal for retrieval planning and prompt shaping rather than just visualization.[^11_3][^11_6][^11_1]

A practical pattern is:

- Use `contentGaps` to ask: “What relevant topic is underconnected or absent in the retrieved context?”[^11_6][^11_1]
- Use `conceptualGateways` to ask: “Which terms or concepts can bridge the user question, the current retrieval cluster, and a neglected cluster?”[^11_7][^11_1]
- Then build a prompt that includes both retrieved passages and a short graph-aware instruction layer.[^11_1][^11_3]

Example prompt scaffold:

```text
You are answering using the retrieved project context.

Primary retrieval cluster:
- retrieval policy
- dependency integrity
- rollback checks

Underconnected topics from graph gaps:
- reproducibility
- bootstrap determinism

Bridge concepts from conceptual gateways:
- environment setup
- evaluation guardrails

Task:
1. Answer the user’s question using the retrieved passages.
2. Explicitly connect the primary cluster to the underconnected topics where relevant.
3. If the current retrieval is insufficient, state which missing topic should be retrieved next.
```

This works because `contentGaps` helps prevent narrow-context answers and `conceptualGateways` gives you the vocabulary for query expansion or bridge reasoning.[^11_3][^11_6][^11_1]

## Meta-Harness workflow

The full automated loop should look like this:

1. **Collect artifacts**
Gather traces, failure notes, benchmark rationales, goals, dependency docs, and accepted harness configs from prior candidates.[^11_5]
2. **Preprocess corpora**
Normalize terminology, remove repetitive scaffolding, split corpora by purpose, and create versioned bundles like `failures.corpus.md`, `goals.corpus.md`, and `dependencies.corpus.md`.[^11_8][^11_1]
3. **Run base graph extraction**
Call `graphAndStatements` with `doNotSave=true`, `addStats=true`, and `extendedGraphSummary=true` for each corpus.[^11_1]
4. **Run advice / gap analysis**
Call `graphAndAdvice` on failures and goals with `optimize=gaps`; use `requestMode=question` when you want bridge questions and `requestMode=idea` or equivalent advice generation mode when you want candidate interventions.[^11_2][^11_1]
5. **Optional graph comparison**
Use `compareGraphs` or `graphsAndAiAdvice` with `compareMode=difference` to compare baseline vs current-best candidate or goals vs implementation.[^11_1]
6. **Generate proposer brief**
Write a machine-readable or markdown brief that includes main topics, top bridge concepts, structural gaps, graph diffs, and benchmark status.[^11_5][^11_1]
7. **Run proposer**
The Meta-Harness proposer reads raw traces plus the InfraNodus artifacts from the filesystem and proposes a new harness revision.[^11_4][^11_5]
8. **Evaluate candidate**
Run the normal benchmark and QA suite, then re-run InfraNodus analysis on the new traces.[^11_5][^11_1]
9. **Accept or reject**
Keep benchmark-driven acceptance primary, and use graph signals as guardrails: reject candidates that introduce critical new gaps in safety, dependency integrity, or requirement coverage.[^11_6][^11_5]

This is aligned with Meta-Harness’s core design, where the proposer benefits from direct filesystem access to raw prior source, scores, and execution traces rather than only compressed summaries.[^11_4][^11_5]

## Automation details

A clean file layout is:

```text
meta_harness_workspace/
  evaluations/
    candidate_017/
      scores.json
      traces/
      summaries/
  analysis/
    infranodus/
      failures.graph.json
      failures.advice.json
      goals.graph.json
      goals.advice.json
      baseline_vs_best.diff.json
      proposal_brief.md
      history/
        iter_017/
```

The automation policy should be:

- always generate graph artifacts after evaluation and before proposal,[^11_5][^11_1]
- cache graph results per corpus hash to avoid repeated API calls on unchanged content,[^11_1]
- fail closed for bad corpora, but fail open to plain benchmark/proposer mode if InfraNodus is temporarily unavailable.[^11_9][^11_1]

That keeps the loop robust without making InfraNodus a single point of failure.[^11_9][^11_4]

## Advanced parameters

The most important advanced parameter for quality-sensitive workflows is `optimize=gaps`. InfraNodus documents that this mode identifies structural gaps in the discourse graph and directs the prompt to bridge them; when the graph is diverse, it focuses on the most common gap, and when the graph is highly connected, it pushes attention toward the least connected peripheral topics.[^11_2][^11_1]

How to use the main optimize modes:


| Mode | Best use | Effect |
| :-- | :-- | :-- |
| `gaps` | Find blind spots, generate bridge questions, improve prompt coverage.[^11_1][^11_2] | Focuses on structural gaps and missing bridges.[^11_1] |
| `develop` | Expand an existing discourse in a balanced way.[^11_1][^11_2] | Pulls top nodes from all clusters to develop the current topic space.[^11_2] |
| `reinforce` | Stay focused on dominant themes for narrow tasks.[^11_2] | Emphasizes top nodes from top clusters.[^11_2] |
| `latent` | Explore underdeveloped or peripheral topics.[^11_1][^11_2] | Identifies less represented entry points and possible connections to other discourses.[^11_1] |

For graph quality work inside Meta-Harness, a good pattern is:

- use `gaps` on failures and goals,[^11_2]
- use `develop` on research corpora or design exploration,[^11_2]
- use `reinforce` only when the task truly needs narrower focus,[^11_2]
- use `latent` when you suspect the harness is missing peripheral but important context.[^11_2]

`gapDepth` is particularly useful with `optimize=gaps`, because higher values tell InfraNodus to probe deeper, less obvious gaps involving smaller or more peripheral topics. In practice:[^11_1]

- `gapDepth=0` for obvious and high-signal gap detection,[^11_1]
- `gapDepth=1–2` for richer proposer diagnostics in mature corpora,[^11_1]
- `gapDepth=3` only for exploratory analysis, because deeper gaps can become more speculative.[^11_1]


## Prompt recipes

Two high-value prompt patterns:

### 1. Query expansion prompt

Use when retrieval is too narrow.

```text
User question: How do we improve harness reproducibility?

Primary retrieved topics:
- evaluation
- traces
- harness config

Graph content gaps:
- bootstrap determinism
- seed management

Conceptual gateways:
- environment setup
- dependency pinning

Instruction:
Expand retrieval using the gateway concepts and include documents that bridge evaluation, bootstrap determinism, and seed management.
```

This helps the retriever move from local similarity to relational expansion.[^11_3][^11_1]

### 2. Synthesis prompt

Use when answering from retrieved context.

```text
Answer using the retrieved passages.
Prioritize the main topics already present.
Bridge any relevant graph gaps using these gateway concepts:
[conceptual gateways]
Mention where the current context appears incomplete based on:
[content gaps]
```

This makes the model less likely to ignore underrepresented but structurally important themes.[^11_6][^11_3]

## Quality guardrails

Advanced parameters help only if you keep a few guardrails:

- Do not use `optimize=gaps` on dirty mixed corpora; you will get misleading bridges.[^11_8][^11_1]
- Do not force bridge prompts when the separation is intentional, such as safety isolation or unrelated subsystems.[^11_8]
- Do not let graph advice override benchmark evidence in candidate acceptance.[^11_5]
- Re-run graph analysis after each accepted harness change to see whether the failure structure actually improved.[^11_5][^11_1]

That gives you a reliable pattern: InfraNodus supplies structural guidance, while Meta-Harness remains the disciplined optimization loop.[^11_4][^11_2]

Would you like a next step focused on a concrete end-to-end pseudocode loop or a real YAML + Python skeleton for this automation?
<span style="display:none">[^11_10][^11_11][^11_12][^11_13][^11_14][^11_15][^11_16][^11_17]</span>

<div align="center">⁂</div>

[^11_1]: https://infranodus.com/api/docs

[^11_2]: https://support.noduslabs.com/hc/en-us/articles/13605983537692-InfraNodus-API-Access-Points

[^11_3]: https://infranodus.com/use-case/ai-knowledge-graphs

[^11_4]: https://yoonholee.com/meta-harness/

[^11_5]: https://arxiv.org/html/2603.28052v1

[^11_6]: https://infranodus.com/docs/content-gap-analysis

[^11_7]: https://noduslabs.com/research/visualization-text-polysingularity-network-analysis/

[^11_8]: https://infranodus.com/about/how-it-works

[^11_9]: https://infranodus.com/docs/graph-rag-knowledge-graph

[^11_10]: https://infranodus.com/api

[^11_11]: https://community.crewai.com/t/content-gap-analysis-with-infranodus-portable-graphrag/5494

[^11_12]: https://rapidapi.com/infranodus-infranodus-default/api/infranodus

[^11_13]: https://n8n.io/workflows/5720-generate-content-ideas-from-pdfs-with-infranodus-graphrag-and-ai-gap-analysis/

[^11_14]: https://infranodus.com

[^11_15]: https://www.linkedin.com/posts/baraktur_meta-harness-end-to-end-optimization-of-activity-7444744842603143168-KJtv

[^11_16]: https://infranodus.com/use-case/network-analysis-visualization

[^11_17]: https://infranodus.com/docs/knowledge-graphs-for-llms


---

# Example curl script for optimize=gaps with gapDepth in Meta-Harness

How to interpret contentGaps output for RAG prompt augmentation

Full Python code for InfraNodus-optimized=latent in agent loop

Compare optimize=gaps vs optimize=latent for graph quality

Here are the key patterns: use `optimize=gaps` when you want InfraNodus to bridge structural gaps in a discourse graph, optionally pushing deeper with `gapDepth`; use `optimize=latent` when you want it to surface underrepresented peripheral clusters and possible entry points beyond the current discourse core. In a Meta-Harness loop, `gaps` is usually better for corrective QA and RAG augmentation, while `latent` is better for exploratory proposer ideation and broadening search beyond the current failure narrative.[^12_1][^12_2][^12_3][^12_4]

## curl example

This example shows a typical Meta-Harness post-evaluation call that sends a cleaned failure corpus to InfraNodus using `optimize=gaps` with `gapDepth=2` and asks for bridge questions.[^12_2][^12_1]

```bash
#!/usr/bin/env bash
set -euo pipefail

API_TOKEN="${INFRANODUS_API_TOKEN:?Set INFRANODUS_API_TOKEN first}"
BASE_URL="https://infranodus.com/api/v1"
CORPUS_FILE="meta_harness_workspace/analysis/infranodus/failures.corpus.md"
OUT_FILE="meta_harness_workspace/analysis/infranodus/failures.gaps.advice.json"

mkdir -p "$(dirname "$OUT_FILE")"

jq -Rs --arg text "$(cat "$CORPUS_FILE")" '
{
  text: $text,
  requestMode: "question"
}' <<<"" | curl -sS -X POST \
  "${BASE_URL}/graphAndAdvice?doNotSave=true&addStats=true&extendedGraphSummary=true&optimize=gaps&gapDepth=2" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data-binary @- \
  > "$OUT_FILE"

echo "Saved InfraNodus gaps advice to $OUT_FILE"
```

According to the API docs, `gaps` identifies structural gaps in the graph and `gapDepth` from 0 to 3 selects deeper, less obvious gaps, with higher values bringing smaller peripheral topics into focus.[^12_1][^12_2]

## contentGaps for RAG

The safest way to interpret `contentGaps` for RAG prompt augmentation is: “these are the underconnected conceptual regions that may matter but are not well linked in the current knowledge representation.” They should therefore be used to **expand or rebalance retrieval**, not as facts to insert directly into the answer.[^12_5][^12_6][^12_7][^12_1]

A practical interpretation flow is:

1. Read `contentGaps` as missing bridge opportunities between topical clusters.[^12_5][^12_1]
2. Convert them into retrieval hints or follow-up subqueries, not final answer statements.[^12_6][^12_7]
3. Use `conceptualGateways` to choose the best bridge terms for expansion into adjacent relevant documents.[^12_7][^12_1]
4. Re-run retrieval and only then synthesize the response from actual documents.[^12_6][^12_7]

Example augmentation template:

```text
User question:
How do we improve harness reproducibility?

Current main topics:
- evaluation
- traces
- harness config

contentGaps:
- bootstrap determinism
- dependency pinning
- rollback consistency

conceptualGateways:
- environment setup
- evaluation guardrails

Instruction to retriever:
Expand retrieval to documents that connect evaluation, bootstrap determinism, dependency pinning, and rollback consistency using the gateway terms environment setup and evaluation guardrails.
Do not assume the content gaps are facts; use them to guide additional retrieval.
```

This is consistent with InfraNodus’s prompt augmentation and GraphRAG guidance, where graph summaries and relational context are used to make retrieval and prompting more pertinent to the underlying knowledge base.[^12_8][^12_7][^12_6]

## Python loop

Below is a full Python example for using `optimize=latent` inside an agent loop that prepares a corpus, calls InfraNodus, stores artifacts, and creates a proposer brief for the next Meta-Harness iteration.[^12_3][^12_1]

```python
import os
import json
import hashlib
from pathlib import Path
import requests

API_TOKEN = os.environ["INFRANODUS_API_TOKEN"]
BASE_URL = "https://infranodus.com/api/v1"
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json",
}

WORKSPACE = Path("meta_harness_workspace")
TRACE_DIR = WORKSPACE / "evaluations" / "current_best" / "traces"
OUT_DIR = WORKSPACE / "analysis" / "infranodus"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def file_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def load_corpus(trace_dir: Path) -> str:
    chunks = []
    for path in sorted(trace_dir.rglob("*")):
        if path.is_file() and path.suffix.lower() in {".md", ".txt", ".log", ".json"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
            if path.suffix.lower() == ".json":
                try:
                    text = json.dumps(json.loads(text), indent=2)
                except Exception:
                    pass
            chunks.append(f"# {path.name}\n{text[:4000]}")
    return "\n\n".join(chunks)

def infranodus_graph_and_advice(text: str, optimize_mode="latent", request_mode="question"):
    url = f"{BASE_URL}/graphAndAdvice"
    params = {
        "doNotSave": "true",
        "addStats": "true",
        "extendedGraphSummary": "true",
        "optimize": optimize_mode,
    }
    payload = {
        "text": text,
        "requestMode": request_mode
    }
    r = requests.post(url, params=params, headers=HEADERS, json=payload, timeout=90)
    r.raise_for_status()
    return r.json()

def validate_graph_summary(result: dict):
    summary = result.get("extendedGraphSummary", {}) or result.get("graphSummary", {})
    topics = summary.get("mainTopics", [])
    concepts = summary.get("mainConcepts", [])
    gaps = summary.get("contentGaps", [])
    gateways = summary.get("conceptualGateways", [])

    warnings = []
    if len(topics) < 2:
        warnings.append("Few main topics; corpus may be narrow or repetitive.")
    if len(concepts) < 5:
        warnings.append("Few main concepts; corpus may be too thin.")
    if len(gateways) == 0:
        warnings.append("No conceptual gateways detected; latent exploration may be weak.")
    return {"warnings": warnings}

def build_proposal_brief(result: dict, validation: dict) -> str:
    summary = result.get("extendedGraphSummary", {}) or result.get("graphSummary", {})
    advice = result.get("aiAdvice", "")

    main_topics = summary.get("mainTopics", [])
    main_concepts = summary.get("mainConcepts", [])
    gaps = summary.get("contentGaps", [])
    gateways = summary.get("conceptualGateways", [])

    lines = []
    lines.append("# InfraNodus proposer brief")
    lines.append("")
    lines.append("## Main topics")
    for x in main_topics[:10]:
        lines.append(f"- {x}")
    lines.append("")
    lines.append("## Main concepts")
    for x in main_concepts[:12]:
        lines.append(f"- {x}")
    lines.append("")
    lines.append("## Content gaps")
    for x in gaps[:10]:
        lines.append(f"- {x}")
    lines.append("")
    lines.append("## Conceptual gateways")
    for x in gateways[:10]:
        lines.append(f"- {x}")
    lines.append("")
    lines.append("## Advice")
    lines.append(str(advice))
    lines.append("")
    lines.append("## Validation warnings")
    for x in validation["warnings"]:
        lines.append(f"- {x}")
    return "\n".join(lines)

def main():
    corpus = load_corpus(TRACE_DIR)
    if len(corpus.split()) < 100:
        raise RuntimeError("Corpus too small for latent exploration.")

    corpus_hash = file_hash(corpus)
    corpus_path = OUT_DIR / "latent.corpus.md"
    result_path = OUT_DIR / "latent.advice.json"
    brief_path = OUT_DIR / "proposal_brief.latent.md"
    meta_path = OUT_DIR / "latent.meta.json"

    corpus_path.write_text(corpus, encoding="utf-8")

    result = infranodus_graph_and_advice(
        text=corpus,
        optimize_mode="latent",
        request_mode="question"
    )

    validation = validate_graph_summary(result)
    brief = build_proposal_brief(result, validation)

    result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    brief_path.write_text(brief, encoding="utf-8")
    meta_path.write_text(json.dumps({
        "corpus_hash": corpus_hash,
        "optimize": "latent",
        "requestMode": "question"
    }, indent=2), encoding="utf-8")

    print(f"Saved corpus to {corpus_path}")
    print(f"Saved result to {result_path}")
    print(f"Saved proposer brief to {brief_path}")

if __name__ == "__main__":
    main()
```

This example follows the Meta-Harness workflow model where the proposer reads persisted files from the workspace, and it uses InfraNodus as a pre-proposal structural analysis stage that can widen exploration toward peripheral or underdeveloped areas.[^12_4][^12_2][^12_3]

## gaps vs latent

The core difference is intent.[^12_2][^12_1]


| Mode | What it looks for | Best use in Meta-Harness | Effect on graph quality work |
| :-- | :-- | :-- | :-- |
| `gaps` | Structural gaps between existing topical clusters.[^12_1][^12_2] | QA, corrective retrieval, benchmark expansion, failure diagnosis.[^12_5][^12_3] | Better for detecting missing bridges and undercovered requirements.[^12_5] |
| `latent` | Least represented clusters and entry points beyond the discourse core.[^12_1][^12_2] | Exploration, proposer ideation, expanding search space, finding neglected avenues.[^12_2][^12_3] | Better for surfacing peripheral but possibly useful topics.[^12_2] |

In practice:

- choose `gaps` when you already have a meaningful graph and want to bridge what is missing inside it,[^12_1][^12_2]
- choose `latent` when the graph is too centered on current narratives and you want entry points into weaker or peripheral regions.[^12_2]

For graph quality specifically, `gaps` is usually more reliable for operational QA because it works against identifiable missing bridges in a known discourse, while `latent` is more exploratory and can be noisier on dirty or weak corpora.[^12_5][^12_2]

## Practical policy

A good operating policy is:

- Use `optimize=gaps` on failure corpora, goal corpora, and retrieval corpora when the task is to reduce blind spots or improve prompt coverage.[^12_1][^12_5]
- Use `gapDepth=0` for routine runs and `gapDepth=1–2` when you want less obvious bridges for mature corpora.[^12_2][^12_1]
- Use `optimize=latent` on proposer ideation runs, research synthesis, or when you suspect the harness is stuck in a narrow local optimum.[^12_3][^12_2]
- Do not use either mode on mixed, noisy, or unvalidated corpora, because both will happily generate structurally plausible but operationally misleading guidance from bad inputs.[^12_9][^12_1]

That combination gives you a stable corrective mode and a broader exploratory mode inside the same Meta-Harness loop.[^12_3][^12_2]

Would you like the next step to be a combined shell + Python toolkit layout for these InfraNodus modes inside your workspace?
<span style="display:none">[^12_10][^12_11][^12_12][^12_13][^12_14][^12_15][^12_16]</span>

<div align="center">⁂</div>

[^12_1]: https://infranodus.com/api/docs

[^12_2]: https://support.noduslabs.com/hc/en-us/articles/13605983537692-InfraNodus-API-Access-Points

[^12_3]: https://yoonholee.com/meta-harness/

[^12_4]: https://arxiv.org/html/2603.28052v1

[^12_5]: https://infranodus.com/docs/content-gap-analysis

[^12_6]: https://support.noduslabs.com/hc/en-us/articles/19602201629596-Prompt-Augmentation-for-LLM-RAG

[^12_7]: https://infranodus.com/use-case/ai-knowledge-graphs

[^12_8]: https://infranodus.com/docs/graph-rag-knowledge-graph

[^12_9]: https://infranodus.com/about/how-it-works

[^12_10]: https://infranodus.com/api

[^12_11]: https://infranodus.com/docs

[^12_12]: https://huggingface.co/papers/2603.28052

[^12_13]: https://infranodus.com/docs/seo-llm-optimization

[^12_14]: https://www.youtube.com/watch?v=vkvRWto3TnQ

[^12_15]: https://infranodus.com/skills/use-cases

[^12_16]: https://community.crewai.com/t/content-gap-analysis-with-infranodus-portable-graphrag/5494


---

# Example curl for optimize=latent in InfraNodus API

How to set gapDepth values for different graph types

Full code for optimize=develop in Meta-Harness agent

Integrating reinforce mode for discourse strengthening

Compare gaps vs latent optimization in RAG performance

Here’s the practical answer: use `optimize=latent` when you want InfraNodus to find underrepresented entry points and push the agent toward the discourse periphery, use `optimize=develop` when you want balanced expansion across all major clusters, and use `optimize=reinforce` when you want the agent to stay centered on the dominant discourse and strengthen it. For Meta-Harness, that means `develop` and `reinforce` are usually better for controlled proposer context building, while `latent` is better for exploratory ideation and escaping narrow local optima.[^13_1][^13_2][^13_3][^13_4][^13_5]

## curl for latent

This is a minimal `curl` example for `optimize=latent` against the InfraNodus API.[^13_2][^13_1]

```bash
#!/usr/bin/env bash
set -euo pipefail

API_TOKEN="${INFRANODUS_API_TOKEN:?Missing INFRANODUS_API_TOKEN}"
BASE_URL="https://infranodus.com/api/v1"
CORPUS_FILE="meta_harness_workspace/analysis/infranodus/failures.corpus.md"
OUT_FILE="meta_harness_workspace/analysis/infranodus/failures.latent.advice.json"

mkdir -p "$(dirname "$OUT_FILE")"

TEXT_CONTENT="$(cat "$CORPUS_FILE")"

curl -sS -X POST \
  "${BASE_URL}/graphAndAdvice?doNotSave=true&addStats=true&extendedGraphSummary=true&optimize=latent" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg text "$TEXT_CONTENT" --arg requestMode "question" '{text:$text, requestMode:$requestMode}')" \
  > "$OUT_FILE"

echo "Saved latent advice to $OUT_FILE"
```

InfraNodus documents `latent` as identifying the least represented topical clusters and ideal points of entry that can connect the discourse to other discourses, which makes it useful for exploratory context expansion rather than direct error correction.[^13_1][^13_2]

## gapDepth values

`gapDepth` is specifically documented for `optimize=gaps`, where higher values select deeper, less obvious gaps and bring smaller, more peripheral topics into focus. One support article also describes a wider range up to 7 corresponding to deeper gap levels, while the main API docs describe 0–3, so the safest operational choice is to stay within the officially documented lower range unless you verify broader support in your own account or endpoint behavior.[^13_4][^13_2][^13_1]

A practical setting guide is:


| Graph type | Recommended `gapDepth` | Why |
| :-- | :-- | :-- |
| Small, focused failure corpus | `0` or `1` [^13_1][^13_2] | Surfaces obvious missing bridges without overfitting to tiny peripheral clusters.[^13_2] |
| Mature failure / QA corpus | `1` or `2` [^13_1][^13_2] | Helps reveal non-obvious recurring blind spots after the obvious ones are already known.[^13_2] |
| Goal / requirements corpus | `1` or `2` [^13_1][^13_2] | Good for finding under-modeled tensions or omitted goal bridges.[^13_6] |
| Exploratory research corpus | `2` or `3` [^13_1][^13_2] | Useful when you intentionally want more peripheral or speculative connections.[^13_2] |
| Noisy or mixed corpus | Avoid deep `gapDepth` [^13_7][^13_2] | Deeper gaps on low-quality input often produce misleading bridges.[^13_7] |

In short, start shallow and only go deeper when the corpus is already clean and coherent.[^13_7][^13_2]

## Python for develop

Below is a full Python example for using `optimize=develop` in a Meta-Harness-style agent loop, where the system collects trace text, calls InfraNodus, stores artifacts, and writes a proposer brief.[^13_5][^13_1]

```python
import os
import json
import hashlib
from pathlib import Path
import requests

API_TOKEN = os.environ["INFRANODUS_API_TOKEN"]
BASE_URL = "https://infranodus.com/api/v1"
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json",
}

WORKSPACE = Path("meta_harness_workspace")
TRACE_DIR = WORKSPACE / "evaluations" / "current_best" / "traces"
OUT_DIR = WORKSPACE / "analysis" / "infranodus"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def load_trace_corpus(trace_dir: Path) -> str:
    docs = []
    for path in sorted(trace_dir.rglob("*")):
        if path.is_file() and path.suffix.lower() in {".md", ".txt", ".log", ".json"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
            if path.suffix.lower() == ".json":
                try:
                    text = json.dumps(json.loads(text), indent=2)
                except Exception:
                    pass
            docs.append(f"# {path.name}\n{text[:5000]}")
    return "\n\n".join(docs)

def call_graph_and_advice(text: str, optimize: str, request_mode: str = "question"):
    url = f"{BASE_URL}/graphAndAdvice"
    params = {
        "doNotSave": "true",
        "addStats": "true",
        "extendedGraphSummary": "true",
        "optimize": optimize,
    }
    payload = {
        "text": text,
        "requestMode": request_mode,
    }
    r = requests.post(url, params=params, headers=HEADERS, json=payload, timeout=90)
    r.raise_for_status()
    return r.json()

def summarize_result(result: dict):
    summary = result.get("extendedGraphSummary", {}) or result.get("graphSummary", {})
    return {
        "mainTopics": summary.get("mainTopics", []),
        "mainConcepts": summary.get("mainConcepts", []),
        "contentGaps": summary.get("contentGaps", []),
        "conceptualGateways": summary.get("conceptualGateways", []),
        "topRelations": summary.get("topRelations", []),
        "aiAdvice": result.get("aiAdvice", ""),
    }

def write_brief(summary: dict, optimize: str) -> str:
    lines = [
        f"# InfraNodus proposer brief ({optimize})",
        "",
        "## Main topics",
    ]
    lines += [f"- {x}" for x in summary["mainTopics"][:10]]
    lines += ["", "## Main concepts"]
    lines += [f"- {x}" for x in summary["mainConcepts"][:12]]
    lines += ["", "## Content gaps"]
    lines += [f"- {x}" for x in summary["contentGaps"][:10]]
    lines += ["", "## Conceptual gateways"]
    lines += [f"- {x}" for x in summary["conceptualGateways"][:10]]
    lines += ["", "## Advice", str(summary["aiAdvice"])]
    return "\n".join(lines)

def main():
    corpus = load_trace_corpus(TRACE_DIR)
    if len(corpus.split()) < 100:
        raise RuntimeError("Corpus too small after loading traces.")

    optimize = "develop"
    corpus_hash = hash_text(corpus)

    result = call_graph_and_advice(
        text=corpus,
        optimize=optimize,
        request_mode="question"
    )
    summary = summarize_result(result)
    brief = write_brief(summary, optimize)

    (OUT_DIR / "develop.corpus.md").write_text(corpus, encoding="utf-8")
    (OUT_DIR / "develop.advice.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (OUT_DIR / "proposal_brief.develop.md").write_text(brief, encoding="utf-8")
    (OUT_DIR / "develop.meta.json").write_text(
        json.dumps({"optimize": optimize, "corpus_hash": corpus_hash}, indent=2),
        encoding="utf-8"
    )

    print("Saved InfraNodus develop artifacts.")

if __name__ == "__main__":
    main()
```

This is appropriate because InfraNodus describes `develop` as using top nodes from all graph clusters, which makes it a good balanced mode for broadening the proposer’s context without drifting too far into speculative periphery.[^13_2][^13_4]

## Reinforce mode

`reinforce` is useful when you want discourse strengthening rather than exploration. Support documentation explains it as focusing on top nodes from the top clusters, with an emphasis on strengthening the main discourse structure rather than widening it.[^13_4][^13_1][^13_2]

In Meta-Harness, good uses for `reinforce` are:

- stabilizing benchmark and goal prompts around dominant validated themes,[^13_2]
- strengthening retrieval for narrow, repetitive operational tasks,[^13_3][^13_2]
- generating proposer briefs that stay close to the current best candidate’s strongest clusters instead of exploring peripheral topics.[^13_5][^13_2]

A good operational pattern is:

- `reinforce` for execution-time answer generation on narrow tasks,[^13_2]
- `develop` for proposer context building,[^13_4]
- `latent` for exploration when improvement stalls,[^13_2]
- `gaps` for QA and missing-bridge correction.[^13_6][^13_1]


## gaps vs latent in RAG

InfraNodus’s docs and support material clearly distinguish the two modes structurally, but they do not provide a published benchmark table quantifying RAG performance differences between `gaps` and `latent` across standard tasks. So the most defensible answer is directional: `gaps` should usually improve RAG when the failure mode is **missing bridges inside a known corpus**, while `latent` should help when the failure mode is **overfocus on dominant themes and lack of peripheral exploration**.[^13_3][^13_1][^13_2]

In practical terms:


| Mode | Likely RAG benefit | Risk |
| :-- | :-- | :-- |
| `gaps` | Better coverage of underconnected but relevant topics, stronger bridge retrieval, fewer blind spots.[^13_6][^13_3] | Can force irrelevant bridges if the corpus is noisy or the separation is intentional.[^13_7][^13_2] |
| `latent` | Better exploration of peripheral concepts and novel entry points, useful when current retrieval is too centered.[^13_2] | Can pull in weaker or less relevant material and reduce answer precision.[^13_2][^13_3] |

So for RAG performance:

- use `gaps` first in production QA and requirements workflows,[^13_6][^13_3]
- use `latent` as a secondary expansion mode or fallback when retrieval appears stuck in a narrow loop.[^13_2]


## Recommended operating policy

A good Meta-Harness policy would be:

- `develop` for proposer briefing every iteration.[^13_4][^13_2]
- `gaps` on failures, goals, and evaluation narratives for QA hardening.[^13_1][^13_6]
- `reinforce` for stable execution-time prompts where high precision matters.[^13_2]
- `latent` only when improvement plateaus or when you explicitly want exploratory search beyond the current discourse core.[^13_5][^13_2]

That gives you one stable mode, one corrective mode, one strengthening mode, and one exploratory mode.[^13_4][^13_2]

Would you like me to package these modes into one unified InfraNodus strategy matrix for your full meta-improvement workflow?
<span style="display:none">[^13_10][^13_11][^13_12][^13_13][^13_14][^13_15][^13_16][^13_17][^13_8][^13_9]</span>

<div align="center">⁂</div>

[^13_1]: https://infranodus.com/api/docs

[^13_2]: https://support.noduslabs.com/hc/en-us/articles/13605983537692-InfraNodus-API-Access-Points

[^13_3]: https://infranodus.com/use-case/ai-knowledge-graphs

[^13_4]: https://support.noduslabs.com/hc/en-us/articles/19226701201436-Portable-GraphRAG-Supercharge-Your-AI-Thinking-with-Knowledge-Graphs

[^13_5]: https://yoonholee.com/meta-harness/

[^13_6]: https://infranodus.com/docs/content-gap-analysis

[^13_7]: https://infranodus.com/about/how-it-works

[^13_8]: https://infranodus.com/api

[^13_9]: https://infranodus.com/skills/use-cases

[^13_10]: https://infranodus.com/docs/knowledge-graphs-llm-reasoning

[^13_11]: https://support.noduslabs.com/hc/en-us/articles/25670401036316-InfraNodus-MCP-Server-Tools-Description

[^13_12]: https://www.emergentmind.com/topics/graphrag-optimisation

[^13_13]: https://infranodus.com/docs/graph-rag-knowledge-graph

[^13_14]: https://support.noduslabs.com/hc/en-us/articles/19311397123996-InfraNodus-Crew-AI-Enhancing-AI-Agent-Workflows-with-Content-Gap-Detection-Research-Questions

[^13_15]: https://support.noduslabs.com/hc/en-us/articles/18430500689820-Optimize-Your-AI-Knowledge-Base-Enhance-Your-RAG-with-a-Graph

[^13_16]: https://infranodus.com/showcase

[^13_17]: https://dify.ai/blog/enhance-dify-rag-with-infranodus-expand-your-llm-s-context


---

# Full code for optimize=reinforce in Meta-Harness agent

Below is a solid full-code pattern for `optimize=reinforce` in a Meta-Harness-style agent loop: it builds a curated corpus from traces and summaries, calls InfraNodus with `graphAndAdvice?optimize=reinforce`, stores the returned graph artifacts, and writes a proposer brief that emphasizes the strongest current discourse clusters rather than exploratory or gap-finding behavior.[^14_1][^14_2][^14_3]

## Python example

`reinforce` is appropriate when you want the proposer or downstream agent to stay anchored to the top nodes in the top clusters of the graph, which InfraNodus documents as reinforcing the current discourse. That makes it a good fit for stabilizing mature workflows, tightening prompts around validated themes, or strengthening a current best harness rather than searching for novel directions.[^14_2][^14_3][^14_1]

```python
import os
import re
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any
import requests

API_TOKEN = os.environ["INFRANODUS_API_TOKEN"]
BASE_URL = "https://infranodus.com/api/v1"
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json",
}

WORKSPACE = Path("meta_harness_workspace")
EVAL_DIR = WORKSPACE / "evaluations" / "current_best"
TRACE_DIR = EVAL_DIR / "traces"
SUMMARY_DIR = EVAL_DIR / "summaries"
OUT_DIR = WORKSPACE / "analysis" / "infranodus"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CANONICAL_TERMS = {
    r"\bmh\b": "meta harness",
    r"\bgraphrag\b": "graph rag",
    r"\bdep map\b": "dependency map",
    r"\bbootstrapping\b": "bootstrap",
    r"\bqa\b": "quality assurance",
    r"\brag\b": "retrieval augmented generation",
}

NOISE_PATTERNS = [
    r"^INFO\b.*$",
    r"^DEBUG\b.*$",
    r"^TRACE\b.*$",
    r"^tool_call\s+\w+.*$",
    r"^SYSTEM PROMPT LOADED.*$",
    r"^retrying\.*$",
    r"^Traceback \(most recent call last\):.*$",
    r"^\s*File \".*\", line \d+.*$",
]

ALLOWED_SUFFIXES = {".md", ".txt", ".log", ".json"}

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def read_text_file(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if path.suffix.lower() == ".json":
        try:
            return json.dumps(json.loads(text), indent=2)
        except Exception:
            return text
    return text

def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n")
    lines = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if any(re.match(p, line) for p in NOISE_PATTERNS):
            continue
        line = re.sub(r"\s+", " ", line)
        lines.append(line)

    text = "\n".join(lines).lower()

    for pattern, replacement in CANONICAL_TERMS.items():
        text = re.sub(pattern, replacement, text)

    return text.strip()

def extract_candidate_docs(base_dir: Path) -> List[Dict[str, str]]:
    docs = []
    if not base_dir.exists():
        return docs

    for path in sorted(base_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in ALLOWED_SUFFIXES:
            continue

        raw = read_text_file(path)
        cleaned = normalize_text(raw)
        if len(cleaned.split()) < 15:
            continue

        docs.append({
            "path": str(path),
            "title": path.name,
            "text": cleaned[:8000],
        })
    return docs

def build_reinforce_corpus() -> str:
    trace_docs = extract_candidate_docs(TRACE_DIR)
    summary_docs = extract_candidate_docs(SUMMARY_DIR)

    all_docs = trace_docs + summary_docs
    if not all_docs:
        raise RuntimeError("No usable documents found for reinforce corpus.")

    sections = []
    for doc in all_docs:
        sections.append(f"## {doc['title']}\nsource: {doc['path']}\n\n{doc['text']}")
    return "\n\n".join(sections)

def infranodus_graph_and_advice(
    text: str,
    request_mode: str = "question",
    include_statements: bool = False,
    include_graph: bool = True,
) -> Dict[str, Any]:
    url = f"{BASE_URL}/graphAndAdvice"
    params = {
        "doNotSave": "true",
        "addStats": "true",
        "optimize": "reinforce",
        "extendedGraphSummary": "true",
        "includeStatements": "true" if include_statements else "false",
        "includeGraph": "true" if include_graph else "false",
        "includeGraphSummary": "true",
    }
    payload = {
        "text": text,
        "requestMode": request_mode
    }

    response = requests.post(
        url,
        params=params,
        headers=HEADERS,
        json=payload,
        timeout=120
    )
    response.raise_for_status()
    return response.json()

def extract_summary(result: Dict[str, Any]) -> Dict[str, Any]:
    summary = result.get("extendedGraphSummary") or result.get("graphSummary") or {}
    stats = result.get("stats", {}) or {}

    return {
        "mainTopics": summary.get("mainTopics", []),
        "mainConcepts": summary.get("mainConcepts", []),
        "contentGaps": summary.get("contentGaps", []),
        "conceptualGateways": summary.get("conceptualGateways", []),
        "topRelations": summary.get("topRelations", []),
        "diversityStatistics": summary.get("diversityStatistics", stats.get("diversityStatistics", {})),
        "aiAdvice": result.get("aiAdvice", ""),
        "graphSummary": result.get("graphSummary", ""),
    }

def validate_reinforce_graph(summary: Dict[str, Any]) -> Dict[str, Any]:
    issues = []
    warnings = []

    topics = summary.get("mainTopics", [])
    concepts = summary.get("mainConcepts", [])
    gateways = summary.get("conceptualGateways", [])
    gaps = summary.get("contentGaps", [])
    diversity = summary.get("diversityStatistics", {})

    if len(topics) < 1:
        issues.append("No main topics detected.")
    if len(concepts) < 5:
        warnings.append("Few main concepts; reinforce context may be underpowered.")
    if len(gateways) == 0:
        warnings.append("No conceptual gateways detected; discourse may be too flat.")
    if len(gaps) == 0:
        warnings.append("No content gaps detected; corpus may be very tightly clustered or repetitive.")

    diversity_score = None
    if isinstance(diversity, dict):
        diversity_score = diversity.get("score") or diversity.get("diversity")
    elif isinstance(diversity, (int, float)):
        diversity_score = diversity

    if diversity_score is not None:
        if diversity_score < 0.10:
            warnings.append("Very low diversity; reinforce output may be over-concentrated.")
        elif diversity_score > 0.85:
            warnings.append("Very high diversity; reinforce mode may be acting on a mixed corpus.")

    return {
        "passed": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
    }

def build_proposer_brief(summary: Dict[str, Any], validation: Dict[str, Any]) -> str:
    lines = []
    lines.append("# InfraNodus proposer brief (reinforce)")
    lines.append("")
    lines.append("Use this brief to strengthen the best current discourse, not to explore new directions.")
    lines.append("Prioritize stable, dominant themes that already correlate with strong candidate behavior.")
    lines.append("")

    lines.append("## Main topics")
    for x in summary.get("mainTopics", [])[:10]:
        lines.append(f"- {x}")
    lines.append("")

    lines.append("## Main concepts")
    for x in summary.get("mainConcepts", [])[:12]:
        lines.append(f"- {x}")
    lines.append("")

    lines.append("## Conceptual gateways")
    for x in summary.get("conceptualGateways", [])[:10]:
        lines.append(f"- {x}")
    lines.append("")

    lines.append("## Content gaps")
    for x in summary.get("contentGaps", [])[:8]:
        lines.append(f"- {x}")
    lines.append("")

    lines.append("## Top relations")
    for x in summary.get("topRelations", [])[:12]:
        lines.append(f"- {x}")
    lines.append("")

    lines.append("## AI advice")
    lines.append(str(summary.get("aiAdvice", "")))
    lines.append("")

    lines.append("## Validation warnings")
    if validation["warnings"]:
        for w in validation["warnings"]:
            lines.append(f"- {w}")
    else:
        lines.append("- None")
    lines.append("")

    lines.append("## Proposer policy")
    lines.append("- Strengthen the current best harness patterns before introducing novelty.")
    lines.append("- Prefer edits that improve consistency, formatting, retrieval ordering, or guardrail enforcement.")
    lines.append("- Avoid speculative changes unless benchmark evidence already suggests instability.")
    lines.append("- Treat content gaps as secondary diagnostic hints, not primary exploration targets in reinforce mode.")

    return "\n".join(lines)

def save_outputs(
    corpus: str,
    raw_result: Dict[str, Any],
    summary: Dict[str, Any],
    validation: Dict[str, Any]
) -> None:
    corpus_hash = sha256_text(corpus)

    (OUT_DIR / "reinforce.corpus.md").write_text(corpus, encoding="utf-8")
    (OUT_DIR / "reinforce.raw.json").write_text(json.dumps(raw_result, indent=2), encoding="utf-8")
    (OUT_DIR / "reinforce.summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (OUT_DIR / "reinforce.validation.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    (OUT_DIR / "reinforce.meta.json").write_text(
        json.dumps(
            {
                "optimize": "reinforce",
                "requestMode": "question",
                "corpusHash": corpus_hash,
                "workspace": str(WORKSPACE),
            },
            indent=2
        ),
        encoding="utf-8"
    )

    proposer_brief = build_proposer_brief(summary, validation)
    (OUT_DIR / "proposal_brief.reinforce.md").write_text(proposer_brief, encoding="utf-8")

def main():
    corpus = build_reinforce_corpus()

    if len(corpus.split()) < 100:
        raise RuntimeError("Reinforce corpus too small after preprocessing.")

    raw_result = infranodus_graph_and_advice(
        text=corpus,
        request_mode="question",
        include_statements=False,
        include_graph=True,
    )

    summary = extract_summary(raw_result)
    validation = validate_reinforce_graph(summary)

    save_outputs(corpus, raw_result, summary, validation)

    if not validation["passed"]:
        raise RuntimeError(f"Reinforce graph failed validation: {validation['issues']}")

    print("Saved InfraNodus reinforce artifacts:")
    print(f"- {OUT_DIR / 'reinforce.corpus.md'}")
    print(f"- {OUT_DIR / 'reinforce.raw.json'}")
    print(f"- {OUT_DIR / 'reinforce.summary.json'}")
    print(f"- {OUT_DIR / 'reinforce.validation.json'}")
    print(f"- {OUT_DIR / 'proposal_brief.reinforce.md'}")

if __name__ == "__main__":
    main()
```


## How to use it

This script expects a Meta-Harness-style workspace where the current best candidate’s traces and summaries are already stored on disk, which matches the Meta-Harness pattern of giving the proposer filesystem access to prior candidates’ source, traces, and scores. It writes reusable artifacts into `analysis/infranodus/`, so your proposer can read `proposal_brief.reinforce.md` before generating the next harness revision.[^14_3][^14_4][^14_1]

A practical insertion point is:

1. Evaluate candidate and save traces/summaries.[^14_3]
2. Run this reinforce analysis script.[^14_1][^14_2]
3. Add `analysis/infranodus/proposal_brief.reinforce.md` to the proposer’s readable workspace.[^14_3]
4. Instruct the proposer to prefer stabilizing edits that strengthen the current dominant high-performing discourse.[^14_2][^14_3]

## Why reinforce helps

`reinforce` uses top nodes from top clusters, so it is especially useful when you have a reasonably good harness and want the next iteration to consolidate strengths rather than wander into speculative changes. In a Meta-Harness setting, that makes it a good complement to `gaps` and `latent`: use `reinforce` when the benchmark says you are near a good local optimum and want to harden it, use `gaps` when coverage is missing, and use `latent` when the loop appears stuck or too narrow.[^14_1][^14_2][^14_3]
<span style="display:none">[^14_10][^14_11][^14_12][^14_13][^14_14][^14_15][^14_5][^14_6][^14_7][^14_8][^14_9]</span>

<div align="center">⁂</div>

[^14_1]: https://infranodus.com/api/docs

[^14_2]: https://support.noduslabs.com/hc/en-us/articles/13605983537692-InfraNodus-API-Access-Points

[^14_3]: https://yoonholee.com/meta-harness/

[^14_4]: https://arxiv.org/abs/2603.28052

[^14_5]: https://infranodus.com/docs/graph-rag-knowledge-graph

[^14_6]: https://dify.ai/blog/level-up-your-dify-chatbot-integrating-infranodus-for-advanced-q-a-and-idea-generation

[^14_7]: https://infranodus.com/api

[^14_8]: https://infranodus.com/docs/knowledge-graphs-for-llms

[^14_9]: https://support.noduslabs.com/hc/en-us/articles/19602201629596-Prompt-Augmentation-for-LLM-RAG

[^14_10]: https://infranodus.com/extension

[^14_11]: https://infranodus.com/use-case/ai-knowledge-graphs

[^14_12]: https://www.linkedin.com/posts/omarsar_new-stanford-mit-paper-on-model-harnesses-activity-7444733559875100672-rBaK

[^14_13]: https://ryuchen.github.io/essay/0x00000C.files/1-WWW- InfraNodus- Generating Insight Using Text Network Analysis.pdf

[^14_14]: https://infranodus.com/docs/faq

[^14_15]: https://github.com/langchain-ai/deepagents/issues/2589

