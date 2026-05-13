<!-- spec-verified: disler/agentic-drop-zones 16a347b 2026-05-12 -->
# Drop Zones

Drop zones turn file events into configured harness jobs.

## Rule

A drop zone is a YAML-configured intake surface:

- watched directory
- file pattern
- event type
- prompt template
- execution surface
- model
- optional MCP/tool config
- output and archive policy

The dropped file is input. The job must emit an artifact and evidence.

## LATTICE use

Drop zones are useful for:

- morning debrief audio
- docs or research intake
- generated training data
- image or media processing
- finance/category extraction
- one-off operator inputs that should become structured work

## Safety

Drop zones must not run with broad local authority by default. Route them through:

- Pi L4/L5 bash policy
- sandbox when file contents are untrusted
- model-fit benchmark if the task will repeat
- explicit archive/output directories

## Config principle

The persistent asset is the drop-zone config. The processing run is disposable unless it emits a deliberate artifact.
