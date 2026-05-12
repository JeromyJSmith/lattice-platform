<!-- spec-verified: disler/install-and-maintain 558b5c8 2026-05-12 -->
# Install And Maintain

LATTICE incorporates the `install-and-maintain` pattern: deterministic scripts are the source of truth, and agents supervise, diagnose, and report.

## Rule

Setup and maintenance are living executable docs:

- deterministic mode runs scripts and exits
- agentic mode reads logs, diagnoses failures, and writes reports
- interactive mode asks questions only when human context matters

The agent should not invent setup steps during a dry run. It should run the scripted setup, read the log, and report exact results.

## LATTICE shape

| Mode | Use |
|---|---|
| deterministic init | CI, dry-run smoke checks, fast local setup |
| agentic init report | failed setup diagnosis, onboarding evidence |
| interactive init | first-time human setup when choices are required |
| deterministic maintenance | recurring dependency/doc/model refresh |
| agentic maintenance report | summarize what changed and what needs attention |

## Meta-Harness dry-run target

The first dry run should prove:

1. the setup script is discoverable from the library
2. the setup script can run without undocumented manual steps
3. logs are written
4. an agent can summarize the logs into an evidence artifact
5. failures produce next steps instead of vague advice

## Script ownership

LATTICE setup scripts must be repo-owned. If a setup action is repeated twice, it belongs in a script or just recipe before it belongs in a prompt.
