#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "click>=8.0",
#   "rich>=13.0",
#   "pyyaml>=6.0",
# ]
# ///
"""lattice — LATTICE platform CLI.

Commands
--------
  project init <name> <path>   Register a project directory with LATTICE
  project switch <name>        Set the active project (machine-local)
  project list                 List all registered projects
  project status               Show health of the active project
  project sync                 Push bridge-briefs for the active project

The active project is stored in .lattice-active-project at the LATTICE root
(gitignored). All ingest routes, scoring, and autoresearch cycles read this
file to scope their Pixeltable namespace to lattice/projects/<id>/.

Usage
-----
  lattice project init juniper2026 /Volumes/PixelTable/GROVE_HARNESS/juniper2026
  lattice project switch juniper2026
  lattice project status
  lattice project list
"""
from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import click
import yaml
from rich.console import Console
from rich.table import Table
from rich import box

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

# The CLI lives at scripts/lattice.py inside the LATTICE repo.
LATTICE_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = LATTICE_ROOT / "projects" / "registry.yaml"
ACTIVE_POINTER = LATTICE_ROOT / ".lattice-active-project"

console = Console()


# ---------------------------------------------------------------------------
# Registry helpers
# ---------------------------------------------------------------------------

def load_registry() -> dict[str, Any]:
    """Load projects/registry.yaml, returning empty dict on missing file."""
    if not REGISTRY_PATH.exists():
        return {"projects": []}
    with REGISTRY_PATH.open() as f:
        data = yaml.safe_load(f) or {}
    if "projects" not in data:
        data["projects"] = []
    return data


def save_registry(data: dict[str, Any]) -> None:
    """Write projects/registry.yaml atomically."""
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(
        yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)
    )


def find_project(registry: dict[str, Any], name: str) -> dict[str, Any] | None:
    """Return the project dict with matching id or name, or None."""
    for p in registry.get("projects", []):
        if p.get("id") == name or p.get("name") == name:
            return p
    return None


def active_project_id() -> str | None:
    """Return the currently active project id, or None."""
    if not ACTIVE_POINTER.exists():
        return None
    raw = ACTIVE_POINTER.read_text().strip()
    return raw or None


# ---------------------------------------------------------------------------
# Health checks
# ---------------------------------------------------------------------------

def project_health(proj: dict[str, Any]) -> list[tuple[str, bool, str]]:
    """Return a list of (check_label, passed, detail) tuples."""
    path = Path(proj["path"])
    checks: list[tuple[str, bool, str]] = []

    checks.append((
        ".lattice-project.yaml",
        (path / ".lattice-project.yaml").exists(),
        str(path / ".lattice-project.yaml"),
    ))
    checks.append((
        "library.yaml",
        (path / "library.yaml").exists(),
        str(path / "library.yaml"),
    ))

    # VW source files
    vw_files = proj.get("vw_files", [])
    for vf in vw_files[:3]:  # cap at 3
        vf_path = path / vf if not Path(vf).is_absolute() else Path(vf)
        checks.append((
            f"vw: {Path(vf).name}",
            vf_path.exists(),
            str(vf_path),
        ))

    # Pixeltable sidecar reachable
    try:
        result = subprocess.run(
            ["curl", "-sf", "http://localhost:8001/health"],
            capture_output=True, text=True, timeout=2,
        )
        checks.append((
            "FastAPI sidecar :8001",
            result.returncode == 0,
            "http://localhost:8001/health",
        ))
    except Exception:
        checks.append(("FastAPI sidecar :8001", False, "curl timed out or failed"))

    return checks


# ---------------------------------------------------------------------------
# CLI root
# ---------------------------------------------------------------------------

@click.group()
def cli() -> None:
    """LATTICE platform CLI. Run 'lattice project --help' to get started."""


# ---------------------------------------------------------------------------
# project subgroup
# ---------------------------------------------------------------------------

@cli.group()
def project() -> None:
    """Manage LATTICE projects."""


# ---------------------------------------------------------------------------
# project init
# ---------------------------------------------------------------------------

