# FRE Test/Eval Improvement in LATTICE

This directory is a bounded evaluation of the FRE minimal loop inside LATTICE.

The purpose is not to adopt FRE as doctrine. The purpose is to test whether a
schema-driven loop can act as the smallest repeatable proof kernel:

```text
research -> source -> schema -> examples -> validation -> metrics -> repair task -> promotion decision
```

Current scope:

- perform research-grounding before promoting any source packet material into
  repo-local authority
- normalize the source packet
- make the loop executable
- make invalid cases fail for expected reasons
- emit repair tasks and a promotion decision

Out of scope:

- Pixeltable migrations
- production runtime integration
- UI work
- Notion sync
- sidecar wiring
- multi-agent orchestration

The canonical plan for this evaluation lives at:

`meta/harness/docs/specs/fre-method-evaluation-plan-2026-05-16.md`
