# Local Doctrine Map

This skill is bound to the local LATTICE Meta-Harness, not just to generic
skills.sh ideas.

## Local Sources

- `meta/harness/CLAUDE.md`
- `meta/harness/GOAL.md`
- `meta/harness/fre/harness/iterate.py`
- `meta/harness/fre/harness/lib.py`

## Local Rules That Matter

1. The ratchet accepts only real score improvements.
2. Incomplete or broken runs are not valid baselines.
3. Blocking-gate failures must prevent promotion.
4. Real fixture evidence is stronger than toy example success.
5. The FRE slice is bounded and must not widen into production mutation during
   this phase.

## Local Interpretation

The local Meta-Harness doctrine says:

```text
score_before -> sandbox or isolated cycle -> score_after -> accept only if improved
```

The FRE skill adds a stronger precondition:

```text
research -> score_before -> iteration -> score_after -> keep or stop
```

## Commit Rule for This Bounded Skill

This local skill uses the user's stricter commit threshold:

- one accepted improvement is not enough to commit
- three consecutive accepted improvements are required before commit
- plateau or regression stops the session
