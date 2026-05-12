<!-- spec-verified: linear.app/docs + code.claude.com/docs + docs.github.com 2026-05-11 -->
# Phase C — Linear + GitHub Bi-Directional Sync Amendment

**Amendment number:** 10 (follows 01–09 Polymorphic Architecture)
**Branch:** `feature/phase-c-linear` (branched off `feature/meta-harness`)
**Status:** In Progress
**Target:** 2026-05-30
**Authored by:** Claude Code (claude/ lane)

---

## Purpose

Phase C wires the planning brain (Linear) to the code brain (GitHub) so that
every agent, every PR, and every commit is traceable to a Linear issue, a
milestone, and an agent lane. This amendment documents the decisions made,
the files delivered, and the steps remaining for human execution.

Phase C does NOT start Phase B (M3 Max bootstrap). Phase B remains gated on
this branch landing and the human go/no-go decision per cardinal rule 23.

---

## Strategic principles applied

1. **One source of truth per concern.** GitHub = code state. Linear = planning.
   No field syncs in both directions simultaneously. Conflict resolution is
   explicit and documented (see `meta/sync-contract.md §4`).

2. **All operational scripts live in the repo.** No local-only scripts.
   `scripts/linear-reconciliation.py` is checked in with `--dry-run` default.

3. **Agents need a contract, not a free-for-all.** `meta/agent-lanes.md`
   defines 5 lanes + human-only, each with allowed file paths, branch prefix,
   and Linear label.

4. **Phase C ≠ Phase B.** Phase C ends when Linear is the planning brain,
   GitHub is the code brain, and they talk fluently. It does not execute
   Phase B M3 Max bootstrap.

---

## Team structure (G1 decision — revised 2026-05-12)

| Linear team | Key | Scope | Status |
|---|---|---|---|
| **MARPA** | MARPA | All work — platform (Phases A–N) + engagement (O–P) | **Active** — free plan blocked creating LATTICE |
| **LATTICE** | LAT | Platform engineering (Phases A–N) | **Blocked** — free plan team limit; create when plan upgrades |

**Revised G1:** The original G1 plan split LATTICE (platform) and MARPA (engagement). Linear's free plan caps team count; creating LATTICE returned `403 FORBIDDEN`. All 242 GitHub issues were imported into the existing MARPA team, giving them `MARPA-XX` identifiers. When the workspace upgrades or gains a free team slot, a `--rename-prefix` pass through the reconciliation script will migrate `MARPA-XX` → `LAT-XX` for platform issues.

**Free-plan import status (2026-05-12):**
- 94 issues imported (previous runs, `MARPA-1` through `MARPA-209`)
- 30 issues imported in final run (`MARPA-210` through `MARPA-212` range)
- **126 issues blocked** by Linear's `activeIssueCount` limit (GH #87–#310)
- Resolution: close/archive existing completed MARPA issues to free slots, then re-run:
  ```bash
  LINEAR_API_KEY=lin_api_… \
    uv run python scripts/linear-bootstrap.py \
    --commit --team-key MARPA \
    --project-id ed0921d9-09d1-4ade-8d3e-2794c29fe745 \
    --skip-setup
  ```
  The script is idempotent — already-imported issues are detected via `github_issue_id:` in description and skipped.

---

## Files delivered on `feature/phase-c-linear`

| File | Type | Purpose |
|---|---|---|
| `meta/sync-contract.md` | New | Canonical field-direction table, Magic Words, branch convention, conflict policy |
| `meta/agent-lanes.md` | New | 5 agent lanes + human-only: scopes, prefixes, prohibited zones, quality gates |
| `.github/PULL_REQUEST_TEMPLATE.md` | Extended | Added Linear + Agent Lane header, updated LATTICE Area checklist with phase labels, added agent quality checklist |
| `scripts/agent-context-regenerate.sh` | New | Idempotent regeneration of `.github/agent-context.md` from repo state |
| `scripts/linear-reconciliation.py` | New | Stage 5b reconciliation script; `--dry-run` default; CSV output to `meta/harness/docs/sessions/` |
| `scripts/linear-notify-commit.sh` | New | SHA-tracking post-commit hook; posts Linear comment for LAT/MAR refs |
| `.github/workflows/linear-sync-check.yml` | New | PR title + branch prefix validation CI job |
| `.claude/settings.json` | Extended | Added `linear-notify-commit.sh` as PostToolUse/Bash hook |
| `meta/harness/PLAN/10-PHASE-C-LINEAR-AMENDMENT.md` | New | This file |

---

## Milestone structure (approved — 17 total)

Phase naming: lettered (A–P), replacing the prior Phase 1 / Phase 1.5 / Phase B numbering.

