# FRE to LATTICE Translation Map

| FRE field | LATTICE concept | Transfer status | Notes |
|---|---|---|---|
| `repair_task` | proposal / bounded implementation task | clean | Requires owner and acceptance criteria |
| `promotion_decision` | ratchet decision / capability promotion gate | partial | Needs stronger evidence fields |
| `scorecard` | benchmark / evidence artifact | clean | Should include command output hashes |
| `validation_pass_criteria` | ratchet acceptance rule | clean | Rename acceptable |
| `source_record` | provenance evidence | partial | Needs richer source typing |
| `artifact` | capability/proof artifact | partial | Needs artifact lineage |

Allowed statuses:

- `clean`
- `partial`
- `conflict`
- `reject`
- `needs_extension`
