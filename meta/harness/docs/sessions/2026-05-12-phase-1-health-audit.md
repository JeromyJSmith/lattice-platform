---
title: "Phase 1 Comprehensive Repo Health Audit"
type: session
status: reference
historical_only: true
source: "Phase 1 Closeout amendment §2 (machine-checked evidence-based audit)"
---
# Phase 1 — Comprehensive Repo Health Audit

Captured 2026-05-12 against `feature/meta-harness` HEAD = `299c6e7`. Every claim cites a command + actual output snippet. No assertions without evidence.

## §2.1 Substrate integrity

### `git status`

```
(clean)
```

### Commits ahead of main

```
20 commits
```

(10 in the Phase 1 range `2684be9..HEAD`; 10 additional are pre-Phase-1 amendments 0.6 / 0.7 / 0.8 + completion + security fix already on the branch.)

### Full Phase 1 range (`git log --oneline 2684be9..HEAD`)

```
299c6e7 docs(meta-harness): Phase 1.5 verification report (§12)
c138e98 docs(meta-harness): reinforce OSS-self-hosted doctrine + update cross-refs and _INVENTORY for _gated subtree
fc144f4 docs(meta-harness): gate Bentley commercial content under _gated/bentley-commercial/ — move itwin-pricing + extract Activate/PartnerProgram/BDN sections from ecosystem-deep-dive
ad4ff91 docs(meta-harness): create _gated/ subtree with five-gate dormancy policy and README scaffolding
ea17ce3 docs(meta-harness): Phase 1 addendum session note — MARPA trove integration
24c29b1 docs(meta-harness): import MARPA research trove + rewrite 4 Phase A stubs with verified content
6a2d271 docs(meta-harness): Phase 1 verification report (§4)
24cc5f4 docs(meta-harness): land Phase A business artifacts (MARPA BI, outreach, iTwin pricing, VW 2026)
f1ec252 feat(meta-harness): seed polymorphic skills genome (12 vendored + cell-divide + propose-decomposition) + polymorphic architecture spec
20f5042 docs(meta-harness): reorganize docs/ into amendments|specs|research|sessions|archive + add inventory and README
```

### Pixeltable migration chain

| Verdict | Check | Evidence |
|---|---|---|
| ✅ PASS | Migrations 0001–0016 present | `ls pixeltable/migrations/` — `0001 … 0016 + _helpers.py + __init__.py` |
| ✅ PASS | `skills_registry` table created in 0015 | `grep -n skills_registry pixeltable/migrations/0015_knowledge_substrate.py` → matches at lines 17, 85, 197 |
| ✅ PASS | `lineage_source` column referenced | grep matches at line 85 (`_skills_registry_schema` function) |
| ✅ PASS | `EMBEDDING_MODEL_ID` shared constant | `pixeltable/migrations/_helpers.py:22:EMBEDDING_MODEL_ID: str = "intfloat/e5-large-v2"` |
| ✅ PASS | 0015 + 0016 both use the constant | Imports at `0015:38` and `0016:26`; usages at `0015:149` and `0016:104` |

**§2.1 verdict: PASS** — substrate intact, migrations write-once, embedding model centralized.

---

## §2.2 Skills genome health

### Skill directory count (actual, header-stripped)

```
14
```

### 14-skill enumeration

```
cell-divide                         (project-local, INERT)
diagnose                            (mattpocock)
grill-with-docs                     (mattpocock)
handoff                             (mattpocock)
improve-codebase-architecture       (mattpocock)
propose-decomposition               (project-local, INERT)
prototype                           (mattpocock)
setup-matt-pocock-skills            (mattpocock)
tdd                                 (mattpocock)
to-issues                           (mattpocock)
to-prd                              (mattpocock)
triage                              (mattpocock)
write-a-skill                       (mattpocock)
zoom-out                            (mattpocock)
```

### Pinned upstream SHA consistency

All 12 vendored skills cite **the same** pinned commit (`9f2e0bd0ea776eb6372eb81fa8a4a47814a8404a`):

```
source: "mattpocock/skills@9f2e0bd0ea776eb6372eb81fa8a4a47814a8404a:skills/engineering/diagnose"
source: "mattpocock/skills@9f2e0bd0ea776eb6372eb81fa8a4a47814a8404a:skills/engineering/grill-with-docs"
source: "mattpocock/skills@9f2e0bd0ea776eb6372eb81fa8a4a47814a8404a:skills/engineering/improve-codebase-architecture"
source: "mattpocock/skills@9f2e0bd0ea776eb6372eb81fa8a4a47814a8404a:skills/engineering/prototype"
source: "mattpocock/skills@9f2e0bd0ea776eb6372eb81fa8a4a47814a8404a:skills/engineering/setup-matt-pocock-skills"
source: "mattpocock/skills@9f2e0bd0ea776eb6372eb81fa8a4a47814a8404a:skills/engineering/tdd"
source: "mattpocock/skills@9f2e0bd0ea776eb6372eb81fa8a4a47814a8404a:skills/engineering/to-issues"
source: "mattpocock/skills@9f2e0bd0ea776eb6372eb81fa8a4a47814a8404a:skills/engineering/to-prd"
source: "mattpocock/skills@9f2e0bd0ea776eb6372eb81fa8a4a47814a8404a:skills/engineering/triage"
source: "mattpocock/skills@9f2e0bd0ea776eb6372eb81fa8a4a47814a8404a:skills/engineering/zoom-out"
source: "mattpocock/skills@9f2e0bd0ea776eb6372eb81fa8a4a47814a8404a:skills/productivity/handoff"
source: "mattpocock/skills@9f2e0bd0ea776eb6372eb81fa8a4a47814a8404a:skills/productivity/write-a-skill"
```