| ID | Name | Target | Status |
|---|---|---|---|
| Phase A | Foundation (was "Phase 1") | Complete | ✅ |
| Phase A.5 | Doctrine (was "Phase 1.5") | 2026-05-20 | Substance complete on `feature/meta-harness`; reaches `main` via PR #230 |
| Phase B | M3 Max Bootstrap | 2026-06-15 | Not started; gated on cardinal rule 23 |
| Phase C | Project Infrastructure (this) | 2026-05-30 | In Progress |
| Phase D | VW Bridge | 2026-07-31 | Not started |
| Phase E | iTwin OSS Self-Hosted | 2026-09-15 | Not started |
| Phase F | 3D Viewer (Context A) | 2026-09-30 | Not started |
| Phase G | Analytics Layer (Context B) | 2026-10-15 | Not started |
| Phase H | Plant Geometry LOD Pipeline | 2026-11-01 | Not started |
| Phase I | Point Cloud | 2026-11-15 | Not started |
| Phase J | Agent Runtime | 2026-12-01 | Not started |
| Phase K | Cesium 3D Tiles + Reality Capture | 2026-12-15 | Not started |
| Phase L | Production Hardening | 2026-12-31 | Not started |
| Phase M | DDC Skills Library Integration | 2026-09-30 | Not started (parallel with F/G) |
| Phase N | Knowledge Substrate Production Ops | 2026-08-15 | Not started (post-Phase-B) |
| Phase O | Outreach + Partnership Execution | Rolling — gate-triggered | Not started |
| Phase P | MARPA Pilot Execution | Rolling — starts when Phase D ingest is end-to-end | Not started |

---

## Sync contract summary (see `meta/sync-contract.md` for full detail)

- **GitHub = source of truth** for: PR status, CI checks, commit refs, branch state.
- **Linear = source of truth** for: priority, cycle, estimate, milestone, parent/child, customer, agent assignment.
- **Title/description:** bidirectional; conflict → Slack `#lattice-sync` alert, no auto-resolve.
- **Magic Words:** `Fixes LAT-XX`, `Closes LAT-XX`, `Resolves LAT-XX` (close); `Refs LAT-XX`, `Part of LAT-XX` (keep open).
- **Linear ID is canonical everywhere.** GitHub issue numbers are metadata only (Linear custom field `github_issue_id`).

---

## Steps remaining for human execution (Stages 3, 4, 5a)

These steps require browser access with your Linear OAuth token. Claude Code
cannot execute them.

### Stage 3 — Configure Linear ↔ GitHub integration

In **Linear → Settings → Integrations → GitHub**:
1. Connect `JeromyJSmith/lattice-platform` to the MARPA workspace.
2. Create **LATTICE team** (key: `LAT`) for platform work. Keep MARPA for Phase O–P.
3. Enable: auto-link PRs/branches/commits, auto-update issue status from PR state, sync issue labels bidirectionally, sync comments bidirectionally, auto-close on merge via Magic Words.
4. Set default Linear project for new GitHub issues = Lattice.
5. Map GitHub labels → Linear labels per `meta/sync-contract.md §Label taxonomy`.
6. Enable webhook events: `issues`, `issue_comment`, `pull_request`, `pull_request_review`, `pull_request_review_comment`, `push`, `status`, `check_suite`, `check_run`, `release`, `deployment`.
7. Copy the webhook URL and add it as a GitHub secret: `gh secret set LINEAR_WEBHOOK_URL --body "<url>"`.
8. Add `LINEAR_API_KEY` as a GitHub secret for the reconciliation script.

### Stage 4 — Build Linear project shell

In **Linear → Projects → New → Lattice**:

- Icon + color + lead = you
- Status: Planned
- Summary: "AI-native AEC digital twin for landscape architecture. Vectorworks → IFC4.3 → iTwin OSS → deck.gl + Cesium 3D Tiles → Pixeltable knowledge substrate. Claude CLI runtime."
- Description: see `meta/ARCHITECTURE.md` executive summary
- Start: 2026-05-11 · Target: 2026-12-31
- Resources: link GitHub repo, `meta/sync-contract.md`, `meta/agent-lanes.md`, `meta/ARCHITECTURE.md`, `AGENTS.md`, `.github/copilot-instructions.md`
- Create the 17 milestones from the table above with their target dates

### Stage 5a — Bulk import 242 GitHub issues

**Linear → Settings → Import & Export → GitHub:**
1. Select repo `JeromyJSmith/lattice-platform`
2. Target team: **LATTICE**
3. Target project: **Lattice**
4. Run import (5–15 min)

After import, run the reconciliation script:
```bash
LINEAR_API_KEY=lin_api_… \
  uv run python scripts/linear-reconciliation.py --dry-run
# Review meta/harness/docs/sessions/<date>-linear-import-reconciliation.md
# Then:
LINEAR_API_KEY=lin_api_… GITHUB_TOKEN=ghp_… \
  uv run python scripts/linear-reconciliation.py --commit
```

### Stage 6 — Verify and enable branch protection (G2 decision)

After `linear-sync-check.yml` is live on `feature/meta-harness`:

In **GitHub → Settings → Branches → Add rule → `feature/meta-harness`**:
- ☑ Require a pull request before merging
- ☑ Require status checks: `docs-sync-check` + `linear-id-check` + `agent-lane-check`
- ☑ Require branches to be up to date before merging
- ☑ Do not allow bypassing the above settings

---

## What Phase C does NOT do

- Does not start Phase B M3 Max bootstrap.
- Does not merge this branch to `main` (that happens when `feature/meta-harness` merges via PR #230, post-Phase-B gate).
- Does not create Linear Cycles (those are created at the start of each active milestone).
- Does not wire Slack per-milestone channels (that is Stage 7b — Linear Asks / Slack routing — added as a Phase C follow-up issue).

---

## Doctrine (inherited from 00-OVERVIEW.md)

1. No file written from memory. Every system file is spec-verified.
2. Branch first, write second.
3. Plan before code. This artifact is the plan; implementation is the files above.
4. Specs override the original prompt.
5. Reversibility: deleting this branch reverts all Phase C changes.
