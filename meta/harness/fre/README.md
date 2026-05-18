# FRE main contract slice

This bounded lane restores the first proof-package slice from the sibling FRE
worktree onto `main`.

The package order is fixed:

1. `source`
2. `schema`
3. `examples`
4. `expected-failures`
5. `tests`
6. `evaluation`
7. `promotion`

Evaluation and promotion are explicit artifact parts. They are not implied by
tests.

Heavy and bounded execution prompts in this lane must trace back to the governed
prompt-contract set:

- `meta/harness/docs/specs/agent-heavy-run-prompt-index.md`
- `meta/harness/docs/specs/agent-heavy-run-prompt-schema.md`
- `meta/harness/docs/specs/agent-heavy-run-prompt.schema.json`
- `meta/harness/docs/specs/agent-heavy-run-prompt.template.yaml`
- `meta/harness/docs/copilot-prompting-playbook.md`