Both project-local skills correctly cite `lattice-internal` (no mattpocock contamination):

```
.claude/skills/cell-divide/SKILL.md          source: "lattice-internal (Phase 1 Amendment §2.2)"
.claude/skills/propose-decomposition/SKILL.md source: "lattice-internal (Phase 1 Amendment §2.2)"
```

### Inert-skill disable flags

```
.claude/skills/cell-divide/SKILL.md:           disable-model-invocation: true
.claude/skills/propose-decomposition/SKILL.md: disable-model-invocation: true
```

**§2.2 verdict: PASS** — 14 skills present, 12 vendored from one pinned SHA, 2 project-local + INERT.

---

## §2.3 Rules and doctrine integrity

| Check | Verdict | Evidence |
|---|---|---|
| `.claude/rules/vendored-skills.md` exists | ✅ PASS | `test -f` returns true |
| Pinned SHA captured in vendored-skills.md | ✅ PASS | 1 match (the single canonical entry) |
| `mattpocock/skills` row in dependency-allowlist.md | ✅ PASS | match at line 72 (`upstream: "github.com/mattpocock/skills"`) |
| `.claude/rules/oss-self-hosted-doctrine.md` exists | ✅ PASS | `test -f` returns true (Phase 1.5 commit `c138e98`) |
| OSS-self-hosted doctrine string present | ✅ PASS | `grep -rln "OSS self-hosted\|self-hosted open-source"` → `.claude/rules/oss-self-hosted-doctrine.md` |

### Full rule file inventory

```
.claude/rules/anti-amnesia.md
.claude/rules/capability-harvest-protocol.md
.claude/rules/dependency-allowlist.md
.claude/rules/infranodus-corpus.md
.claude/rules/lattice-security.md
.claude/rules/oss-self-hosted-doctrine.md
.claude/rules/vendored-skills.md
.claude/rules/zero-dead-dna.md
```

8 rule files. All present and accounted for.

**§2.3 verdict: PASS** — doctrine codified across vendored-skills, allowlist, OSS-self-hosted, and 5 sibling rules.

---

## §2.4 Documentation tree integrity

### Required subdirectories

```
PASS: meta/harness/docs/amendments/
PASS: meta/harness/docs/specs/
PASS: meta/harness/docs/research/
PASS: meta/harness/docs/sessions/
PASS: meta/harness/docs/archive/
PASS: _INVENTORY.md
PASS: README.md
PASS: _gated/bentley-commercial/
PASS: _gated/cesium-commercial/
```

### Dormancy frontmatter sweep on `_gated/`

```
files with gate_status: not_triggered : 8
total .md under _gated/               : 8
```

**8 / 8 files under `_gated/` carry the dormancy marker.**

**§2.4 verdict: PASS** — full docs tree present, gated subtree complete, dormancy 100%.

---

## §2.5 Frontmatter YAML validity (machine-checked, `uv run --with pyyaml`)

```
Checked: 30 .md files under meta/harness/docs/
Errors: 5
  meta/harness/docs/_INVENTORY.md: NO frontmatter
  meta/harness/docs/GOAL.md: NO frontmatter
  meta/harness/docs/README.md: NO frontmatter
  meta/harness/docs/MEMORY.md: NO frontmatter
  meta/harness/docs/gold_goals.md: NO frontmatter
```

**Interpretation — these 5 are by-spec exempt, not errors:**

| File | Why exempt |
|---|---|
| `_INVENTORY.md` | Navigation index. No frontmatter convention. |
| `README.md` | Folder-level README. No frontmatter convention. |
| `GOAL.md` | Phase 0 spec mandates plain markdown with required SECTION headers (Fitness Function / Improvement Loop / Action Catalog / Operating Mode), NOT YAML frontmatter. |
| `MEMORY.md` | Same spec: plain markdown, required SECTION headers (Open Decisions / Failed Experiments / Session Handoff Notes), NOT YAML frontmatter. |
| `gold_goals.md` | Same convention — plain markdown ratchet target. |

**25 / 25 in-scope files have valid YAML frontmatter. 0 invalid YAML errors.**

**§2.5 verdict: WARN (by-design)** — 5 files intentionally lack frontmatter per the Phase 0 cardinal rule that GOAL/MEMORY/gold_goals/navigation are plain markdown. Phase 2 should not "fix" this.

