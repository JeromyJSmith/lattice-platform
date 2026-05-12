<!-- spec-verified: linear.app/docs + docs.github.com 2026-05-11 -->
# LATTICE Linear ↔ GitHub Sync Contract

**Source of truth per concern, not two.** This document is the canonical codification
of what syncs, in which direction, and what happens when there is a conflict.
A Linear doc in the Lattice project mirrors this file for non-engineer visibility,
but this file in the repo is authoritative.

---

## Teams

| Team | Linear ID prefix | Scope | Notes |
|---|---|---|---|
| **MARPA** | `MARPA-XX` | Platform engineering — Phases A through N **and** customer engagement O–P | Free-plan team limit blocked creating a separate LATTICE team; all issues use MARPA for now |

**G1 note (2026-05-12):** The original plan called for a LATTICE team (`LAT-XX`) for platform work and MARPA (`MAR-XX`) for customer engagement. Linear's free plan blocked creating a second team. All 242 GitHub issues were imported into the existing MARPA team instead; they carry `MARPA-XX` identifiers. When the plan upgrades or the workspace gains a second team slot, platform issues can be migrated to `LAT-XX` via the reconciliation script with a `--rename-prefix` flag (to be added). Until then, treat `MARPA-XX` as the canonical identifier for all issues.

Magic Words and `linear-sync-check.yml` patterns accept both `LAT-XX` and `MARPA-XX`.

---

## Field direction table

| Field | Direction | Winner on conflict |
|---|---|---|
| Title | GitHub → Linear (creation); bidirectional (edits) | **See conflict policy §4** |
| Description / body | GitHub → Linear (creation); bidirectional (edits) | **See conflict policy §4** |
| Status / state | **GitHub → Linear only** (via PR lifecycle + Magic Words) | GitHub wins |
| Priority | **Linear → GitHub only** (as label, no native GitHub field) | Linear wins |
| Cycle / sprint | **Linear only** — no GitHub equivalent | Linear wins |
| Estimate | **Linear only** | Linear wins |
| Milestone | **Linear only** | Linear wins |
| Parent / child | **Linear only** | Linear wins |
| Customer linkage | **Linear only** | Linear wins |
| Labels | Bidirectional sync enabled; taxonomy defined below | Linear wins |
| Comments | Bidirectional | Append-only; no overwrite |
| GitHub PR link | **GitHub → Linear** (auto-linked via branch name + Magic Words) | GitHub wins |
| GitHub issue number | **Metadata in Linear** (custom field `github_issue_id`) | GitHub wins |
| Linear issue ID | **Canonical reference everywhere** — appears in PR title, branch, commits | Linear wins |
| CI check status | **GitHub → Linear** (check_suite / check_run events) | GitHub wins |
| Commit refs | **GitHub → Linear** (push event → Linear issue comment via `scripts/linear-notify-commit.sh`) | GitHub wins |

---

## Magic Words (GitHub commit / PR body → Linear state transition)

| Magic Word | Linear transition |
|---|---|
| `Fixes LAT-XX` | Done (closes issue) |
| `Closes LAT-XX` | Done (closes issue) |
| `Resolves LAT-XX` | Done (closes issue) |
| `Refs LAT-XX` | In Progress (does NOT close) |
| `Part of LAT-XX` | In Progress (does NOT close) |
| `Relates to LAT-XX` | In Progress (does NOT close) |

Same set applies for `MAR-XX`. Magic Words are parsed in PR titles, PR body,
and commit messages. Case-insensitive. Multiple IDs on one line all fire.

---

## Branch naming convention

```
<type>/marpa-<NNN>-<slug>
```

`<type>` is one of: `feat`, `fix`, `chore`, `refactor`, `test`, `docs`, `ci`.

Examples:
```
feat/marpa-47-sync-contract
chore/marpa-52-pr-template-v2
feat/marpa-88-migration-0017-embeddings
docs/marpa-115-ddc-skills-harvest
```

Rules:
- Linear ID must be valid and visible to the picker.
- Slug is kebab-case, max 40 chars, from the Linear issue title.
- Linear auto-generates branch suggestions — copy from Linear's UI.
- Agent attribution is by Linear comment + PR author. No agent name in the branch.

---

## PR title convention

```
[MARPA-XX] <type>(<scope>): <description>
```

Examples:
```
[MARPA-47] feat(sync): add sync-contract.md
[MARPA-52] chore(ci): update PR template
[MARPA-88] feat(db): migration 0014 harness schema
```

