# Frontend Harness — Session Memory

## Open Decisions

1. **Context A vs B separation**: are we enforcing route-level separation (e.g., `/viewer` always uses ThatOpen, `/analysis` always uses deck.gl) or allowing dynamic context switching within a route? Current: route-level. May refine if UX demands context blending.
2. **TanStack DB scope**: currently ephemeral collections in `src/db/collections.ts` (no persistence). Should we add IndexedDB + sync? Deferred to Phase 2 offline-first work.
3. **Server function streaming**: should we support streaming responses for large data exports (e.g., parquet download)? Currently all responses are JSON. Planned for Phase 3.

## Failed Experiments

- (placeholder — no failed experiments logged yet for this section)

## Session Handoff Notes

**Current state (2026-05-13)**: All 11 core routes scaffolded and rendering. TanStack Router file-based conventions in place. Server functions wired to sidecar via proxy. No Anthropic SDK in client code verified. TanStack Query replacing manual fetch logic.

**Known issues**:
- `/admin` DDC dashboard stubbed; needs cost + BOQ data binding
- `/notebooks` marimo integration pending; currently placeholder iframe
- Error boundary logging not yet wired to `lattice/execution/outcomes` table

**Ready for next agent**: Route surface frozen. Server function contracts stable. Client purity verified. Ready for context-specific rendering work (Context A ThatOpen, Context B deck.gl layer development).
