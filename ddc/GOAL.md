# DDC + CI Infrastructure Harness — LATTICE Meta-Harness Control

Owns DDC mapping (`meta/DDC_MAPPING.md`), GitHub Actions workflows under `.github/workflows/`, CWICR Qdrant integration for cost database, OpenConstructionERP BOQ adapter, 221 DDC skills index.

## Fitness Function

Score DDC health against **CI workflow success**, **DDC skill coverage**, and **ERP data flow**:

1. **CI workflow pass rate**: all 6 workflows in `.github/workflows/` pass on main (docs-sync-check, lint, test-api, test-frontend, test-georef, test-genai)
2. **No warning escape hatches**: zero `|| true` or `set +e` in CI config outside documented temporary exceptions
3. **DDC skill index**: `meta/DDC_MAPPING.md` lists 221 skills with mappings to Qdrant nodes; count matches actual index size
4. **BOQ adapter**: every IFC element row has `erp_item_id` after BOQ ingest pass; `lattice/execution/boq_items` table populated with cost + schedule data
5. **Cost database health**: Qdrant at `localhost:6333` responds to `/health`; no orphaned skill nodes
6. **No forbidden strings**: CI config files clean of hardcoded secrets, bare AWS keys, or unescaped regex patterns (verified by docs-sync-check)

**Baseline score**: `scripts/score-ddc.sh` runs in < 10s, outputs JSON with `ci_pass_rate`, `ddc_skill_count`, `boq_coverage`, `cost_db_health`.

## Improvement Loop

Autoresearch loop (on every CI failure or new DDC skill):

1. Run `scripts/score-ddc.sh` → baseline snapshot
2. Auto-read `.github/workflows/` directory, check each workflow for exit code handling + proper logging
3. Spawn `claude -p` subprocess to audit CI output, flag warnings, suggest remediation (replace `|| true` with proper error handling, add retry logic, etc.)
4. Auto-read `meta/DDC_MAPPING.md`, verify skill count matches Qdrant index; reindex if drift detected
5. Write CI audit + skill reindex report to `runtime-runs/<run-id>/ddc-ci-audit.md`
6. If all CI workflows pass and skill count matches, commit; else hold + escalate to ops
7. Flock concurrency: max 1 CI audit job at a time via `/tmp/vwbridge-ddc.lock`

## Action Catalog

- **CI health**: `gh workflow list --all` shows all workflows; `gh run list --limit 10` shows recent runs (query status via API)
- **Docs-sync check**: `bash scripts/pre-commit-docs-check.sh` local validation (runs pre-commit)
- **Qdrant health**: `curl -s http://localhost:6333/health | jq .` should return `{"status":"ok"}`
- **DDC skill count**: `grep -c "^- id:" meta/DDC_MAPPING.md` should equal Qdrant `/collections/ddc-skills/points` count
- **BOQ coverage**: `pixeltable select count(*) from lattice.bridge.ifc_elements where erp_item_id is null` should be 0 after BOQ pass
- **CI logs**: `gh run view <run-id> --log` retrieves full job output for debugging

## Operating Mode

- **CI trigger**: push to feature branch → docs-sync-check runs first (gates other workflows); all 6 workflows run in parallel
- **Docs-sync-check**: validates migration counts, endpoint counts, forbidden strings, section headers (fail if any drift detected)
- **Qdrant integration**: DDC skills indexed as vectors in `ddc-skills` collection; cost database stored in `cost-items` collection; query via semantic similarity
- **BOQ adapter**: OpenConstructionERP API → fetch BOQ items → assign `erp_item_id` to `lattice/bridge/ifc_elements` rows → compute cost rollup
- **Failure mode**: CI workflow fails → PR blocked; docs-sync mismatch → merge blocked (MANDATORY); Qdrant offline → BOQ adapter stalled; cost data missing → financial reporting broken
