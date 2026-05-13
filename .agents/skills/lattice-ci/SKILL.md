---
description: Author and maintain GitHub Actions CI workflows, enforce the docs-sync-check gate, validate forbidden-string allowlists, and keep all 6 workflows passing on main.
---

# LATTICE CI Workflow Authoring and docs-sync Enforcement

The ci section owns all GitHub Actions workflows under `.github/workflows/` and the
local pre-commit validation script `scripts/pre-commit-docs-check.sh`. The
docs-sync-check workflow is the gate that runs first and blocks all other workflows
on any docs drift, forbidden string, or migration count mismatch. The scoring script
`scripts/score-ddc.sh` includes CI pass rate as a sub-metric.

## When this skill applies

- Adding or modifying any `.github/workflows/*.yml` file
- A CI workflow fails on main and needs diagnosis
- The docs-sync-check allowlist needs updating (new docs file legitimately contains
  a term that would otherwise be flagged as forbidden)
- Running `bash scripts/pre-commit-docs-check.sh` and fixing failures locally
- Regex escaping issues in workflow grep patterns (a known failure mode)
- A merge is blocked by docs-sync and the source of drift must be identified

## How it works

1. Run the docs-sync check locally first:
   ```bash
   bash scripts/pre-commit-docs-check.sh
   ```
   Exit 0 means all checks pass. Exit non-zero shows which check failed.

2. Check which CI workflows exist and their recent status:
   ```bash
   gh workflow list --all
   gh run list --limit 10
   ```

3. View full job output for a failed run:
   ```bash
   gh run view <run-id> --log
   ```

4. The docs-sync-check validates:
   - Migration counts consistent across `meta/SCHEMA.md`, `meta/ARCHITECTURE.md`,
     and `AGENTS.md` LIVE STATE block.
   - Endpoint counts consistent across `meta/API.md` and `meta/ARCHITECTURE.md`.
   - All 4 mandatory rules present in `AGENTS.md`.
   - Required section headers present in `meta/FEATURE_BACKLOG.md`.
   - No forbidden strings in non-allowlisted files:
     `Revit`, `MicroStation`, `@itwin/core-backend`, `pxt.Geometry`, # allow-forbidden
     `pixeltable/service/migrations`, bare `import Anthropic` in `.ts`/`.tsx`. # allow-forbidden

5. Fix a forbidden-string false positive by adding the file to the allowlist in
   `.github/workflows/docs-sync-check.yml`. Allowlist entries use exact filename
   patterns. Regex must be shell-escaped — use `\\.` not `.` in grep patterns.

6. Fix a migration count mismatch:
   - Find the canonical count: `ls pixeltable/migrations/0*.py | wc -l`
   - Update `meta/SCHEMA.md`, `meta/ARCHITECTURE.md`, and `AGENTS.md` LIVE STATE
     to match in the same commit.

7. Fix an endpoint count mismatch:
   - Count live: `git grep -h "^@\(app\|router\)\." -- pixeltable/service/ | wc -l`
   - Update `meta/API.md` and `meta/ARCHITECTURE.md` to match.

8. When authoring a new workflow:
   - Never use `|| true` or `set +e` except in explicitly documented temporary
     exceptions with an expiry comment.
   - Never hardcode secrets, AWS keys, or API tokens — use `${{ secrets.* }}` only.
   - Ensure the workflow name matches a valid trigger in the push/PR event filter.
   - All workflows must exit non-zero on failure; no silent swallowing of errors.

## Files used

- `.github/workflows/docs-sync-check.yml` — mandatory gate workflow
- `.github/workflows/lint.yml`, `test-api.yml`, `test-frontend.yml`,
  `test-georef.yml`, `test-genai.yml` — parallel test workflows
- `scripts/pre-commit-docs-check.sh` — local mirror of docs-sync-check logic
- `meta/SCHEMA.md` — migration count source of truth for CI check
- `meta/API.md` — endpoint count source of truth for CI check
- `meta/ARCHITECTURE.md` — must match both counts
- `AGENTS.md` (repo root) — LIVE STATE block, mandatory rules checked by CI
- `meta/FEATURE_BACKLOG.md` — required section headers checked by CI
- `scripts/score-ddc.sh` — ddc scoring script (includes CI pass rate)

## Constraints

- The docs-sync-check workflow must run before all other workflows. It is the merge
  gate; PRs with docs drift cannot merge.
- Zero `|| true` or `set +e` in CI config outside documented temporary exceptions.
  Every documented exception must have an expiry comment.
- Never hardcode credentials in workflow files. Use `${{ secrets.* }}` exclusively.
- Regex patterns in grep calls within workflow YAML must be properly shell-escaped.
  The known failure mode is unescaped `.` in regex — use `\\.` in patterns that
  match literal dots (e.g., file extensions).
- The allowlist for forbidden-string checks must be exact filename patterns, not
  directory globs, to avoid accidentally allowing new files.
- This skill owns CI workflow files and the pre-commit check script. DDC data
  integration and Qdrant live in the `lattice-ddc` skill.
