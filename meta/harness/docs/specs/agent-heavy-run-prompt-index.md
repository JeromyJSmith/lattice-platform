# Agent Heavy-Run Prompt Artifacts

Last updated: 2026-05-18

## Purpose

This directory contains the governed prompt-contract artifacts for heavy-run
agent execution in the Meta-Harness.

These artifacts are meant to work together:

- human-readable method/spec
- machine-readable validation schema
- fill-in template for concrete prompt instances

They are designed to support Copilot, Codex, Claude, and other capable agents
without changing the underlying execution contract.

## Artifact Roles

### 1. Human-readable method/spec

File:

- `agent-heavy-run-prompt-schema.md`

Role:

- explains the prompting method in prose
- defines the prompt blocks and their intent
- records the heavy-run execution pattern
- captures repo policy such as `uv`-first Python execution and truthful blocked
  states

Use this when:

- reviewing the prompting standard with humans
- refining the contract shape
- checking whether a prompt is aligned with Meta-Harness operating doctrine

### 2. Machine-readable schema

File:

- `agent-heavy-run-prompt.schema.json`

Role:

- validates the structure of prompt-contract instances
- defines the required fields and allowed shapes
- provides a portable contract that can be checked automatically

Use this when:

- validating prompt YAML/JSON instances
- building tooling around prompt generation
- enforcing prompt completeness before execution or promotion

### 3. Fill-in template

File:

- `agent-heavy-run-prompt.template.yaml`

Role:

- provides the concrete operator-facing skeleton for new heavy-run prompts
- gives a consistent starting format for bounded execution tasks

Use this when:

- preparing a new Copilot heavy run
- drafting an execution prompt for another agent
- turning repo truth into a governed prompt instance quickly

## Meta-Harness Usage Path

1. Start with the local repo truth and validated current state.
2. Fill the template for the bounded mission.
3. Validate the filled prompt instance against the JSON schema.
4. Render or adapt the prompt for the target execution surface.
5. Run the agent.
6. Record proofs, artifacts, and promotion/repair outcomes.

## Policy Summary

- Use heavy bounded runs when the task boundary is clear.
- Use `uv` for Python execution, dependencies, scripts, and tests.
- Do not default to `pip`, `python -m pip`, `venv`, or `virtualenv` unless `uv`
  is first proven insufficient.
- Do not introduce paid-model API keys as the default runtime path when a
  subscribed execution surface already exists.
- Keep blocked states honest and evidence-backed.

## Canonical Set

The current canonical prompt-contract artifact set is:

- `agent-heavy-run-prompt-index.md`
- `agent-heavy-run-prompt-schema.md`
- `agent-heavy-run-prompt.schema.json`
- `agent-heavy-run-prompt.template.yaml`
