#!/usr/bin/env python3
"""Assess the current Farber-Haines working-copy IFC export."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path


REPO_ROOT = Path("/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge")
IFC_PATH = REPO_ROOT / "_Farber-Haines [2521]__ESTIMATION_WORKING_COPY__2026-05-16.ifc"
REPORT_JSON = REPO_ROOT / "docs/farber-haines-ifc-export-assessment.json"
REPORT_MD = REPO_ROOT / "docs/farber-haines-ifc-export-assessment.md"

ENTITY_NAMES = [
    "IFCPROJECT",
    "IFCSITE",
    "IFCBUILDING",
    "IFCBUILDINGSTOREY",
    "IFCGEOGRAPHICELEMENT",
    "IFCSLAB",
    "IFCWALL",
    "IFCMEMBER",
    "IFCFURNISHINGELEMENT",
    "IFCPLANT",
    "IFCBUILDINGELEMENTPROXY",
    "IFCPROXY",
]

TERM_LABELS = {
    "Project Cost": "project_cost_record",
    "Plant Record": "plant_record",
    "Unit Cost": "unit_cost_field",
    "Total Cost": "total_cost_field",
    "Measure Basis": "measure_basis_field",
    "VwPset_MARPA_Object": "vwpset_marpa_object",
    "VwPset_MARPA_Plant": "vwpset_marpa_plant",
    "VwPset_MARPA_Cost": "vwpset_marpa_cost",
    "VwPset_MARPA_Source": "vwpset_marpa_source",
    "VwPset_MARPA_ExportQA": "vwpset_marpa_exportqa",
    "Pset_VegetationCommon": "pset_vegetation_common",
}


def parse_schema(text: str) -> str:
    match = re.search(r"FILE_SCHEMA\(\('([^']+)'\)\);", text)
    return match.group(1) if match else ""


def parse_header_description(text: str) -> str:
    match = re.search(r"FILE_DESCRIPTION\(\('([^']+)'\),", text)
    return match.group(1) if match else ""


def count_entities(text: str) -> Counter[str]:
    pattern = re.compile(r"=\s*(IFC[A-Z0-9_]+)\(")
    counts: Counter[str] = Counter()
    for line in text.splitlines():
        match = pattern.search(line)
        if match:
            counts[match.group(1)] += 1
    return counts


def parse_projected_crs(text: str) -> dict[str, str]:
    match = re.search(r"IFCPROJECTEDCRS\('([^']+)'(?:,\$|,)", text)
    full = match.group(1) if match else ""
    epsg = ""
    if full.startswith("EPSG:"):
        epsg = full.split()[0].replace("EPSG:", "")
    return {"name": full, "epsg_code": epsg}


def parse_map_conversion(text: str) -> dict[str, float | None]:
    match = re.search(
        r"IFCMAPCONVERSION\([^,]+,[^,]+,([-0-9.]+),([-0-9.]+),([-0-9.]+),([-0-9.]+),([-0-9.]+),",
        text,
    )
    if not match:
        return {
            "eastings": None,
            "northings": None,
            "orthogonal_height": None,
            "x_axis_abscissa": None,
            "x_axis_ordinate": None,
        }
    eastings, northings, height, abscissa, ordinate = match.groups()
    return {
        "eastings": float(eastings),
        "northings": float(northings),
        "orthogonal_height": float(height),
        "x_axis_abscissa": float(abscissa),
        "x_axis_ordinate": float(ordinate),
    }


def scan_terms(text: str) -> dict[str, bool]:
    return {label: term in text for term, label in TERM_LABELS.items()}


def determine_status(
    schema: str,
    entity_counts: Counter[str],
    epsg_code: str,
    term_hits: dict[str, bool],
) -> tuple[str, list[str]]:
    issues: list[str] = []
    if schema not in {"IFC4X3", "IFC4X3_ADD2"}:
        issues.append(f"unexpected_schema:{schema or 'missing'}")
    if entity_counts.get("IFCGEOGRAPHICELEMENT", 0) <= 0:
        issues.append("missing_site_semantic_entities")
    if entity_counts.get("IFCSLAB", 0) == 0:
        issues.append("hardscape_not_typed_as_ifcslab")
    if epsg_code != "2231":
        issues.append(f"unexpected_crs:{epsg_code or 'missing'}")
    if not term_hits.get("vwpset_marpa_cost"):
        issues.append("missing_marpa_cost_pset")
    if not term_hits.get("project_cost_record"):
        issues.append("missing_project_cost_payload")
    status = "pass" if not issues else "warn"
    return status, issues


def render_markdown(report: dict) -> str:
    lines = [
        "# Farber-Haines IFC Export Assessment",
        "",
        f"- IFC path: `{report['ifc_path']}`",
        f"- Size bytes: `{report['size_bytes']}`",
        f"- Schema: `{report['schema']}`",
        f"- Header description: `{report['header_description']}`",
        f"- Status: `{report['status']}`",
        "",
        "## Georeference",
        "",
        f"- Projected CRS name: `{report['projected_crs']['name']}`",
        f"- Projected CRS EPSG: `{report['projected_crs']['epsg_code']}`",
        f"- Map conversion eastings: `{report['map_conversion']['eastings']}`",
        f"- Map conversion northings: `{report['map_conversion']['northings']}`",
        f"- Map conversion X-axis abscissa: `{report['map_conversion']['x_axis_abscissa']}`",
        f"- Map conversion X-axis ordinate: `{report['map_conversion']['x_axis_ordinate']}`",
        "",
        "## Entity Coverage",
        "",
    ]
    for name in ENTITY_NAMES:
        lines.append(f"- `{name}`: `{report['entity_counts'].get(name, 0)}`")
    lines.extend([
        "",
        "## Payload Checks",
        "",
    ])
    for key, value in report["term_hits"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend([
        "",
        "## Issues",
        "",
    ])
    if report["issues"]:
        for issue in report["issues"]:
            lines.append(f"- `{issue}`")
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    if not IFC_PATH.exists():
        payload = {"ok": False, "error": f"missing_ifc:{IFC_PATH}"}
        REPORT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        REPORT_MD.write_text("# Farber-Haines IFC Export Assessment\n\n- missing IFC export\n", encoding="utf-8")
        print(json.dumps(payload, indent=2))
        return 1

    text = IFC_PATH.read_text(encoding="utf-8", errors="ignore")
    entity_counts = count_entities(text)
    projected_crs = parse_projected_crs(text)
    term_hits = scan_terms(text)
    schema = parse_schema(text)
    status, issues = determine_status(schema, entity_counts, projected_crs["epsg_code"], term_hits)

    report = {
        "ok": True,
        "ifc_path": str(IFC_PATH),
        "size_bytes": IFC_PATH.stat().st_size,
        "schema": schema,
        "header_description": parse_header_description(text),
        "projected_crs": projected_crs,
        "map_conversion": parse_map_conversion(text),
        "entity_counts": {name: entity_counts.get(name, 0) for name in ENTITY_NAMES},
        "term_hits": term_hits,
        "status": status,
        "issues": issues,
    }
    REPORT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
