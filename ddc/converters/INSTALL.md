# DDC Converters — Install (only when needed)

You don't need this set up until an IfcOpenShell ingest fails and writes a row to `lattice/bridge/health/schema_drift_events`. Below is the bring-up procedure.

## 1. OrbStack Ubuntu VM

```bash
brew install orbstack
orb create ubuntu lattice-ddc          # arm64 by default on Apple Silicon
ssh ubuntu@orb                          # auto-keyed by OrbStack
```

The Mac filesystem is mounted at `/Users` inside the VM, so any path on your Mac is reachable as `/Users/<rest>` from the VM.

## 2. Download the converters

Fetch the latest `.deb` releases for **ifcconverter** and **dwgconverter** from https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN/releases.

```bash
# inside the VM
cd /tmp
curl -L -o ddc-ifcconverter.deb '<release URL for ifcconverter>'
curl -L -o ddc-dwgconverter.deb '<release URL for dwgconverter>'
sudo dpkg -i ddc-ifcconverter.deb ddc-dwgconverter.deb
sudo apt-get -f install -y    # pull any missing system deps
```

**Do not install** `ddc-rvtconverter.deb` or `ddc-dgnconverter.deb` — LATTICE does not accept Revit or DGN input.

## 3. Verify

```bash
ddc-ifcconverter --version
ddc-dwgconverter --version
```

## 4. Use from the Mac

```bash
# Example: fallback parse for an IFC IfcOpenShell choked on
ssh ubuntu@orb 'ddc-ifcconverter /Users/me/projects/x.ifc /Users/me/projects/x.ddc.json'
```

The resulting JSON has the same shape DDC's notebooks expect. From the LATTICE side, re-feed it through the VW sidecar path — same upsert, just a different parser source.

## Why not just Docker?

We could. OrbStack happens to also be the host for the CWICR Qdrant container (see `../cwicr/INSTALL.md`), so we get a single VM hosting both DDC pieces for free. If you don't need CWICR, you can replace this VM with a single `docker run --rm` instead.
