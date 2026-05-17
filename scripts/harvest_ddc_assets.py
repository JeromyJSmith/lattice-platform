#!/usr/bin/env -S uv run --script
"""Harvest DDC skills and n8n assets into local LATTICE paths.

Copies upstream DDC assets from `projects/DDC_Skills_for_AI_Agents_in_Construction-main`
into:
  - `skills/ddc/` (all SKILL.md files, mirrored by relative path)
  - `ddc/n8n/workflows/` (n8n-* automation packs)

Usage:
  uv run scripts/harvest_ddc_assets.py
  uv run scripts/harvest_ddc_assets.py --skills-only
  uv run scripts/harvest_ddc_assets.py --n8n-only
"""

from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class HarvestCounts:
    skill_files: int = 0
    n8n_packs: int = 0
    n8n_files: int = 0


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _reset_dir(target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)


def harvest_skills(source_root: Path, target_root: Path, counts: HarvestCounts) -> None:
    _reset_dir(target_root)
    skill_paths = sorted(source_root.rglob("SKILL.md"))
    for src in skill_paths:
        rel = src.relative_to(source_root)
        dst = target_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        counts.skill_files += 1


def harvest_n8n(source_root: Path, workflows_root: Path, counts: HarvestCounts) -> None:
    _reset_dir(workflows_root)
    packs = sorted(
        p
        for p in source_root.rglob("n8n-*")
        if p.is_dir() and (p / "SKILL.md").exists()
    )
    for pack in packs:
        dst_pack = workflows_root / pack.name
        shutil.copytree(pack, dst_pack, dirs_exist_ok=True)
        counts.n8n_packs += 1
        counts.n8n_files += sum(1 for _ in dst_pack.rglob("*") if _.is_file())


def write_manifest(manifest_path: Path, source_root: Path, counts: HarvestCounts) -> None:
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_root": str(source_root),
        "skills_harvested": counts.skill_files,
        "n8n_packs_harvested": counts.n8n_packs,
        "n8n_files_harvested": counts.n8n_files,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Harvest DDC assets into local repo")
    parser.add_argument("--skills-only", action="store_true", help="Only harvest SKILL.md corpus")
    parser.add_argument("--n8n-only", action="store_true", help="Only harvest n8n packs")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.skills_only and args.n8n_only:
        raise SystemExit("--skills-only and --n8n-only are mutually exclusive")

    root = _repo_root()
    source_root = root / "projects" / "DDC_Skills_for_AI_Agents_in_Construction-main"
    if not source_root.exists():
        raise SystemExit(f"DDC source root missing: {source_root}")

    counts = HarvestCounts()
    do_skills = not args.n8n_only
    do_n8n = not args.skills_only

    if do_skills:
        harvest_skills(source_root, root / "skills" / "ddc", counts)
    if do_n8n:
        harvest_n8n(source_root, root / "ddc" / "n8n" / "workflows", counts)

    write_manifest(root / "ddc" / "harvest-manifest.json", source_root, counts)
    print(
        f"harvest complete: skills={counts.skill_files} "
        f"n8n_packs={counts.n8n_packs} n8n_files={counts.n8n_files}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

