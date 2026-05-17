# CLAUDE Instructions for FRE Evaluation

Work only inside `meta/harness/fre/` unless a session report explicitly justifies
an exception.

Mission:

- make research-grounding the first gate
- make the FRE candidate loop executable
- keep it falsifiable
- keep it repair-producing
- do not let Notion export damage become executable truth

Hard rules:

1. `validation_pass_criteria` is the canonical term.
2. The rejected green-terminology field is forbidden except in intentional
   invalid fixtures, source-normalization records, and enforcement tests.
3. Do not mutate production schema, routes, UI, deployment config, or data.
4. Do not add migrations.
5. Do not add runtime integration before the contract proves useful.
6. Invalid examples must fail for expected reasons, not accidental ones.
7. Failed blocking gates must emit repair tasks.
8. No run is promotable if the research-grounding artifact layer is missing.

First-pass commands:

```text
uv run pytest meta/harness/fre/tests
uv run python meta/harness/fre/harness/validate_schema.py
uv run python meta/harness/fre/harness/validate_examples.py
uv run python meta/harness/fre/harness/evaluate.py
uv run python meta/harness/fre/harness/propose_repairs.py
uv run python meta/harness/fre/harness/report.py
```
