# DDC + CI Infrastructure Harness — Session Memory

## Open Decisions

1. **Qdrant remote vs local**: should we run Qdrant in production (OrbStack VM on Mac, or remote cloud), or keep it ephemeral for dev? Current: local OrbStack. May move to remote for multi-region cost analysis.
2. **DDC skill granularity**: are 221 skills the right count, or should we consolidate similar skills? Current count includes manual + auto-extracted. May implement skill clustering to reduce duplication.
3. **BOQ item reconciliation**: if a plant species is not found in ERP database, should we create a placeholder cost entry or reject the element? Current: create placeholder with cost=0 + flag for human review.

## Failed Experiments

- (placeholder — no failed experiments logged yet for this section)

## Session Handoff Notes

**Current state (2026-05-13)**: 6 CI workflows scaffolded (.github/workflows/). Docs-sync-check passing (verifies migrations 0001–0013, endpoints 33, forbidden strings, section headers). Qdrant health check integrated into `/v1/health/*`. DDC mapping table at 221 skills (manual + auto-extracted). BOQ adapter skeleton in `pixeltable/service/routes/erp.py` (stub-501, not yet wired to OpenConstructionERP API).

**Known issues**:
- OpenConstructionERP API credentials not yet configured (placeholder env vars in `.env.example`)
- Qdrant reindexing on skill drift not yet automated (manual `python ddc/reindex_qdrant.py` for now)
- CI workflow retry logic minimal (max 1 retry; may increase to 3)
- Cost rollup logic (aggregate plant costs per zone, per project) not yet implemented

**Ready for next agent**: CI surface frozen. Docs-sync-check stable and enforced. Qdrant integration ready for performance testing. BOQ adapter ready for OpenConstructionERP integration. DDC skill index ready for clustering experiment. Next: wire ERP API credentials, implement cost rollup, test multi-workflow concurrency.
