<!-- spec-verified: disler/bash-damage-from-within f639414 2026-05-12 -->
# Bash Safety

LATTICE incorporates Disler's `bash-damage-from-within` ladder as baseline doctrine for agent and Pi harness execution. This is not a vendor drop; it is part of how LATTICE runs safely.

## Policy

| Level | Policy | LATTICE use |
|---|---|---|
| L1 | skill / user prompt caution | Not enforcement |
| L2 | system-prompt caution | Not enforcement |
| L3 | bash blacklist | Emergency floor only |
| L4 | bash whitelist | Minimum for general Pi harness jobs |
| L5 | no bash, custom tools only | Required for verifier and high-blast-radius jobs |

The operational rule is simple: production-grade harnesses start at L4 and move toward L5.

## L4 default-deny whitelist

L4 means arbitrary bash is denied. Only curated, anchored commands may run, and compound shell operators are rejected before pattern matching.

Never whitelist broad interpreters:

```text
BAD: ^uv run .*\.py$
BAD: ^python .*$
BAD: ^bash .*\.sh$
BAD: ^npm .*$
```

Pin exact repo-owned scripts instead:

```text
GOOD: ^bash scripts/lattice-verify\.sh$
GOOD: ^bash scripts/audit-dead-dna\.sh$
GOOD: ^uv run python scripts/specific-check\.py$
```

## L5 custom tools

L5 removes bash from the tool menu and exposes purpose-built tools. For LATTICE, the first safe tools should wrap:

- `scripts/lattice-verify.sh`
- `scripts/audit-dead-dna.sh`
- `git status --porcelain -b`
- read-only report listing for harness artifacts

Verifier mode should prefer L5. A verifier does not need a general shell; it needs trustworthy oracles.

## Pi implementation note

Pi exposes the required hook point through the `tool_call` event. LATTICE Pi jobs should use a project extension that either:

- blocks bash except for pinned L4 commands, or
- blocks bash entirely and registers L5 tools.

The verifier surface should use L5 wherever possible.
