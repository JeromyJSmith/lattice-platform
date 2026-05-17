# Runs

Each run must live in an immutable directory:

```text
RUN-YYYY-MM-DD-0001/
```

Canonical artifacts per run:

- `input-manifest.yaml`
- `normalized-source-summary.md`
- `research-grounding.json`
- `schema-validation.json`
- `example-validation.json`
- `gate-results.json`
- `scorecard.yaml`
- `repair-tasks.yaml`
- `report.md`
- `promotion-decision.md`

`latest` may exist as a convenience pointer later, but it is never the canonical
run identity.

Iteration rule:

- compare `score_after` to the last accepted score
- accept only if the new score is higher
- stop on the first non-improvement
- if three consecutive accepted improvements occur in one loop session, the
  loop may commit the accepted state
