<!-- spec-verified: disler/the-library 47f455c 2026-05-12 -->
# Agentics Library

LATTICE incorporates Disler's `the-library` as the internal catalog pattern for skills, agents, prompts, capabilities, references, and small harness command workflows.

This is not a vendor registry. It is a LATTICE catalog of references to agentic capabilities that live in source repos, local paths, or harness directories. Nothing is installed everywhere by default. The orchestrator pulls what a harness job needs.

The persistent asset is the catalog entry. The working copy is disposable.

## Rule

The Library is a catalog, not a manifest.

- Catalog entries define what is available.
- Harness jobs install or refresh entries on demand.
- Dependencies use typed references: `skill:name`, `agent:name`, `prompt:name`.
- The source path is the provenance record.
- A source file points to the capability entrypoint; the parent directory is the transferable unit.
- LATTICE may add catalog sections beyond the original skill/agent/prompt buckets.

## Why it fits now

The Meta-Harness is about to create many small harness agents and prompt commands. Without a library, those will sprawl across `.claude/`, `.pi/`, `.codex/`, repo-local docs, and worktrees. The Library gives LATTICE a controlled reference catalog before the dry run.

## LATTICE scope

LATTICE extends the original skill/agent/prompt idea with capabilities, references, and harness jobs:

| Type | Meaning |
|---|---|
| skill | Reusable agent skill directory with `SKILL.md` |
| agent | Single-file or directory-backed agent persona |
| prompt | Slash command, `/P` command, or prompt template |
| capability | Tool surface, doctrine pattern, or harness function registered in `analysis/capabilities/` |
| reference | Repo, gist, doc page, workflow, diagram, local file, or research source |
| job | One-shot harness task with input, artifact, and verification target |

The first three map directly to `the-library`. `capability`, `reference`, and `job` are LATTICE extensions.

## Frontmatter

Agents, skills, and prompts should carry enough frontmatter for the library and harness to understand them without reading the entire body first.

Recommended fields:

```yaml
---
name: <name>
description: <when to use>
capabilities:
  - capability:<id>
references:
  - reference:<id>
requires:
  - skill:<name>
  - agent:<name>
  - prompt:<name>
verification:
  command: bash scripts/lattice-verify.sh
---
```

The library catalog remains the source of truth for where to fetch something. Frontmatter makes each artifact self-describing once fetched.

## Operating flow

1. Build or select a capability.
2. Register it in `meta/harness/library.yaml`.
3. Pull it on demand into the target surface.
4. Run it through Pi, Claude CLI, Codex, or another selected execution surface.
5. Verify output with a repo-owned script.
6. Promote or revise based on model-fit and verifier evidence.

## Ephemeral sandbox pattern

The library reduces repository bloat by keeping references in config and pulling working copies only when a job needs them.

Default flow:

1. Read `meta/harness/library.yaml`.
2. Resolve the referenced repo, gist, doc, workflow, script, skill, agent, or prompt.
3. Create a temporary sandbox outside the repo working tree.
4. Clone or copy only what the job needs.
5. Run the bounded task through Pi or another selected execution surface.
6. Emit the required artifact or evidence back into the LATTICE repo or external workpad.
7. Delete the sandbox.

This is the "turn and burn" pattern: wake up, pull the referenced capability, execute, verify, report, clean up. The repo keeps the durable config and evidence, not every transient tool checkout.

Rules:

- Do not vendor-copy external repos just to make them available.
- Do not leave temporary clones in the LATTICE repo.
- Do not promote a sandbox artifact unless it is an intended output of the task.
- Keep source provenance in the library entry so the next run can recreate the sandbox.
- If a pulled capability becomes permanent doctrine, register it in `analysis/capabilities/` and document the incorporated rule.

## Dry-run use

For the first Meta-Harness dry run, the library should catalog only the capabilities needed for setup:

- Pi delegation surface
- Pi verifier observer pattern
- bash safety ladder
- capability harvest lifecycle
- model-fit benchmark loop
- lattice verifier script
- key upstream repos and docs used by those capabilities

Do not flood the catalog before the dry run. The point is controlled reuse, not inventory noise.