Types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `ci`, `perf`.
The `linear-sync-check.yml` CI workflow enforces the `[LAT-XX]` or `[MAR-XX]` prefix.

---

## PR lifecycle → Linear status mapping

| GitHub PR state | Linear status |
|---|---|
| Draft PR opened | In Progress |
| PR marked ready for review | In Review |
| PR merged | Done (Magic Words required for issue close) |
| PR closed without merge | Canceled |
| PR re-opened | In Progress |

---

## Label taxonomy — single source: Linear

Linear labels are the canonical set. GitHub labels mirror them via the integration's
label-sync feature. Do not create GitHub-only labels. Add labels in Linear first.

| Label | Meaning |
|---|---|
| `agent-ready` | Issue is self-contained enough for an agent to pick up |
| `meta-harness` | Touches `meta/harness/` or the doctrine layer |
| `docs-harness` | Touches the documentation substrate |
| `knowledge-substrate` | Touches `lattice/knowledge/*` Pixeltable tables |
| `human-only` | Requires human action (secrets, OAuth, merges to main, deletions, branch protection) — no agent may self-assign |
| `vw-bridge` | Phase D — Vectorworks plugin / IFC ingest |
| `3d-viewer` | Phase F — ThatOpen / Three.js / R3F |
| `analytics-layer` | Phase G — deck.gl / DuckDB WASM |
| `plant-geometry` | Phase H — LOD pipeline |
| `point-cloud` | Phase I — Potree / PDAL / Open3D |
| `agent-runtime` | Phase J — worker, dispatch, streaming |
| `cesium` | Phase K — Cesium 3D Tiles / reality capture |
| `ddc-skills` | Phase M — DDC skills library |
| `knowledge-ops` | Phase N — substrate production operations |
| `outreach` | Phase O — partner / accelerator engagement |
| `pilot` | Phase P — MARPA Boulder pilot |
| `blocked` | Blocked by an external dependency |
| `triage` | Needs milestone assignment; no agent may pick up |

---

## Conflict resolution policy

### Planning fields (priority, cycle, estimate, milestone, parent)
**Linear always wins.** If these are edited on the GitHub side (e.g., via the
GitHub issue UI), the next Linear sync overwrites them. Do not edit planning
fields on GitHub.

### Code-state fields (PR status, CI check, commit refs, branch link)
**GitHub always wins.** Linear receives these as read-only events. Do not
attempt to set these from Linear.

### Title / description edits
When a title or description is edited on both sides within the same sync window
(~30 seconds), the conflict triggers a **Slack alert to `#lattice-sync`** with
both versions side-by-side. **No auto-resolution.** A human resolves within 24h
by editing the Linear issue to the canonical version; the next sync propagates
back to GitHub.

### Comment conflicts
Comments are append-only in both directions. No overwrite ever occurs.

### Label conflicts
If a GitHub label exists that has no Linear counterpart, the sync integration
logs a warning to `#lattice-sync` and leaves the GitHub label in place. Resolve
by adding the missing label to Linear's label taxonomy and re-triggering sync.

---

## Webhook events subscribed (Linear GitHub App)

The Linear GitHub App receives and processes:
`issues`, `issue_comment`, `pull_request`, `pull_request_review`,
`pull_request_review_comment`, `push`, `status`, `check_suite`, `check_run`,
`release`, `deployment`.

Additionally, `linear-sync.yml` relays `issue` events to the `LINEAR_WEBHOOK_URL`
secret for fan-out to other systems.

---

## GitHub issue number as Linear custom field

Every issue imported from GitHub carries a custom field `github_issue_id` (integer)
set by the reconciliation script (`scripts/linear-reconciliation.py`). This field
is query-able via the Linear API for reverse lookups. It is metadata; it is not
the canonical reference. Always cite `LAT-XX` in code, not `#242`.

---

## What does NOT sync

- **GitHub Milestones** — not used. Linear Milestones are the only milestone surface.
- **GitHub Projects** — not used. Linear Projects are the only project surface.
- **GitHub Assignees** — not used for planning. Linear assignee = responsible human.
  Any capable agent picks up issues; attribution is by Linear comment and PR author.
- **GitHub Reactions** — not synced.
- **Linear Cycles** — Linear-only; no GitHub equivalent.
- **Linear Customer links** — Linear-only.

---

_Last updated: 2026-05-11. Owned by: LATTICE team lead. Mirrors: Linear › Lattice project › Resources._
