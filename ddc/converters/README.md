# DDC Linux Converters — Fallback Only

DDC ships native Linux CLI converters: `ddc-ifcconverter`, `ddc-dwgconverter`. They produce the same kind of JSON-ish output IfcOpenShell does, but with different quirks and a different bug surface.

**LATTICE uses IfcOpenShell + ezdxf on Mac as the primary path.** These DDC binaries are a fallback for edge-case IFC files IfcOpenShell can't parse, or binary DWG from collaborators that needs a different decoder.

## Never used

| Binary | Why never |
|---|---|
| `ddc-rvtconverter` | LATTICE does not accept Revit input. Collaborators export IFC4.3 first. |
| `ddc-dgnconverter` | LATTICE does not accept DGN / MicroStation input. |

The corresponding repo is [`cad2data-Revit-IFC-DWG-DGN`](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN). LATTICE pulls only `ddc-ifcconverter` and `ddc-dwgconverter` from there — see [`INSTALL.md`](INSTALL.md).

## Deployment

- OrbStack Ubuntu VM, arm64 (Apple Silicon native)
- Mac filesystem mounted at `/Users` inside the VM (OrbStack default)
- SSH: `ssh ubuntu@orb`
- Wine: never. The converters have native Linux .deb packages.

## When LATTICE would call these

The IfcOpenShell ingest path emits a warning row in `lattice/bridge/health/schema_drift_events` when it gives up on a file. An operator (or an agent) can then explicitly request a DDC fallback parse:

```bash
ssh ubuntu@orb 'ddc-ifcconverter /Users/.../bad-file.ifc /Users/.../bad-file.json'
```

Then the resulting JSON is re-ingested via the regular VW sidecar path. We expect this to be needed for <1 % of files.

Tracked in [`../../meta/FEATURE_BACKLOG.md`](../../meta/FEATURE_BACKLOG.md) § DDC INTEGRATION (not currently a priority — only stand it up when a real IfcOpenShell failure shows up in `schema_drift_events`).
