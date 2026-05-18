# FRE to LATTICE translation map

| FRE field | LATTICE concept | Transfer status | Notes |
|---|---|---|---|
| `gate_id` | lifecycle gate join key | clean | Governance joins must use the stable gate identifier only. |
| `repair_task` | proposal / bounded implementation task | clean | Requires owner and explicit acceptance criteria. |
| `promotion_decision` | ratchet decision / capability promotion gate | partial | Promotion is explicit, but deeper readiness criteria still need expansion. |
| `scorecard` | benchmark / evidence artifact | clean | Keep evidence tied to concrete artifact paths. |
| `validation_pass_criteria` | contract acceptance rule | clean | Remains the canonical positive-proof term. |
| `source_record` | provenance evidence | partial | Needs richer source typing beyond this minimal slice. |
| `artifact` | proof artifact | partial | Needs lineage expansion once more evaluation outputs are ported. |

Allowed statuses:

- `clean`
- `partial`
- `conflict`
- `reject`
- `needs_extension`
