# Research Grounding

This evaluation should have started with research-grounding.

The first FRE scaffold violated that rule by moving directly into
source-normalization, schema creation, and scoring. This document corrects the
contract and records the minimum research layer required before the loop may
claim useful evidence.

## Grounding Inputs

1. Source packet:
   - `/Volumes/PixelTable/VW_iTWIN_Bridge/fre-test-eval-improvement 76019c48ec2441c0a42a1ac7a3f9b49b.md`
2. Existing LATTICE Meta-Harness ratchet doctrine:
   - `meta/harness/CLAUDE.md`
   - `meta/harness/GOAL.md`
3. Existing FRE bounded evaluation artifacts:
   - `docs/source-normalization.md`
   - `docs/fre-to-lattice-map.md`
   - `docs/phase3-fixture-selection.md`

## Research Conclusions

- Research must precede schema execution.
- The imported FRE packet is a proposal source, not executable authority.
- The LATTICE Meta-Harness contract is ratchet-based:
  `score_before -> sandbox proposal -> score_after -> accept only if improved`.
- A bounded FRE slice inside LATTICE must inherit that ratchet discipline rather
  than pretending the schema loop alone is enough.
- Real artifact pressure tests matter more than toy example success.

## Local Contract Change

The bounded FRE kernel now treats this sequence as canonical:

```text
research -> source -> schema -> examples -> validation -> metrics -> repair task -> promotion decision
```

Any future score or promotion decision that omits the research layer should be
treated as incomplete.
