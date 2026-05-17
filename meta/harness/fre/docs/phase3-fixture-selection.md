# Phase 3 Fixture Selection

The first real pressure-test fixtures should cover different artifact classes.

Selected initial fixtures:

1. `golden-path-proof-run`
   - source: `meta/harness/docs/sessions/2026-05-12-codebase-context-proof-run.json`
   - why: this is a real verifier-oriented proof artifact with provenance,
     selected files, and verification fields.

2. `handoff-next-session`
   - source: `meta/harness/HANDOFF-NEXT-SESSION.md`
   - why: this is a real restart-ready handoff artifact with baseline, goal,
     mapping lens, and continuity structure.

Why this pair:

- they are both already part of the codebase learning pipeline
- they exercise two different real artifact classes
- they do not require production mutation
- they let the FRE kernel prove value on real repo surfaces before touching
  routes, migrations, or runtime integration