@project.command("init")
@click.argument("name")
@click.argument("path", type=click.Path(exists=True, file_okay=False, resolve_path=True))
@click.option("--force", is_flag=True, help="Overwrite existing registration")
def project_init(name: str, path: str, force: bool) -> None:
    """Register a project directory with LATTICE.

    NAME  — short identifier used for switching (e.g. juniper2026)
    PATH  — absolute or relative path to the project directory
    """
    proj_path = Path(path)
    registry = load_registry()

    # Check for duplicate
    existing = find_project(registry, name)
    if existing and not force:
        console.print(
            f"[yellow]Project '{name}' is already registered at {existing['path']}.[/yellow]\n"
            "Use --force to overwrite."
        )
        sys.exit(1)

    # Auto-detect existing project metadata
    detected: dict[str, Any] = {}
    for candidate in ["project.yaml", ".lattice-project.yaml"]:
        candidate_path = proj_path / candidate
        if candidate_path.exists():
            with candidate_path.open() as f:
                raw = yaml.safe_load(f) or {}
            # Support nested {project: {id: ...}} or flat {id: ...}
            detected = raw.get("project", raw)
            console.print(f"[dim]Detected metadata from {candidate}[/dim]")
            break

    # Build project record
    display_name = detected.get("name") or name.replace("-", " ").replace("_", " ").title()
    namespace = f"lattice/projects/{name}"
    now = datetime.now(timezone.utc).date().isoformat()

    record: dict[str, Any] = {
        "id": name,
        "name": display_name,
        "path": str(proj_path),
        "pixeltable_namespace": namespace,
        "added": now,
    }

    # Pull VW file references if they exist — skip hidden dirs and virtual envs
    _SKIP_DIRS = {".venv", ".git", ".claude", "node_modules", "__pycache__", "_attic"}

    def _vw_files_in(root: Path, pattern: str) -> list[Path]:
        results = []
        for f in root.rglob(pattern):
            # Skip if any parent segment is a hidden or skipped dir
            parts = set(f.relative_to(root).parts)
            if parts & _SKIP_DIRS or any(p.startswith(".") for p in parts):
                continue
            results.append(f)
        return sorted(results)[:2]

    vw_files = []
    for ext in ["*.vwx", "*.ifc"]:
        for f in _vw_files_in(proj_path, ext):
            vw_files.append(str(f.relative_to(proj_path)))
    if vw_files:
        record["vw_files"] = vw_files

    # Write .lattice-project.yaml into the project dir
    lp_path = proj_path / ".lattice-project.yaml"
    lp_data: dict[str, Any] = {
        "id": name,
        "name": display_name,
        "lattice_platform": str(LATTICE_ROOT),
        "pixeltable_namespace": namespace,
        "created": now,
    }
    if vw_files:
        lp_data["vw_files"] = vw_files
    lp_path.write_text(
        yaml.dump(lp_data, default_flow_style=False, sort_keys=False, allow_unicode=True)
    )
    console.print(f"[green]✓[/green] Wrote {lp_path}")

    # Write library.yaml template if missing
    lib_path = proj_path / "library.yaml"
    if not lib_path.exists():
        lib_template = LATTICE_ROOT / "projects" / "template" / "library.yaml"
        if lib_template.exists():
            lib_path.write_text(lib_template.read_text())
            console.print(f"[green]✓[/green] Wrote {lib_path} (from template)")
        else:
            # Write minimal inline template
            lib_data = {
                "platform": {
                    "name": "LATTICE",
                    "path": str(LATTICE_ROOT),
                    "pixeltable_namespace": namespace,
                },
                "shared_knowledge": {
                    "plant_classifications": "lattice/knowledge/plant_classifications",
                    "bis_class_overrides": "lattice/knowledge/bis_class_overrides",
                    "site_georef_anchors": "lattice/knowledge/site_georef_anchors",
                },
            }
            lib_path.write_text(
                yaml.dump(lib_data, default_flow_style=False, sort_keys=False, allow_unicode=True)
            )
            console.print(f"[green]✓[/green] Wrote {lib_path}")

    # Register in registry
    projects = registry.get("projects", [])
    if existing and force:
        projects = [p for p in projects if p.get("id") != name]
    projects.append(record)
    registry["projects"] = projects
    save_registry(registry)
    console.print(f"[green]✓[/green] Registered '{name}' in {REGISTRY_PATH.relative_to(LATTICE_ROOT)}")

    # Suggest switching
    active = active_project_id()
    if active != name:
        console.print(
            f"\n[bold]Next:[/bold] run [cyan]lattice project switch {name}[/cyan] to make this the active project."
        )


# ---------------------------------------------------------------------------
# project switch
# ---------------------------------------------------------------------------

