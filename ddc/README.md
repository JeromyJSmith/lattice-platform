# DataDrivenConstruction (DDC) — LATTICE Integration

LATTICE wraps four pieces of the DDC ecosystem:

| Piece | LATTICE home | What it gives us |
|---|---|---|
| 221 SKILL.md patterns | [`skills/`](skills/) | Proven agent workflows — quantity takeoff, cost estimation, scheduling, QC reports |
| CWICR cost database | [`cwicr/`](cwicr/) | 55,719 cost items × 30 regions, semantic-searchable via Qdrant |
| OpenConstructionERP | [`erp/`](erp/) | BOQ, 4D/5D scheduling, AI cost estimation, REST API |
| n8n workflow patterns | [`n8n/`](n8n/) | Visual process logic to translate into LATTICE FastAPI pipelines |

Plus an admin dashboard data layer ([`admin/`](admin/)) and Linux fallback converters ([`converters/`](converters/)) for edge cases IfcOpenShell can't handle.

**The DDC philosophy for LATTICE:** the value is the *patterns and cost data*, not the file converters. LATTICE handles IFC/DXF natively on Mac via IfcOpenShell + ezdxf. DDC's Linux converters are fallbacks only, and we never touch `ddc-rvtconverter` or `ddc-dgnconverter` (no Revit, no DGN in LATTICE).

For the full repo-by-repo map see [`../meta/DDC_MAPPING.md`](../meta/DDC_MAPPING.md).
