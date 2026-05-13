# InfraNodus Skills Master Audit

Date: 2026-05-13
Source path: `.claude/skills/skills-master/`
Status: source audit, no activation changes

This audit reviews the local InfraNodus skills bundle currently present under
`.claude/skills/skills-master/`. The folder appears to be a vendored copy of the
InfraNodus Claude skills repository plus local InfraNodus MCP docs. It should be
treated as a source corpus for capability research until we decide which skills,
if any, should become active LATTICE skills or harness-proven capabilities.

## What Is In The Folder

| Path | Purpose |
|---|---|
| `.claude/skills/skills-master/README.md` | Overview of the InfraNodus skills collection and installation model |
| `.claude/skills/skills-master/infranodus-cli/SKILL.md` | Direct InfraNodus MCP/tool-use reference skill |
| `.claude/skills/skills-master/infranodus-cli/references/tool-examples.md` | Condensed MCP tool examples |
| `.claude/skills/skills-master/infranodus-tools.md` | Full InfraNodus MCP tool reference copy |
| `.claude/skills/skills-master/infranodus-mcp-deploy-claude-code.txt` | Claude Code MCP setup reference copy |
| `.claude/skills/skills-master/skill-*/SKILL.md` | Individual InfraNodus-adjacent skills |

No license file was found in the local folder. The deployment reference notes
that some InfraNodus open-source tooling is AGPL. Treat this folder as vendored
reference material until license provenance is clarified.

## Skill Inventory

| Skill | LATTICE relevance | Notes |
|---|---|---|
| `infranodus` | High | Direct reference for MCP tools, parameters, input shapes, and examples |
| `ontology-generator` | High | Useful for schema vocabulary, BIS/DDC/VW ontology extraction, and `lattice/knowledge/*` design |
| `shifting-perspective` | High | Good fit for gap analysis over capability docs and research corpus |
| `critical-perspective` | Medium | Useful as a review lens for assumptions and blind spots |
| `cognitive-variability` | Medium | Useful as a conceptual framework for diagnosing biased/focused/diversified/dispersed docs |
| `llm-wiki` | Medium | Useful pattern for persistent research wiki design, but too broad to adopt wholesale |
| `actionize` | Medium | Useful for turning InfraNodus gap findings into P0/P1/P2 plans; Telegram/cron parts are not in scope |
| `rhetorical-analyst` | Low/medium | Useful pattern for analyzing arguments, not directly core to capability mapping |
| `writing-assistant` | Low/medium | Useful only for prose cleanup and structural signals |
| `seo-analysis` | Low | Mostly public content/SEO; not a core LATTICE workflow |
| `youtube-viral-optimizer` | Low | Not relevant to current LATTICE architecture, except as an example of graph-to-script workflow |
| `shopping-assistant` | Low | Not relevant to LATTICE |
| `perspective-reversal` | Low | Not relevant to core repo work |
| `embodied-navigation` | Low | Interesting but not a capability-mapping priority |
| `vipassana-llm` | Low | Personal/cognitive workflow, not core LATTICE architecture |

## Immediate Candidates

### 1. `infranodus-cli`

Use this as the canonical local reference for InfraNodus MCP invocation. It
summarizes:

- `generate_knowledge_graph`
- `create_knowledge_graph`
- `analyze_text`
- `generate_topical_clusters`
- `generate_content_gaps`
- `generate_contextual_hint`
- `generate_research_questions`
- `generate_research_ideas`
- `develop_text_tool`
- `develop_latent_topics`
- `develop_conceptual_bridges`
- `optimize_text_structure`
- memory, retrieval, comparison, and SEO tools

LATTICE fit:

```text
curated docs -> InfraNodus gap analysis -> gap report -> harness evidence
```

### 2. `ontology-generator`

This is a strong fit for the schema-vocabulary phase. Its wikilink relation
format can help generate candidate vocabularies before migration `0017`.

Potential use:

```text
BIS/DDC/VW/ODBC terms
-> [[entity]] relation [[entity]] [relationCode]
-> InfraNodus graph
-> schema vocabulary candidates
-> future lattice/knowledge/schema_vocabulary rows
```

Do not treat generated ontologies as schema truth. They are design input only
until verified against source docs and code.

### 3. `shifting-perspective`

This is the best skill for the first gap-analysis run because it has a clear
workflow:

```text
optimize_text_structure
-> diversity score
-> content gaps
-> latent topics
-> perspective shift
-> next actions
```

LATTICE can adapt this into a deterministic report shape:

```text
documentation gap
proof gap
schema gap
tooling gap
operator workflow gap
```

### 4. `actionize`

Useful after the gap-analysis report exists. It should not be adopted wholesale
because its `.plan/`, Telegram, and cron behavior do not match the current repo
guardrails. The valuable part is the conversion of loose research into a
scheduled P0/P1/P2 task plan.

## Not Ready For Activation

Do not copy these skills into the active LATTICE skill surface yet. Reasons:

1. The folder is untracked and may be a raw vendored source copy.
2. License provenance is not clear from the local folder.
3. Several skills are irrelevant to LATTICE and would add noise.
4. Some skills assume tools like `MCPorter`, `AskUserQuestion`, `CronCreate`,
   or Telegram reminders that are not part of the current harness path.
5. The current LATTICE need is a narrow InfraNodus gap-analysis proof, not a
   broad skill-system import.

## Recommended Mapping

| LATTICE need | Use from skills-master | Current action |
|---|---|---|
| Understand InfraNodus tools | `infranodus-cli` and `tool-examples.md` | Reference in runbook |
| Create schema/capability vocabulary | `ontology-generator` | Make future contract-only row |
| Find conceptual and organization gaps | `shifting-perspective` | Use in first InfraNodus run prompt |
| Pressure-test assumptions | `critical-perspective`, `cognitive-variability` | Optional analysis lenses |
| Convert gaps to plan | `actionize` | Borrow P0/P1/P2 structure only |

## Proposed Future Registry Rows

Do not add these rows until we are ready to reconcile the existing
`infranodus-capability-registry.yaml`.

Candidate rows:

| Candidate id | Source | Proof shape |
|---|---|---|
| `infranodus-skills-cli-reference` | `infranodus-cli/SKILL.md` | Verify one curated-doc gap analysis uses the documented tool sequence |
| `infranodus-ontology-generator-reference` | `skill-ontology-creator/SKILL.md` | Generate a small BIS/DDC/VW ontology from fixture terms and verify relation syntax |
| `infranodus-shifting-perspective-gap-pass` | `skill-shifting-perspective/SKILL.md` | Produce documentation/proof/schema/tooling/operator gap report from curated corpus |
| `infranodus-actionize-gap-plan-pattern` | `skill-actionize/SKILL.md` | Convert gap report into P0/P1/P2 plan without writing `.plan/` or creating reminders |

## Where It Fits

Current source:

```text
.claude/skills/skills-master/
```

Current audit:

```text
meta/capability-research/tools/infranodus-skills-master-audit.md
```

Future allowed outputs:

```text
meta/capability-research/tools/infranodus-gap-analysis-YYYY-MM-DD.md
meta/capability-research/inventory/infranodus-gap-analysis-YYYY-MM-DD.json
meta/harness/docs/sessions/YYYY-MM-DD-infranodus-proof.md
```

Future durable schema candidate:

```text
lattice/knowledge/source_artifacts
lattice/knowledge/schema_vocabulary
lattice/knowledge/harvested_capabilities
```

No migration should be written for this yet.