@project.command("switch")
@click.argument("name")
def project_switch(name: str) -> None:
    """Set the active project (written to .lattice-active-project, gitignored)."""
    registry = load_registry()
    proj = find_project(registry, name)
    if not proj:
        console.print(
            f"[red]Project '{name}' not found.[/red] "
            "Run [cyan]lattice project list[/cyan] to see registered projects."
        )
        sys.exit(1)

    ACTIVE_POINTER.write_text(proj["id"] + "\n")
    console.print(
        f"[green]✓[/green] Active project → [bold]{proj['id']}[/bold]  ({proj['name']})\n"
        f"  Pixeltable namespace: [dim]{proj['pixeltable_namespace']}[/dim]"
    )


# ---------------------------------------------------------------------------
# project list
# ---------------------------------------------------------------------------

@project.command("list")
def project_list() -> None:
    """List all registered projects."""
    registry = load_registry()
    projects = registry.get("projects", [])
    active = active_project_id()

    if not projects:
        console.print("[dim]No projects registered. Run 'lattice project init' to add one.[/dim]")
        return

    table = Table(box=box.SIMPLE_HEAVY, show_header=True, header_style="bold cyan")
    table.add_column("", width=2)
    table.add_column("ID", style="bold")
    table.add_column("Name")
    table.add_column("Namespace", style="dim")
    table.add_column("Path", style="dim")
    table.add_column("Added", style="dim")

    for p in projects:
        marker = "[green]●[/green]" if p.get("id") == active else " "
        table.add_row(
            marker,
            p.get("id", "?"),
            p.get("name", "?"),
            p.get("pixeltable_namespace", "?"),
            p.get("path", "?"),
            p.get("added", "?"),
        )

    console.print(table)
    if active:
        console.print(f"[dim]Active (●): {active}[/dim]")


# ---------------------------------------------------------------------------
# project status
# ---------------------------------------------------------------------------

@project.command("status")
@click.option("--project", "proj_id", default=None, help="Project ID (default: active project)")
def project_status(proj_id: str | None) -> None:
    """Show health of the active project (or a named project)."""
    target = proj_id or active_project_id()
    if not target:
        console.print(
            "[yellow]No active project.[/yellow] "
            "Run [cyan]lattice project switch <name>[/cyan] first."
        )
        sys.exit(1)

    registry = load_registry()
    proj = find_project(registry, target)
    if not proj:
        console.print(f"[red]Project '{target}' not found in registry.[/red]")
        sys.exit(1)

    console.print(f"\n[bold]{proj['name']}[/bold]  [dim]({proj['id']})[/dim]")
    console.print(f"  Path:      {proj['path']}")
    console.print(f"  Namespace: {proj['pixeltable_namespace']}")
    console.print()

    checks = project_health(proj)
    all_pass = True
    for label, passed, detail in checks:
        icon = "[green]✓[/green]" if passed else "[red]✗[/red]"
        console.print(f"  {icon}  {label}")
        if not passed:
            console.print(f"       [dim]missing: {detail}[/dim]")
            all_pass = False

    console.print()
    if all_pass:
        console.print("[green]All checks passed.[/green]")
    else:
        console.print("[yellow]Some checks failed — see above.[/yellow]")


# ---------------------------------------------------------------------------
# project sync
# ---------------------------------------------------------------------------

@project.command("sync")
@click.option("--project", "proj_id", default=None, help="Project ID (default: active project)")
@click.option("--dry", is_flag=True, help="Describe what would sync without writing")
def project_sync(proj_id: str | None, dry: bool) -> None:
    """Push bridge-briefs for the active project (feeds autoresearch)."""
    target = proj_id or active_project_id()
    if not target:
        console.print(
            "[yellow]No active project.[/yellow] "
            "Run [cyan]lattice project switch <name>[/cyan] first."
        )
        sys.exit(1)

    registry = load_registry()
    proj = find_project(registry, target)
    if not proj:
        console.print(f"[red]Project '{target}' not found.[/red]")
        sys.exit(1)

    bridge_script = LATTICE_ROOT / "meta" / "harness" / "bootstrap" / "bridge-to-proposals.py"
    if not bridge_script.exists():
        console.print(f"[red]bridge-to-proposals.py not found at {bridge_script}[/red]")
        sys.exit(1)

    cmd = ["uv", "run", str(bridge_script)]
    if dry:
        cmd.append("--dry")

    console.print(
        f"[bold]Syncing bridge-briefs[/bold] for [cyan]{proj['id']}[/cyan]"
        + (" [dim](dry)[/dim]" if dry else "")
    )
    console.print(f"[dim]$ {' '.join(cmd)}[/dim]\n")

    env_extra = {"LATTICE_PROJECT_ID": proj["id"]}
    import os
    env = {**os.environ, **env_extra}

    result = subprocess.run(cmd, env=env)
    sys.exit(result.returncode)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    cli()
