<!-- spec-verified: code.claude.com/docs 2026-05-11 -->
# Capability Matrix — <tool>

| Capability ID | Harness | Value | Risk | Decision | Proof run | Registry state after proof | Verification target | Tracking |
|---|---|---|---|---|---|---|---|---|
| `<slug>` | `<global|docs|runtime|bridge|viewer|...>` | `high|medium|low` | `high|medium|low` | `candidate|defer|block|reject` | `none|pass|fail` | `ACTIVE|DEFERRED|BLOCKED|none` | `<command, test, report, or artifact>` | `<issue or PR>` |

Rules:

- `candidate` means the capability is worth trying, but does not become `ACTIVE` until a proof run passes.
- `defer` maps to `DEFERRED` and requires a reason, target phase, and issue.
- `block` maps to `BLOCKED` and requires a resolution path.
- `reject` is allowed in the matrix but does not enter the registry unless the rejection needs audit visibility.
- A capability with `Proof run = none` has zero operational credit, even if it looks promising.
