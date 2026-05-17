# Source Normalization Record

The source packet is Notion-derived and already contains export corruption.
Nothing becomes executable until it passes this normalization layer.

Normalization decisions applied:

- malformed markdown links inside code blocks are treated as corruption
- malformed commands such as `validate_[schema.py](http://schema.py)` are corrected to `validate_schema.py`
- malformed commands such as `harness/[evaluate.py](http://evaluate.py)` are corrected to `harness/evaluate.py`
- Notion page mentions are converted into plain provenance records
- YAML blocks must be checked before reuse
- JSON blocks must be checked before reuse
- code fences must be closed before reuse

Terminology decisions:

- canonical term: `validation_pass_criteria`
- rejected term: `definition_of_green`
- the rejected term may appear only in:
  - intentional invalid fixtures
  - expected-failure manifests
  - this normalization record
  - tests that enforce the rejection

Normalization exit check:

1. repo-local commands are plain text, not markdown links
2. schema/example/test content is valid JSON, YAML, or Markdown
3. no executable artifact inherits malformed Notion formatting