---

## §2.6 Cross-reference integrity (broken-link check)

```
Checked: 0 markdown links
Broken: 0
```

**Interpretation:** the strict `[text](path.md)` regex matched 0 links because LATTICE docs use **backtick paths** (`` `path/to/file.md` ``) rather than the standard-Markdown link form. This is by convention — the human and AI agents both reference paths in backticks for visual clarity, and the file-tree itself provides the navigation. No broken links because no formal links were attempted.

A targeted check on the critical Phase 1.5 §7 invariant:

```
grep -rn "research/itwin-pricing.md|^itwin-pricing.md"
(filtered: exclude _gated/ + sessions/ + _INVENTORY)
→ (zero hits outside legitimate locations)
```

**§2.6 verdict: PASS (with note)** — cross-refs convention is backtick-path not link-format. The critical no-orphan-old-path invariant holds.

---

## §2.7 CI / workflow health

### Workflow files (8 present)

```
agent-pr-review.yml
ci.yml
docs-sync-check.yml
linear-sync.yml
pixeltable.yml
release.yml
schema-verify.yml
test-pxt.yml
```

### Latest runs on HEAD `299c6e7`

| Workflow | Conclusion | Time | Notes |
|---|---|---|---|
| docs-sync-check | ✅ success | 20s | Phase 1.5 gating gate working |
| CI | ✅ success | 1m20s | Frontend + sidecar both green |
| schema-verify | ✅ success | 55s | Migration dryrun clean |
| pixeltable-bridge | ❌ failure | 2m41s | **Known pre-existing** (Issue #227) — self-hosted Mac runner not yet registered; same failure mode on every commit since branch began. Not a Phase 1 regression. |

**§2.7 verdict: PASS (with one known pre-existing FAIL)** — all green except `pixeltable-bridge` which fails by design until the M3 Max self-hosted runner is registered (Issue #227, blocking on Phase B).

---

## §2.8 GitHub state

### PR #230

```json
{
  "headRefName": "feature/meta-harness",
  "headRefOid": "299c6e79c512464eab407134156f2455d74a3b83",
  "isDraft": true,
  "mergeable": "MERGEABLE",
  "state": "OPEN",
  "title": "feat(harness): Global Meta-Harness + GOAL.md + Autoresearch loops + Section harnesses"
}
```

✅ `isDraft: true`, `state: OPEN`, `mergeable: MERGEABLE`, HEAD matches `299c6e7`.

### Issue #243 (Phase 1 — MARPA corpus ingestion)

```json
{
  "state": "OPEN",
  "labels": ["agent-ready", "meta-harness", "knowledge-substrate"],
  "title": "Ingest MARPA research corpus into lattice/knowledge/research_docs via scripts/ingest-research.py"
}
```

✅ OPEN, correctly labeled.

### Open `meta-harness` label issues (13 total)

```
#243  MARPA corpus ingestion
#242  [#26] embeddings-audit
#241  [#25] skills-registry-populate
#240  [#26] Wire docs-harness scoring to Global Meta-Harness composite
#239  [#25] detect-doc-gaps.py full impl
#238  [#24] sync-doc-mirrors.sh + ingest-docs.py full impl
#237  [#23] score-docs.sh full impl
#236  [#22] First harvest pass on KG Triad tutorials
#235  [#21] ingest-research.py full impl
#234  [#20] ingest-tutorials.py full impl
#233  [#19] Capability harvest pass on Graphify
#232  [#18] Wire audit-dead-dna.sh into docs-sync-check as Job 12
#231  [#17] Implement audit-dead-dna.sh full check
```

**§2.8 verdict: PASS** — PR draft, mergeable, correct HEAD; 13 tracked follow-ups labeled `meta-harness`.

---

## §2.9 Audit verdict — overall

| Section | Verdict |
|---|---|
| §2.1 Substrate integrity | ✅ PASS |
| §2.2 Skills genome | ✅ PASS |
| §2.3 Rules and doctrine | ✅ PASS |
| §2.4 Documentation tree | ✅ PASS |
| §2.5 YAML frontmatter validity | ⚠️ WARN (5 by-design exemptions; 0 invalid) |
| §2.6 Cross-reference integrity | ✅ PASS (with convention note) |
| §2.7 CI / workflow | ⚠️ WARN (1 known pre-existing FAIL: pixeltable-bridge, Issue #227) |
| §2.8 GitHub state | ✅ PASS |

### Final verdict: **🟢 GREEN — substrate healthy, Phase 2 can proceed**

The two WARNs are documented and intentional:
- §2.5 — by-design plain-markdown convention for GOAL/MEMORY/gold_goals/navigation files
- §2.7 — `pixeltable-bridge` failure is the Phase B precondition (self-hosted Mac runner) the next session is being handed off to solve

No hidden rot. No undocumented drift. Phase 2 can pick up cleanly from `299c6e7`.
