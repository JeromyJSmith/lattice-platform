<!-- spec-verified: disler/fork-repository-skill ba196f6; disler/agent-sandbox-skill ac460ee; disler/agent-sandboxes 1a72555 2026-05-12 -->
# Fork And Sandbox

LATTICE uses forking and sandboxing to scale work without bloating the main repo or risking the local production environment.

## Fork terminal pattern

Forking means creating a separate execution context for a bounded job:

- new terminal or process
- selected tool/model
- optional context summary
- one explicit task
- one output artifact
- one verification target

Use it for parallel review, model comparisons, long-running jobs, and work that benefits from an isolated context window.

## Sandbox pattern

Sandboxing means running the job away from the local repo and production filesystem. E2B is the first incorporated sandbox target.

The default sandbox lifecycle is:

1. create sandbox
2. clone/copy the required repo or library reference
3. run the bounded task
4. host/test if needed
5. collect artifact, logs, cost, and verification evidence
6. destroy or pause the sandbox according to the job policy

## Plan-build-host-test

For buildable artifacts, use this lifecycle:

```text
Plan -> Build -> Host -> Test -> Report
```

Each stage must leave evidence. Browser-visible work needs browser verification, not only a build log.

## Parallel forks

Parallel forks are for experiments and model-fit benchmarking:

- run the same prompt against multiple models
- run several implementation approaches in isolated sandboxes
- compare outputs by deterministic metrics
- promote only the winning artifact or doctrine

Parallel forks should never merge or push directly to protected branches.

## Local boundary

Local tools may only touch allowed report/spec/temp directories during sandbox orchestration. Repo operations belong inside the sandbox unless the task explicitly returns a verified artifact for the main repo.

## Backslash and prompt commands

Reusable prompt commands can be mapped by path convention, including nested commands such as:

```text
\agent-sandboxes:plan-build-host-test
\sandbox
```

For LATTICE, these become library catalog entries and Pi-run harness jobs rather than ad hoc chat instructions.
